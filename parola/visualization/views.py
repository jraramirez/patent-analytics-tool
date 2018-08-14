from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from django import forms

from data_sets.models import Patents
from data_sets.models import Datasets

import numpy as np
import pandas as pd
import os
import math
import ast
import json
from itertools import combinations
from os import listdir
from os.path import isfile, join
import networkx as nx
from community import best_partition
import urllib
import random
from collections import defaultdict

from sklearn.pipeline import Pipeline
from sklearn.pipeline import FeatureUnion
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.manifold import TSNE

import PatentProcessing as pp
import CategoriesCleaner as catc
import ClaimsCleaner as cc
import Visualization as v
import ItemSelector as ise
import DBQueries as dbq
import ChartInputManager as cim

pd.options.display.max_colwidth = 1000

# View for dataset statistics
def dataset_statistics(request, data_set, classification):
    nPPA = None
    CPCLegend = None
    selectedClassificationDisplay = ''
    selectedClass = ''
    minCount = 1
    maxCount = 15
    minCount2 = 1
    maxCount2 = 15
    minCount3 = 1
    maxCount3 = 15
    targetN = 12
    previousNYears = 20
    yearData = None
    areaData = None
    categoryData = None
    categoryPercentData = None
    categoryYearData = None
    assigneeData = None
    assigneeYearData = None
    categoryAssigneeData = None
    sunBurstData = None
    smallMultipleData = None

    dataSetNames = []
    datasets = Datasets.objects.all()
    for dataset in datasets:
        dataSetNames.append(dataset.name)
    dataSetNames.insert(0, 'index')
    
    classificationNames = dbq.getClassificationList()
    classificationNames.insert(0, 'index')

    if(data_set != 'index'):
        if(request.method == "POST"): 
            targetN = int(request.POST.get('target-n'))
            previousNYears = int(request.POST.get('target-n-years'))

        # df = dbq.getDataSetPatents(data_set)
        df = pd.DataFrame()
        df = dbq.getDataSetPatentYears(data_set, df)
        df = dbq.getDataSetPatentAssignees(data_set, df)
        assigneeSectorsIndustries = dbq.getAssigneeSectorIndustry()
        df['Current Assignees'] = df['Clean Assignees'].tolist()
        df = dbq.getDataSetPatentTypes(data_set, df)
        df = dbq.getDataSetPatentColumn(data_set, df, classification)
        years = df['Years']
        maxYear = max(years)
        minYear = maxYear - previousNYears + 1
        df = df[df.Years >= minYear]
        df = df[df['Current Assignees'] != '']
        years = df['Years']
        CAs = df['Current Assignees']        
        types = df['Types']
        selectedClass = df[classification].tolist()
        nPPA = len(df.index)
        topNAssignees = pd.crosstab(df['Current Assignees'], [df['Types']], margins=True).sort_values(by=['All'], ascending=False).reset_index().drop(['All'], axis=1).drop([0]).head(targetN)['Current Assignees'].tolist()

        dfCopy = df.copy()
        smallMultipleData = dfCopy.groupby(['Years', 'Current Assignees']).size().unstack(fill_value=0).stack().reset_index(name='nPPA')    
        smallMultipleData = smallMultipleData[smallMultipleData['Current Assignees'].isin(topNAssignees)]
        smallMultipleData = smallMultipleData.rename(index=str, columns={
            'Current Assignees': "CurrentAssignees"
        })
        smallMultipleData =  smallMultipleData.to_json(orient="index")

        dfCopy = df.copy()
        dataSetSource = Datasets.objects.filter(name=data_set)[0].source
        dfCopy = pp.assignAssigneeSectorIndustry(dfCopy, assigneeSectorsIndustries, dataSetSource)
        dfCopy = dfCopy.dropna(subset=['Sectors'])
        dfCopy = dfCopy.dropna(subset=['Industries'])
        dfCopy = dfCopy[['Sectors', 'Industries', 'ids']]
        sectorsIndustriesCounts = dfCopy.groupby(['Sectors', 'Industries']).size().reset_index(name='nPPA')

        d = dict()
        d = {"name":"flare", "children": []}
        for line in sectorsIndustriesCounts.values:
            the_parent = line[0]
            the_child = line[1]
            child_size = line[2]
            keys_list = []
            for item in d['children']:
                keys_list.append(item['name'])
            if not the_parent in keys_list:
                d['children'].append({"name":the_parent, "children":[{"name":the_child, "size":child_size}]})
            else:
                d['children'][keys_list.index(the_parent)]['children'].append({"name":the_child, "size":child_size})
        sunBurstData = d

        allYears = []
        allCAs = []
        allClass = []
        allTypes = []
        for cList, year, CA, patentType in zip(selectedClass, years, CAs, types):
            if(cList == cList and cList != None):
                for c in cList:
                    if(c != 'nan' and c !='' and c !='NAN'):
                        allClass.append(c)
                        allYears.append(year)
                        allCAs.append(CA)
                        allTypes.append(patentType)
        expandedDF = pd.DataFrame()
        expandedDF['Categories'] = allClass
        expandedDF['Years'] = allYears
        expandedDF['Current Assignees'] = allCAs
        expandedDF['Types'] = allTypes

        # Number of PPA per year for line graph
        yearData = cim.getGroupByInput(df, 'Years', 'nPPA')

        # Number of PPA per year for area chart
        # areaData = cim.getGroupByInput2(df, 'Years', 'Types', 'nPPA')
        counts = df.groupby(['Years', 'Types']).size().unstack(fill_value=0).stack().reset_index(name='nPPA')
        areaData =  counts.to_json(orient="index")

        # top 10 category counts
        categoryData = cim.getCrossTabInput(expandedDF, 'Categories', 'Types', targetN)
        categoryCounts = pd.crosstab(expandedDF['Categories'], [expandedDF['Types']], margins=True).sort_values('All', ascending=False).reset_index()
        categoryCounts = categoryCounts.drop(['All'], axis=1).drop([0]).head(targetN)
        if(classification == 'cpc'):
            CPCLegend = zip(categoryCounts['Categories'].tolist(), pp.getCPCDescription(categoryCounts['Categories'].tolist()))

        categoryPercentages = expandedDF.groupby(['Categories']).size().reset_index(name='percent')
        total = categoryPercentages['percent'].sum()
        categoryPercentages['percent'] = categoryPercentages['percent']/total*100
        categoryPercentages['percent'] = categoryPercentages['percent'].round(decimals=1)
        categoryPercentages = categoryPercentages.head(targetN)
        categoryPercentData = categoryPercentages.to_json(orient="index")

        # top 10 categories and their PPA counts per year
        grouped = expandedDF.groupby(['Categories']).size().reset_index(name='Number of P/PA')
        topNCategories = grouped.nlargest(targetN, 'Number of P/PA')['Categories'].tolist()
        expandedDF = expandedDF[expandedDF['Categories'].isin(topNCategories)]
        expandedDF = expandedDF.sort_values(['Years','Categories'],ascending=False)
        hm = expandedDF.groupby(['Years', 'Categories']).size().reset_index(name='nPPA')
        hm = hm.sort_values(['Years'], ascending=True)
        hm = hm.sort_values(['nPPA'], ascending=False)
        hm = hm[hm.Years != 0]
        maxCount = hm['nPPA'].max()
        minCount = hm['nPPA'].min()
        categoryYearData = hm.to_json(orient="index")

        # top assignees
        assigneeData = cim.getCrossTabInput(df, 'Current Assignees', 'Types', targetN)
        # grouped = df.groupby(['Current Assignees']).size().reset_index(name='Number of P/PA')
        # topNAssignees = grouped.nlargest(targetN, 'Number of P/PA')['Current Assignees'].tolist()

        # top 10 assignees and their PPA counts per year
        dfCopy = df.copy()
        dfCopy = dfCopy[dfCopy['Current Assignees'].isin(topNAssignees)]
        hm = dfCopy.groupby(['Years', 'Current Assignees']).size().reset_index(name='nPPA')
        hm = hm[hm.Years != 0]
        maxCount2 = hm['nPPA'].max()
        minCount2 = hm['nPPA'].min()
        hm = hm.rename(index=str, columns={
            'Current Assignees': "Categories"
        })
        tempDF = pd.DataFrame(columns=['Years', 'Categories', 'nPPA'])
        tempDF['Categories'] = topNAssignees
        tempDF['Years'] = 9999
        tempDF['nPPA'] = 0
        tempDF = tempDF.append(hm).reset_index()
        assigneeYearData = tempDF.to_json(orient="index")

        # top 10 categories and top 10 assignees
        expandedDF = expandedDF[expandedDF['Current Assignees'].isin(topNAssignees)]
        hm = expandedDF.groupby(['Categories', 'Current Assignees']).size().reset_index(name='nPPA')
        # hm = hm.sort_values(['CurrentAssignees'], ascending=True)
        hm = hm.sort_values(['nPPA'], ascending=False)
        hm = hm.rename(index=str, columns={
            'Current Assignees': "CurrentAssignees"
        })
        tempDF = pd.DataFrame(columns=['Categories', 'CurrentAssignees', 'nPPA'])
        tempDF['CurrentAssignees'] = topNAssignees
        tempDF['Categories'] = "9999"
        tempDF['nPPA'] = 0
        tempDF = tempDF.append(hm).reset_index()
        categoryAssigneeData = tempDF.to_json(orient="index")
        maxCount3 = hm['nPPA'].max()
        minCount3 = hm['nPPA'].min()

    templateHTML = 'visualization/dataset_statistics.html'
    mainHTML = render_to_string(
        templateHTML, {
        'data_set': data_set,
        'classification': classification,
        'selectedClassificationDisplay': selectedClassificationDisplay,
        'dataSetNames': dataSetNames,
        'classificationNames': classificationNames,
        'minCount': minCount,
        'maxCount': maxCount,
        'minCount2': minCount2,
        'maxCount2': maxCount2,
        'minCount3': minCount3,
        'maxCount3': maxCount3,
        'nPPA': nPPA,
        'CPCLegend': CPCLegend,
        'targetN': targetN,
        'previousNYears': previousNYears,
        'yearData': yearData,
        'areaData': areaData,
        'categoryData': categoryData,
        'categoryPercentData': categoryPercentData,
        'categoryYearData': categoryYearData,
        'assigneeData': assigneeData,
        'assigneeYearData': assigneeYearData,
        'categoryAssigneeData': categoryAssigneeData,
        'sunBurstData': sunBurstData,
        'smallMultipleData': smallMultipleData
    })
    return mainHTML

# View for category statistics
def category_statistics(request, data_set, classification, category):
    errors = []
    warnings = []
    form = None
    valid = False
    hasDataSet = False
    hasCategory = False
    nPPA = None
    categoryList = None
    selectedCategory = str(category).replace('_','/')
    selectedCPCDescription = None
    selectedClass = ''
    selectedClassificationDisplay = ''
    maxYear = None
    assigneeData = None
    yearData = None
    targetAssigneeColumnName = "CA"
    targetYearColumnName = "YEAR"
    targetCategoryColumnName = "CATEGORY"
    previousNYears = 20
    
    # Data set selection view
    dataSetNames = []
    datasets = Datasets.objects.all()
    for dataset in datasets:
        dataSetNames.append(dataset.name)
    dataSetNames.insert(0, 'index')

    classificationNames = dbq.getClassificationList()
    classificationNames.insert(0, 'index')

    # Category selection view
    if(not data_set == 'index' and not classification == 'index' and selectedCategory == 'index'):
        df = pd.DataFrame()
        df = dbq.getDataSetPatentColumn(data_set, df, classification)
        selectedClass = df[classification].tolist()
        nPPA = len(df.index)
        allClass = []
        for cList in selectedClass:
            if(cList and cList == cList):
                for c in cList:
                    if(c and c == c and c != 'nan' and c !='NAN'):
                        allClass.append(c.lstrip().rstrip())
        categoryList = sorted(list(set(allClass)))
        categoryList.insert(0, 'index')
        hasDataSet = True

    # Graph preparations
    elif(not data_set == 'index' and not selectedCategory == 'index'):
        if(request.method == "POST"): 
            previousNYears = int(request.POST.get('target-n-years'))
        df = pd.DataFrame()
        df = dbq.getDataSetPatentYears(data_set, df)
        nPPA = len(df.index)
        df = dbq.getDataSetPatentAssignees(data_set, df)
        df['Current Assignees'] = df['Clean Assignees'].tolist()
        df = dbq.getDataSetPatentTypes(data_set, df)
        df = dbq.getDataSetPatentColumn(data_set, df, classification)
        selectedClass = df[classification].tolist()
        
        years = df['Years']   
        maxYear = max(years)
        minYear = maxYear - previousNYears + 1
        df = df[df.Years >= minYear]
        years = df['Years']   
        CAs = df['Current Assignees']        
        types = df['Types']
        allClass = []
        allYears = []
        allCAs = []
        allTypes = []
        for year, CA, cList, patentType in zip(years, CAs, selectedClass, types):
            if(cList == cList and cList != None):
                for c in cList:
                    if(c and c == c and c != 'nan'):
                        allClass.append(c.lstrip().rstrip())
                        allYears.append(year)
                        allCAs.append(CA)
                        allTypes.append(patentType)
        categoryList = sorted(list(set(allClass)))
        expandedDF = pd.DataFrame()
        expandedDF[targetCategoryColumnName] = allClass
        expandedDF['Years'] = allYears
        expandedDF[targetAssigneeColumnName] = allCAs
        expandedDF['Types'] = allTypes
        expandedDF.drop(expandedDF[expandedDF[targetCategoryColumnName] != selectedCategory.lstrip().rstrip()].index, inplace=True)
        nPPA = len(expandedDF.index)

        # Year Bar Graph Data
        yearData = pd.crosstab(expandedDF['Years'], [expandedDF['Types']]).reset_index()
        yearData = yearData.head(10)
        yearData = yearData.rename(index=str, columns={
            'Years': "Categories"
        })
        yearData = yearData.to_json(orient="index")
        # yearData = cim.getCrossTabInput(expandedDF, 'Years', 'Types', 10)

        # Assignee Bar Graph Data
        assigneeData = cim.getCrossTabInput(expandedDF, targetAssigneeColumnName, 'Types', 10)

        # Bar Graph 2 Data
        # expandedDFCopy = expandedDF.copy()
        # maxYear = int(sizesDF.iloc[sizesDF['Count'].argmax()]['Year'])
        # expandedDFCopy.drop(expandedDFCopy[expandedDFCopy[targetYearColumnName] != maxYear].index, inplace=True)
        # assigneeCounts = pd.crosstab(expandedDFCopy[targetAssigneeColumnName], [expandedDFCopy['Types']], margins=True).sort_values('All', ascending=False).reset_index()
        # assigneeCounts = assigneeCounts.drop(['All'], axis=1).drop([0]).head(10)        
        # assigneeCounts.to_csv(outFolderName + outBarGraphFileName2 + barFileType, sep='\t', index=False)

        hasDataSet = True
        hasCategory = True
        valid = True

    templateHTML = 'visualization/category_statistics.html'
    mainHTML = render_to_string(
        templateHTML, {
        'form': form,
        'hasDataSet': hasDataSet,
        'hasCategory': hasCategory,
        'classification': classification,
        'selectedClassificationDisplay': selectedClassificationDisplay,
        'valid': valid,
        'errors': errors,
        'warnings': warnings,
        'nPPA': nPPA,
        'dataSetNames': dataSetNames,
        'classificationNames': classificationNames,
        'categoryList': categoryList,
        'data_set': data_set,
        'category': category,
        'selectedCategory': selectedCategory,
        'selectedCPCDescription': selectedCPCDescription,
        'maxYear': maxYear,
        'yearData': yearData,
        'assigneeData': assigneeData,
        'previousNYears': previousNYears,
    })
    return mainHTML
    
# View for assignee statistics
def assignee_statistics(request, data_set, classification, assignee):
    errors = []
    warnings = []
    form = None
    valid = False
    hasDataSet = False
    hasAssignee = False
    nPPA = None
    CPCLegend = None
    assigneeList = None
    selectedClass = ''
    selectedClassificationDisplay = ''
    maxYear = None
    categoryData = None
    yearData = None
    previousNYears = 20
    
    targetAssigneeColumnName = "CA"
    targetYearColumnName = "YEAR"
    targetCategoryColumnName = "Categories"
    
    # Data set selection view
    dataSetNames = []
    datasets = Datasets.objects.all()
    for dataset in datasets:
        dataSetNames.append(dataset.name)
    dataSetNames.insert(0, 'index')

    classificationNames = dbq.getClassificationList()
    classificationNames.insert(0, 'index')

    # Category selection view
    if(not data_set == 'index' and assignee == 'index'):
        # df = dbq.getDataSetPatents(data_set)
        df = pd.DataFrame()
        df = dbq.getDataSetPatentAssignees(data_set, df)
        df['Current Assignees'] = df['Clean Assignees'].tolist()
        CAs = df['Current Assignees']
        assigneeList = sorted(list(set(CAs.tolist())))
        assigneeList.insert(0, 'index')
        hasDataSet = True

    # Graph preparations
    elif(not data_set == 'index' and not assignee == 'index'):
        if(request.method == "POST"): 
            previousNYears = int(request.POST.get('target-n-years'))
        # df = dbq.getDataSetPatents(data_set)
        df = pd.DataFrame()
        df = dbq.getDataSetPatentYears(data_set, df)
        df = dbq.getDataSetPatentTypes(data_set, df)
        df = dbq.getDataSetPatentAssignees(data_set, df)
        assigneeList = sorted(list(set(df['Current Assignees'].tolist())))
        df['Current Assignees'] = df['Clean Assignees'].tolist()
        df = dbq.getDataSetPatentColumn(data_set, df, classification)
        df.drop(df[df['Current Assignees'] != assignee].index, inplace=True)
        years = df['Years']   
        maxYear = max(years)
        minYear = maxYear - previousNYears + 1
        df = df[df.Years >= minYear]
        years = df['Years']   
        nPPA = len(df.index)
        selectedClass = df[classification].tolist()
        CAs = df['Current Assignees']        
        types = df['Types']
        allClass = []
        allYears = []
        allCAs = []
        allTypes = []
        for year, CA, cList, patentType in zip(years, CAs, selectedClass, types):
            if(cList == cList and cList != None):
                # for c in ast.literal_eval(cList):
                for c in cList:
                    if(c and c == c and c != 'nan' and c !='NAN'):
                        allClass.append(c.lstrip().rstrip())
                        allYears.append(int(year))
                        allCAs.append(str(CA).lower().lstrip().rstrip())
                        allTypes.append(patentType)
        expandedDF = pd.DataFrame()
        expandedDF[targetCategoryColumnName] = allClass
        expandedDF[targetYearColumnName] = allYears
        expandedDF[targetAssigneeColumnName] = allCAs
        expandedDF['Types'] = allTypes

        # Line Graph Data
        expandedDFCopy = expandedDF.copy()
        grouped = df.groupby(['Years'])
        groupSizes = df.groupby(['Years']).size()
        years = []
        sizes = []
        for g, s in zip(grouped, groupSizes):
            years.append(int(g[0]))
            sizes.append(s)
        sizesDF = pd.DataFrame()
        sizesDF['Year'] = years
        sizesDF['Count'] = sizes
        maxYear = int(sizesDF.iloc[sizesDF['Count'].argmax()]['Year'])

        # Bar Graph 1 Data
        uniqueCategories = []
        expandedDFCopy = expandedDF.copy()
        assigneeCounts = pd.crosstab(expandedDFCopy[targetCategoryColumnName], [expandedDFCopy['Types']], margins=True).sort_values('All', ascending=False).reset_index()
        assigneeCounts = assigneeCounts.drop(['All'], axis=1).drop([0]).head(10)        
        uniqueCategories = assigneeCounts[targetCategoryColumnName].tolist()
        categoryData = assigneeCounts.to_json(orient="index")
        
        # Bar Graph 2 Data
        # Year Bar Graph Data
        yearData = pd.crosstab(df['Years'], [df['Types']]).reset_index()
        yearData = yearData.head(10)
        yearData = yearData.rename(index=str, columns={
            'Years': "Categories"
        })
        yearData = yearData.to_json(orient="index")

        if(classification == 'cpc'):
            CPCLegend = zip(uniqueCategories, pp.getCPCDescription(uniqueCategories))

        hasDataSet = True
        hasAssignee = True
        valid = True

    templateHTML = 'visualization/assignee_statistics.html'
    mainHTML = render_to_string(
        templateHTML, {
        'form': form,
        'hasDataSet': hasDataSet,
        'hasAssignee': hasAssignee,
        'classification': classification,
        'selectedClassificationDisplay': selectedClassificationDisplay,
        'valid': valid,
        'errors': errors,
        'warnings': warnings,
        'nPPA': nPPA,
        'CPCLegend': CPCLegend,
        'dataSetNames': dataSetNames,
        'classificationNames': classificationNames,
        'assigneeList': assigneeList,
        'data_set': data_set,
        'assignee': assignee,
        'maxYear': maxYear,
        'categoryData': categoryData,
        'yearData': yearData,
        'previousNYears': previousNYears,
    })
    return mainHTML

# View for cluster map
def cluster_map(request, data_set, classification1, classification2):
    errors = []
    warnings = []
    form = None
    valid = False
    hasDataSet = False
    clusterData = None
    dataSetNames = []
    selectedClassificationDisplay = ''
    selectedClass = ''

    minNodeSize = 99999
    maxNodeSize = 0
    minEdgeWeight = 99999
    maxEdgeWeight = 0
    minNodeSizeWithLabel = 20
    maxNNodes = 20
    topN = 10
    
    targetCPCColumnName = 'CPCs'
    outFileName = 'clusterMapInput'
    outFolderName = '../templates/visualization/'
    fileType = '.json'
    
    dataSetNames = []
    datasets = Datasets.objects.all()
    for dataset in datasets:
        dataSetNames.append(dataset.name)
    dataSetNames.insert(0, 'index')

    classificationNames = dbq.getClassificationList()
    classificationNames.insert(0, 'index')

    # Model setup view
    if(not (data_set == 'index' or classification1 == 'index' or classification2 == 'index' or classification1 == classification2)):
        # df = dbq.getDataSetPatents(data_set)
        # if(len(df.index)>1000):
        #     df = df.sample(n=500, replace=False, random_state=17)]
        df = pd.DataFrame()
        df = dbq.getDataSetPatentColumn(data_set, df, classification1)
        selectedClass1 = df[classification1].tolist()
        df = dbq.getDataSetPatentColumn(data_set, df, classification2)
        selectedClass2 = df[classification2].tolist()

        allCategories = []
        uniqueCategories1 = []
        uniqueCategories2 = []
        combinedCategories = []

        allClass1 = []
        allClass2 = []
        for cList1 in selectedClass1:
            if(cList1 == cList1 and cList1 != None):
                for c in cList1:
                    if(c != 'nan' and c !='' and c !='NAN' and c != 'Nan'):
                        allClass1.append(c)
        for cList2 in selectedClass2:
            if(cList2 == cList2 and cList2 != None):
                for c in cList2:
                    if(c != 'nan' and c !='' and c !='NAN' and c != 'Nan'):
                        allClass2.append(c)
        expandedDF1 = pd.DataFrame()
        expandedDF1[classification1] = allClass1
        expandedDF2 = pd.DataFrame()
        expandedDF2[classification2] = allClass2

        grouped = expandedDF1.groupby([classification1]).size().reset_index(name='nPPA')
        topNClassification1 = grouped.nlargest(topN, 'nPPA')[classification1].tolist()
        grouped = expandedDF2.groupby([classification2]).size().reset_index(name='nPPA')
        topNClassification2 = grouped.nlargest(topN, 'nPPA')[classification2].tolist()

        # for c2, c3, c4 in zip(categories2, categories3, categories4):
        for c1, c2 in zip(selectedClass1, selectedClass2):
            if(not c1):
                c1 = []
            if(not c2):
                c2 = []
            c1 = [c for c in c1 if c in topNClassification1]
            c2 = [c for c in c2 if c in topNClassification2]
            allCategories = allCategories + c1 + c2
            combinedCategories.append(c1 + c2)
            uniqueCategories1 = uniqueCategories1 + c1
            uniqueCategories2 = uniqueCategories2 + c2
        uniqueCategories1 = list(set(uniqueCategories1))
        uniqueCategories2 = list(set(uniqueCategories2))
        # expanded = pd.DataFrame()
        # expanded['Categories'] = allCategories
        # categorySizes = expanded.groupby(['Categories']).size().reset_index(name='nPPA')
        # categoryList = categorySizes['Categories'].tolist()
        # categorySizesList = categorySizes['nPPA'].tolist()

        selectedClass = combinedCategories
        # selectedClass = categoryByKeywords

        # wordList = []
        # f = open('../out/words.txt', 'r')
        # for line in f:
        #     wordList.append(line.rstrip())
        # f.close()
        # titleWords = pp.normalizeCorpus(df['Titles'].tolist(), wordList)

        allClass = []
        for c in selectedClass:
            if(c):
                allClass = allClass + list(filter(lambda a: a != '', c))
        expanded = pd.DataFrame()
        expanded['Class'] = allClass
        classSizes = expanded.groupby(['Class']).size().reset_index(name='nPPA')
        classList = classSizes['Class'].tolist()
        classSizesList = classSizes['nPPA'].tolist()

        grouped = expanded.groupby(['Class']).size().reset_index(name='Number of P/PA')
        topNClass = grouped.nlargest(10, 'Number of P/PA')['Class'].tolist()

        # Cleaning of CPC
        relationships = selectedClass
        relationshipsEval = []

        if(maxNNodes > 0):
            topNNodes = v.getTopNNodes(relationships, maxNNodes)
            for rList in relationships:
                tempRList = []
                for node in list(filter(lambda a: a != '', rList)):
                    if(node in topNNodes):
                        tempRList.append(node)
                relationshipsEval.append(tempRList)
        else:
            for rList in relationships:
                relationshipsEval.append(list(filter(lambda a: a != '', rList)))
        source = []
        target = []
        weight = []
        for r in relationshipsEval:
            pairs = combinations(r, 2)
            for p in pairs:
                if((p[0] in uniqueCategories1 and p[1] in uniqueCategories1)
                    or (p[0] in uniqueCategories2 and p[1] in uniqueCategories2)                 
                    ):
                    continue
                else:
                    source.append(p[0])
                    target.append(p[1])
                    weight.append(1)
                # source.append(p[0])
                # target.append(p[1])
                # weight.append(1)

        newDF = pd.DataFrame()
        newDF['source'] = source
        newDF['target'] = target
        newDF['weight'] = weight

        graphDF = newDF.groupby(['source', 'target']).sum().reset_index()
        maxEdgeWeight = graphDF['weight'].max()
        minEdgeWeight = graphDF['weight'].min()
        # graphDF.to_excel(outFolderName + 'edgelist.xlsx')
        G = nx.from_pandas_edgelist(graphDF, 'source', 'target', 'weight')
        G2 = nx.convert_node_labels_to_integers(G, label_attribute='name')

        # Determine node groups using Louvain modularity
        # communities = best_partition(G2, weight='size')
        d = nx.readwrite.json_graph.node_link_data(G2, {'name': 'index'})
        nodeNames = []
        nodeCommunities = []
        nodeSizes = []
        nodeTop10 = []
        for node in d['nodes']:
            name = node['name']
            # size = G2.degree[list(G.nodes()).index(node['name'])]
            size = classSizesList[classList.index(node['name'])]
            community = 2
            if(name in uniqueCategories1):
                community = 0
            if(name in uniqueCategories2):
                community = 1
            # community = communities[list(G.nodes()).index(node['name'])]
            node['size'] = size
            node['group'] = community
            nodeNames.append(name)
            nodeSizes.append(size)
            nodeCommunities.append(community)
            name = node['name']
            if(node['size'] < minNodeSize):
                minNodeSize = node['size']
            if(node['size'] > maxNodeSize):
                maxNodeSize = node['size']
        # minNodeSizeWithLabel = 0.2 * maxNodeSize
        # for node in d['nodes']:
        #     if(node['size'] < minNodeSizeWithLabel):
        #         node['name'] = None
        for node in d['nodes']:
            if(not node['name'] in topNClass):
                node['fontSize'] = 8
                node['opacity'] = 0.5
            else:
                node['fontSize'] = node['size']
                node['opacity'] = 1
            
        nodesDF = pd.DataFrame()
        nodesDF['CPC'] = nodeNames
        nodesDF['Size'] = nodeSizes
        nodesDF['Community'] = nodeCommunities

        del d["directed"]
        del d["multigraph"]
        del d["graph"]
        clusterData = d
        hasDataSet = True
        valid = True

    templateHTML = 'visualization/cluster_map.html'
    mainHTML = render_to_string(
        templateHTML, {
            'form': form,
            'valid': valid,
            'errors': errors,
            'warnings': warnings,
            'data_set': data_set,
            'classification1': classification1,
            'classification2': classification2,
            'classificationNames': classificationNames,
            'selectedClassificationDisplay': selectedClassificationDisplay,
            'hasDataSet': hasDataSet,
            'dataSetNames': dataSetNames,
            'minNodeSize': minNodeSize,
            'maxNodeSize': maxNodeSize,
            'maxEdgeWeight': maxEdgeWeight,
            'minEdgeWeight': minEdgeWeight,
            'clusterData': clusterData, 
    })
    return mainHTML

# View for cluster map
def word_cluster_map(request, data_set, column):
    errors = []
    warnings = []
    form = None
    valid = False
    hasDataSet = False
    clusterData = None
    dataSetNames = []
    selectedClassificationDisplay = ''

    minNodeSize = 99999
    maxNodeSize = 0
    minEdgeWeight = 99999
    maxEdgeWeight = 0
    minNodeSizeWithLabel = 20
    maxNNodes = 30
    topN = 10
        
    dataSetNames = []
    datasets = Datasets.objects.all()
    for dataset in datasets:
        dataSetNames.append(dataset.name)
    dataSetNames.insert(0, 'index')

    columnNames = ['titles', 'abstracts', 'independent_claims']
    columnNames.insert(0, 'index')

    # Model setup view
    if(not (data_set == 'index' or column == 'index')):
        if(request.method == "POST"): 
            maxNNodes = int(request.POST.get('target-n-nodes'))
        # if(len(df.index)>1000):
        #     df = df.sample(n=500, replace=False, random_state=17)]
        df = pd.DataFrame()
        df = dbq.getDataSetPatentTACs(data_set, df)

        wordList = []
        f = open('../out/words.txt', 'r')
        for line in f:
            wordList.append(line.rstrip())
        f.close()
        columnWords = []
        if(column == 'titles'):
            columnWords = pp.normalizeCorpus(df['Titles'].tolist(), wordList)
        elif(column == 'abstracts'):
            columnWords = pp.normalizeCorpus(df['Abstracts'].tolist(), wordList)
        elif(column == 'independent_claims'):
            columnWords = pp.normalizeCorpus(df['Independent Claims'].tolist(), wordList)
        selectedColumn = columnWords

        uniqueWords = []
        combinedWords = []

        allWords = []
        for wordList in selectedColumn:
            if(wordList == wordList and wordList != None):
                for word in wordList:
                    if(word != 'nan' and word !='' and word !='NAN' and word != 'Nan'):
                        allWords.append(word)
        expandedDF = pd.DataFrame()
        expandedDF[column] = allWords
        uniqueWords = list(set(allWords))
        
        wordSizes = expandedDF.groupby([column]).size().reset_index(name='nPPA')
        topNWords = wordSizes.nlargest(topN, 'nPPA')[column].tolist()
        wordList = wordSizes[column].tolist()
        wordSizesList = wordSizes['nPPA'].tolist()

        # Cleaning of CPC
        relationships = selectedColumn
        relationshipsEval = []

        if(maxNNodes > 0):
            topNNodes = v.getTopNNodes(relationships, maxNNodes)
            for rList in relationships:
                tempRList = []
                for node in list(filter(lambda a: a != '', rList)):
                    if(node in topNNodes):
                        tempRList.append(node)
                relationshipsEval.append(tempRList)
        else:
            for rList in relationships:
                relationshipsEval.append(list(filter(lambda a: a != '', rList)))
        source = []
        target = []
        weight = []
        for r in relationshipsEval:
            pairs = combinations(r, 2)
            for p in pairs:
                source.append(p[0])
                target.append(p[1])
                weight.append(1)

        newDF = pd.DataFrame()
        newDF['source'] = source
        newDF['target'] = target
        newDF['weight'] = weight

        graphDF = newDF.groupby(['source', 'target']).sum().reset_index()
        maxEdgeWeight = graphDF['weight'].max()
        minEdgeWeight = graphDF['weight'].min()
        # graphDF.to_excel(outFolderName + 'edgelist.xlsx')
        G = nx.from_pandas_edgelist(graphDF, 'source', 'target', 'weight')
        G2 = nx.convert_node_labels_to_integers(G, label_attribute='name')

        # Determine node groups using Louvain modularity
        communities = best_partition(G2, weight='size')
        d = nx.readwrite.json_graph.node_link_data(G2, {'name': 'index'})
        nodeNames = []
        nodeCommunities = []
        nodeSizes = []
        nodeTop10 = []
        for node in d['nodes']:
            name = node['name']
            # size = G2.degree[list(G.nodes()).index(node['name'])]
            size = wordSizesList[wordList.index(node['name'])]
            community = communities[list(G.nodes()).index(node['name'])]
            node['size'] = size
            node['group'] = community
            nodeNames.append(name)
            nodeSizes.append(size)
            nodeCommunities.append(community)
            name = node['name']
            if(node['size'] < minNodeSize):
                minNodeSize = node['size']
            if(node['size'] > maxNodeSize):
                maxNodeSize = node['size']
        # minNodeSizeWithLabel = 0.2 * maxNodeSize
        # for node in d['nodes']:
        #     if(node['size'] < minNodeSizeWithLabel):
        #         node['name'] = None
        for node in d['nodes']:
            if(not node['name'] in topNWords):
                node['fontSize'] = 8
                node['opacity'] = 0.5
            else:
                node['fontSize'] = node['size']
                node['opacity'] = 1
            
        nodesDF = pd.DataFrame()
        nodesDF['CPC'] = nodeNames
        nodesDF['Size'] = nodeSizes
        nodesDF['Community'] = nodeCommunities

        del d["directed"]
        del d["multigraph"]
        del d["graph"]
        clusterData = d
        hasDataSet = True
        valid = True

    templateHTML = 'visualization/word_cluster_map.html'
    mainHTML = render_to_string(
        templateHTML, {
            'form': form,
            'valid': valid,
            'errors': errors,
            'warnings': warnings,
            'data_set': data_set,
            'column': column,
            'columnNames': columnNames,
            'hasDataSet': hasDataSet,
            'dataSetNames': dataSetNames,
            'minNodeSize': minNodeSize,
            'maxNodeSize': maxNodeSize,
            'maxEdgeWeight': maxEdgeWeight,
            'minEdgeWeight': minEdgeWeight,
            'clusterData': clusterData,
            'maxNNodes': maxNNodes
    })
    return mainHTML

# View for landscape map
def landscape_map(request, data_set):
    errors = []
    warnings = []
    form = None
    valid = False
    hasDataSet = False
    columnList = None
    dataSetNames = None
    topicsTableHTML = None
    stringUniqueAllTopics = None
    n_top_documents = 3
    documentsPerTopic = []
    selectedDataSet = data_set
    uniqueStringFeatureNames = None
    tsneData = None
    # colorList = ["#2D777F", "#173B40", "#2b9ca5", "#7cc9d2", "#5BEEFF", "#51D6E5", "#44B2BF", "#e5f2f9", "#E9EDDE", "#e2e2e2"]
    # colorList = ["#5BEEFF", "#d62728", "#2b9ca5", "#ff7f0e", "#756bb1", "#66aa00", "#1f77b4", "#bcbd22"]
    colorList = ["#ed7d2e", "#258296", "#6cc8db", "#194660", "#316e8c", "#2D777F", "#1f77b4", "#8a8a8a", "#756bb1", "#bcbd22"]

    outFolderName = '../templates/visualization/'
    fileType = '.xlsx'
    scatterFileName = 'landscapeMapInput'
    scatterFileType = '.tsv'
    targetTitlesColumnName = 'Titles'
    targetAbstractsColumnName = 'Abstracts'
    targetIndependentClaimsColumnName = 'Independent Claims'

    dataSetNames = []
    datasets = Datasets.objects.all()
    for dataset in datasets:
        dataSetNames.append(dataset.name)
    dataSetNames.insert(0, 'index')
    
    # Model setup view
    if(not selectedDataSet == 'index' and not request.method == "POST"):
        hasDataSet = True

    # Graph preparation
    elif(request.method == "POST"):
        n_top_words = 12
        df = pd.DataFrame()
        df = dbq.getDataSetPatentTACs(data_set, df)
        if(len(df.index)>1000):
            # df = df.sample(n=500, replace=False)
            df = df.sample(frac=0.1, replace=False)
        df = df.dropna(subset=[targetTitlesColumnName])
        df = df.dropna(subset=[targetAbstractsColumnName])
        df = df.dropna(subset=[targetIndependentClaimsColumnName])

        targetFeatures = request.POST.getlist('features')
        targetMethod = request.POST.get('method')
        targetNumberOfComponents = int(request.POST.get('target-n-components'))
        targetNGram1 = int(request.POST.get('target-n-gram-1'))
        targetNGram2 = int(request.POST.get('target-n-gram-2'))
        
        wordList = []
        f = open('../out/words.txt', 'r')
        for line in f:
            wordList.append(line.rstrip())
        f.close()

        featuresDF = pd.DataFrame()
        cleanTitles = cc.removePublicationNumbers(df[targetTitlesColumnName])
        # featuresDF[targetTitlesColumnName] = pp.normalizeCorpusAsStrings(cleanTitles, wordList)
        # featuresDF[targetAbstractsColumnName] = pp.normalizeCorpusAsStrings(df[targetAbstractsColumnName], wordList)
        # featuresDF[targetIndependentClaimsColumnName] = pp.normalizeCorpusAsStrings(df[targetIndependentClaimsColumnName], wordList)

        if('titles' in targetFeatures):        
            temp = cc.removePublicationNumbers(df[targetTitlesColumnName])
            temp = pp.normalizeCorpusAsStrings(temp, wordList)
            df[targetTitlesColumnName] = cc.remove2LetterWords(temp)
            featuresDF[targetTitlesColumnName] = df[targetTitlesColumnName]

        if('abstracts' in targetFeatures):        
            temp = cc.removePublicationNumbers(df[targetAbstractsColumnName])
            temp = pp.normalizeCorpusAsStrings(temp, wordList)
            df[targetAbstractsColumnName] = cc.remove2LetterWords(temp)
            featuresDF[targetAbstractsColumnName] = df[targetAbstractsColumnName]
        if('independentclaims' in targetFeatures):        
            temp = cc.removePublicationNumbers(df[targetIndependentClaimsColumnName])
            temp = pp.normalizeCorpusAsStrings(temp, wordList)
            temp = cc.remove2LetterWords(temp)
            df[targetIndependentClaimsColumnName] = cc.removeDigits(temp)
            featuresDF[targetIndependentClaimsColumnName] = df[targetIndependentClaimsColumnName]

        transformerList = []
        if('titles' in targetFeatures):    
            transformerList.append(
                ('titles', Pipeline([
                    ('selector', ise.ItemSelector(key=targetTitlesColumnName)),
                    ('vectorizer', TfidfVectorizer(stop_words='english', lowercase=True, ngram_range=(targetNGram1, targetNGram2))),
            ])))
        if('abstracts' in targetFeatures):
            transformerList.append(
                ('abstracts', Pipeline([
                    ('selector', ise.ItemSelector(key=targetAbstractsColumnName)),
                    ('vectorizer', TfidfVectorizer(stop_words='english', lowercase=True, ngram_range=(targetNGram1, targetNGram2))),
            ])))
        if('independentclaims' in targetFeatures):
            transformerList.append(
                ('independent claims', Pipeline([
                    ('selector', ise.ItemSelector(key=targetIndependentClaimsColumnName)),
                    ('vectorizer', TfidfVectorizer(stop_words='english', lowercase=True, ngram_range=(targetNGram1, targetNGram2))),
            ])))  

        # Model fitting
        pipeline = Pipeline([
            ('union', FeatureUnion(
                transformer_list=transformerList,
            )),

            ('clf', LatentDirichletAllocation(
                n_components=targetNumberOfComponents, 
                random_state=10, 
                doc_topic_prior = .1, 
                learning_method='online',
                learning_offset=50, 
                max_iter=random.randint(1, 6))),
            # ('clf', LatentDirichletAllocation(
            #     n_components=targetNumberOfComponents, 
            #     random_state=0, 
            #     learning_method='online', 
            #     learning_offset=50, 
            #     max_iter=5)),
            # ('clf', NMF(n_components=10, random_state=1,
            #       beta_loss='kullback-leibler', solver='mu', max_iter=1000, alpha=.1,
            #       l1_ratio=.5)),
        ])

        pipeline.fit(featuresDF)
        model = pipeline.named_steps['clf']
        wordToTopics = model.components_ / model.components_.sum(axis=1)[:, np.newaxis]
        topicToDocuments = pipeline.transform(featuresDF)
        words = []
        for transformer in pipeline.steps[0][1].transformer_list:
            words = words + transformer[1].named_steps['vectorizer'].get_feature_names()

        topicsDF = pd.DataFrame()
        allTopics = []
        stringAllTopics = []
        stringUniqueAllTopics = []
        # allImportances = []
        allDocuments = []
        documentsPerTopic = []
        for topic_idx, topic in enumerate(wordToTopics):
            featureNames = [words[i] for i in topic.argsort()[:-n_top_words - 1:-1]]
            stringFeatureNames = str(featureNames).replace("'", '').replace("[", '').replace("]", '')
            uniqueStringFeatureNames = list(set(stringFeatureNames.replace(",", '').split(' ')))
            stringAllTopics.append(stringFeatureNames)
            stringUniqueAllTopics.append(str(uniqueStringFeatureNames).replace("'", '').replace("[", '').replace("]", '').replace(",", ''))
            # featureImportances = [importance for importance in topic.argsort()[:n_top_words]]
            top_doc_indices = np.argsort( topicToDocuments[:,topic_idx] )[::-1][0:n_top_documents]
            tempDocumentsPerTopic = []
            for doc_index in top_doc_indices:
                allTopics.append(featureNames)
                # allImportances.append(featureImportances)
                tempDocumentsPerTopic.append(cleanTitles[doc_index])
                allDocuments.append(cleanTitles[doc_index])
            documentsPerTopic.append(tempDocumentsPerTopic)
        topicsDF['Topics'] = allTopics
        topicsTable = pd.DataFrame()
        topicsTable['Topics'] = stringUniqueAllTopics
        topicsTableHTML = topicsTable.to_html(index=False)
        stringUniqueAllTopics = zip(colorList, stringUniqueAllTopics)
        documentsPerTopic = zip(colorList, documentsPerTopic)
        # topicsDF['Importances'] = allImportances
        topicsDF['Documents'] = allDocuments
        # topicsDF.to_excel(outFolderName + 'LDA2' + fileType)
        
        topWords = []
        for topic_idx, topic in enumerate(wordToTopics):
            featureNames = [words[i] for i in topic.argsort()[:-n_top_words - 1:-1]]
            topWords.append(str(featureNames).replace('[', '').replace(']', '').replace("'", ''))

        mostProbableTopicsIndex = [0] * len(wordToTopics[0])
        mostProbableTopics = [0] * len(wordToTopics[0])
        for word_idx, topics in enumerate(np.transpose(wordToTopics)):
            mostProbableTopicsIndex[word_idx] = np.argmax(topics)
            mostProbableTopics[word_idx] = topWords[np.argmax(topics)]

        # tsne_model = TSNE(n_components=2, verbose=1, random_state=0, angle=.99, init='pca')
        # tsne_model = TSNE(n_components=2, verbose=1, random_state=0, angle=.99, init='pca', perplexity=30, early_exaggeration=5)
        tsne_model = TSNE(n_components=2, verbose=1, random_state=0)
        tsne_lda = tsne_model.fit_transform(np.transpose(wordToTopics))
        # tsne_lda = tsne_model.fit_transform(topicToDocuments)
        xCoords = tsne_lda[:, 0]
        yCoords = tsne_lda[:, 1]
        tsnseDF = pd.DataFrame()
        tsnseDF['x'] = xCoords
        tsnseDF['y'] = yCoords
        tsnseDF['n'] = mostProbableTopicsIndex
        tsnseDF['label'] = mostProbableTopics
        tsnseDF.to_csv(outFolderName + scatterFileName + scatterFileType, sep='\t', index=False)
        tsneData = tsnseDF.to_json(orient="index")
        
        hasDataSet = True
        valid = True

    templateHTML = 'visualization/landscape_map.html'
    mainHTML = render_to_string(
        templateHTML, {
        'form': form,
        'valid': valid,
        'hasDataSet': hasDataSet,
        'errors': errors,
        'warnings': warnings,
        'columnList': columnList,
        'data_set': data_set,
        'dataSetNames': dataSetNames,
        'selectedDataSet': selectedDataSet,
        'stringUniqueAllTopics': stringUniqueAllTopics,
        'documentsPerTopic': documentsPerTopic,
        'n_top_documents': n_top_documents,
        'topicsTableHTML': topicsTableHTML,
        'tsneData': tsneData,
    })
    return mainHTML