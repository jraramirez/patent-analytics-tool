from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from wsgiref.util import FileWrapper
from django import forms
from django.template.loader import render_to_string

from data_sets.models import Patents
from data_sets.models import Datasets
from data_sets.models import TrainingDatasets
from data_sets.models import TrainingPatents
from data_sets.models import CategorySet
from data_sets.models import CategorySetKeywords

import datetime
import numpy as np
import pandas as pd
import os
import math
import ast

import DBQueries as dbq
import PatentProcessing as pp
import CategoriesCleaner as catc
import ClaimsCleaner as cc
import ItemSelector as ise

pd.options.display.max_colwidth = 1000

class UploadFileForm(forms.Form):
    file = forms.FileField()

# View for the list of data tools
def data_tools(request):
    return render(
        request,
        'data_tools/data_tools.html',
        {}
    )

# View for CPC and Descriptions Extractor
def cpc_extractor(request):
    errors = []
    warnings = []
    valid = False
    targetSheetName = None
    form = None
    columnList = None
    sampleFileHTML = None
    inputFileHTML = None
    CPCDescriptionsHTML = None

    inFileName = 'cpcExtractorInput'
    outFileName = 'CPC Nodes with Descriptions'
    inFolderName = '../in/'
    outFolderName = '../out/'
    fileType = '.xlsx'
    sheetName = 'Sheet1'
    
    # Submit File View Setup
    if(request.method == "POST" and request.POST.get('upload')): 
        form = UploadFileForm(request.POST, request.FILES)
        inputFile = request.FILES['file']
        if form.is_valid():
            inputFile = request.FILES['file']
            targetSheetName = request.POST.get('target-sheet')
            # TODO: Validate file
            # if(valid):
            # Read data from input excel file and save it as a dataframe
            inputFileDF = pd.read_excel(inputFile, targetSheetName)
            columnList = inputFileDF.columns
            inputFileDF.to_excel(inFolderName + inFileName + fileType, index=False)
            inputFileHTML = inputFileDF.to_html()
        try:       
            if(inputFile):
                inputFile.close()
        except Exception:
            valid = False
            errors.append("The process cannot access the input file because it is being used by another process.")
        valid = True

    # Process File View Setup
    elif(request.method == "POST" and request.POST.get('process')):
        targetColumnName = request.POST.get('target-column')
        # TODO: Get CPCs and descriptions from the database
        descriptionsDF = pd.read_excel('../out/CPC Descriptions.xlsx', sheetName)
        inputFileDF = pd.read_excel(inFolderName + inFileName + fileType, sheetName)
        outDF = pd.DataFrame()
        outDF = inputFileDF.copy()
        outDF['Descriptions'], outDF['CPC'] = pp.getCPCDescriptions(pd.DataFrame(outDF, columns=outDF.keys()), descriptionsDF, targetColumnName)
        CPCDescriptionsHTML = outDF.to_html()
        outDF.to_excel(outFolderName + outFileName + fileType)
    
    # Default View Setup
    else:
        form = UploadFileForm()
        sampleFileDF = pd.read_excel('../out/Sample File for CPC and Descriptions Extractor.xlsx', 'Sheet1')
        sampleFileHTML = sampleFileDF.to_html()

    return render(
        request,
        'data_tools/cpc_extractor.html',
        {
            'form': form,
            'valid': valid,
            'errors': errors,
            'warnings': warnings,
            'columnList': columnList,
            'sampleFileHTML': sampleFileHTML,
            'inputFileHTML': inputFileHTML,
            'CPCDescriptionsHTML': CPCDescriptionsHTML,
        }
    )

# View for Co-Occurrence Matrix Generator
def co_occurrence(request):
    errors = []
    warnings = []
    valid = False
    targetSheetName = None
    form = None
    columnList = None
    matrix = None
    sampleFileHTML = None
    inputFileHTML = None
    matrixHTML = None

    inFileName = 'coOccurrenceInput'
    outFileName = 'Co-Occurrence Matrix'
    inFolderName = '../in/'
    outFolderName = '../out/'
    fileType = '.xlsx'
    sheetName = 'Sheet1'

    # Submit File View Setup
    if(request.method == "POST" and request.POST.get('upload')): 
        form = UploadFileForm(request.POST, request.FILES)
        inputFile = request.FILES['file']
        if form.is_valid():
            inputFile = request.FILES['file']
            targetSheetName = request.POST.get('target-sheet')
            # TODO: Validate file
            # if(valid):
            # Read data from input excel file and save it as a dataframe
            inputFileDF = pd.read_excel(inputFile, targetSheetName)
            columnList = inputFileDF.columns
            inputFileDF.to_excel(inFolderName + inFileName + fileType, index=False)
            inputFileHTML = inputFileDF.to_html()
        try:       
            if(inputFile):
                inputFile.close()
        except Exception:
            valid = False
            errors.append("The process cannot access the input file because it is being used by another process.")
        valid = True

    # Submit File View
    elif(request.method == "POST" and request.POST.get('process')): 
        targetColumnName = request.POST.get('target-column')
        targetColumnType = request.POST.get('column-type')
        # TODO: Validate file
        df = pd.read_excel(inFolderName + inFileName + fileType, sheetName)
        if(targetColumnType == 'category'):
            df['cleanCategories'] = catc.getCleanL1L2L3Categories(df[targetColumnName])
            categories = df['cleanCategories'].tolist()
        elif(targetColumnType == 'cpc'):
            df['cleanCPCs'], df['cleanCPC4s'] = cc.getCPCs(df[targetColumnName])
            categories = df['cleanCPCs'].tolist()

        allCategories = []
        categoryList = []

        for cList in categories:
            if(cList and cList == cList):
                categoryList.append(cList)

        for cList in categories:
            if(cList and cList == cList):
                # for c in ast.literal_eval(cList):
                for c in cList:
                    allCategories.append(c)
        uniqueCategories = set(allCategories)

        matrix = pd.DataFrame(columns=uniqueCategories, index=uniqueCategories)
        for a in uniqueCategories:
            for b in uniqueCategories:
                count = 0
                for x in categoryList:
                    if a != b:
                        if a in x and b in x:
                            count += 1
                    else:
                        n = x.count(a)
                        if n >= 2:
                            count += math.factorial(n)/math.factorial(n - 2)/2
                matrix.at[a, b] = count

        matrix = matrix.reset_index()
        matrix.to_excel(outFolderName + outFileName + fileType, index=False)
        matrixHTML = matrix.to_html()

    # Default View
    else:
        form = UploadFileForm()
        sampleFileDF = pd.read_excel('../out/Sample File for Co-Occurrence Matrix.xlsx', 'Sheet1')
        sampleFileHTML = sampleFileDF.to_html()

    return render(
        request,
        'data_tools/co_occurrence.html',
        {
            'form': form,
            'valid': valid,
            'errors': errors,
            'warnings': warnings,
            'columnList': columnList,
            'sampleFileHTML': sampleFileHTML,
            'inputFileHTML': inputFileHTML,
            'matrixHTML': matrixHTML,
        }
    )

# View for updating category keywords
def new_category_set_keywords(request):
    form = None
    errors = []
    warnings = []
    valid = False
    hasInputFile = False
    targetSheetName = None
    columnList = None
    data_set = 'index'
    inFolderName = '../in/'
    inFileName = 'newCategorySetInput'
    fileType = '.xlsx'

    # Submit File View Setup
    if(request.method == "POST" and request.POST.get('upload')):  
        form = UploadFileForm(request.POST, request.FILES)
        inputFile = request.FILES['file']
        if form.is_valid():
            inputFile = request.FILES['file']
            targetSheetName = request.POST.get('target-sheet')
            inputFileDF = pd.read_excel(inputFile, targetSheetName)
            columnList = list(inputFileDF.columns)
            inputFileDF.to_excel(inFolderName + inFileName + fileType, index=False)
        try:       
            if(inputFile):
                inputFile.close()
        except Exception:
            valid = False
            errors.append("The process cannot access the input file because it is being used by another process.")
        hasInputFile = True

    # Step 2 View
    elif(request.method == "POST" and request.POST.get('finish')): 
        categorySetName = request.POST.get('category-set-name')
        targetCategoryColumnName = request.POST.get('target-column-category')
        targetKeywordsColumnName = request.POST.get('target-column-keywords')
        df = pd.read_excel(inFolderName + inFileName + fileType, 'Sheet1')
        df = df.rename(index=str, columns={
            targetCategoryColumnName: "Category", 
            targetKeywordsColumnName: "Keywords", 
            })
        dbq.insertCategoryKeywords(df, categorySetName)
        hasInputFile = True
        valid = True
    
        dataSetNames = []
        datasets = Datasets.objects.all()
        for dataset in datasets:
            dataSetNames.append(dataset.name)
        dataSetNames.insert(0, 'index')

        categorySetNames = []
        categorySets = CategorySet.objects.all()
        for categorySet in categorySets:
            categorySetNames.append(categorySet.name)

        templateHTML = 'data_tools/view_category_sets.html'
        mainHTML = render_to_string(
            templateHTML, {
            'valid': valid,
            'errors': errors,
            'warnings': warnings,
            'valid': valid,
            'hasInputFile': hasInputFile,
            'columnList': columnList,
            'data_set': data_set,
            'dataSetNames': dataSetNames,
            'categorySetNames': categorySetNames,
        })
        return mainHTML

    # Default View
    else:
        form = UploadFileForm()
        sampleFileDF = pd.read_excel('../out/Category Keywords.xlsx', 'Sheet1')
        sampleFileHTML = sampleFileDF.to_html()

    templateHTML = 'data_tools/new_category_set_keywords.html'
    mainHTML = render_to_string(
        templateHTML, {
        'form': form,
        'valid': valid,
        'errors': errors,
        'warnings': warnings,
        'valid': valid,
        'hasInputFile': hasInputFile,
        'columnList': columnList,
    })
    return mainHTML

# View for categorize by keywords setup
def categorize_by_keywords(request, data_set, category_set):
    form = None
    errors = []
    warnings = []
    valid = False
    hasDataSet = False
    hasCategorySet = False
    dataSetNames = []
    categorySetNames = []
    classificationHTML = None
    outFileName = 'Categorize by Keywords'
    outFolderName = '../out/'
    fileType = '.xlsx'
    
    datasets = Datasets.objects.all()
    for dataset in datasets:
        dataSetNames.append(dataset.name)
    dataSetNames.insert(0, 'index')

    categorySets = CategorySet.objects.all()
    for categorySet in categorySets:
        categorySetNames.append(categorySet.name)
    categorySetNames.insert(0, 'index')

    if(not data_set == 'index'):
        hasDataSet = True

    if(not category_set == 'index'):
        hasCategorySet = True

    if(not data_set == 'index' and not category_set == 'index' and request.method == 'POST'):
        targetFeatures = request.POST.getlist('features')
        df = pd.DataFrame()
        df = dbq.getDataSetPatentTACs(data_set, df)
        keywordsDF = dbq.getAllCategoryKeywords(category_set)
        df = pp.categorizeByKeywords(df, keywordsDF, targetFeatures)
        dbq.updateCategoryByKeywords(data_set, df)
        valid = True

    templateHTML = 'data_tools/categorize_by_keywords.html'
    mainHTML = render_to_string(
        templateHTML, {
        'form': form,
        'valid': valid,
        'hasDataSet': hasDataSet,
        'hasCategorySet': hasCategorySet,
        'errors': errors,
        'warnings': warnings,
        'data_set': data_set,
        'category_set': category_set,
        'dataSetNames': dataSetNames,
        'categorySetNames': categorySetNames,
    })
    return mainHTML

# View for the list of categorize by keywords feature
def view_category_sets(request, category_set):
    errors = []
    warnings = []
    categorySetNames = []
    keywordsDFHTML = None
    categorySets = CategorySet.objects.all()
    for categorySet in categorySets:
        categorySetNames.append(categorySet.name)

    if(category_set != 'index'):
        keywordsDF = dbq.getAllCategoryKeywords(category_set)
        keywordsDFHTML = keywordsDF.to_html()

    templateHTML = 'data_tools/view_category_sets.html'
    mainHTML = render_to_string(
        templateHTML, {
            'categorySetNames': categorySetNames,
            'keywordsDFHTML': keywordsDFHTML,
            'errors': errors,
            'warnings': warnings,
    })
    return mainHTML
    
# View for the list of categorize by keywords feature
def view_training_sets(request):
    errors = []
    warnings = []
    trainingSetNames = []
    trainingSets = TrainingDatasets.objects.all()
    for trainingSet in trainingSets:
        trainingSetNames.append(trainingSet.name)

    templateHTML = 'data_tools/view_training_sets.html'
    mainHTML = render_to_string(
        templateHTML, {
            'trainingSetNames': trainingSetNames,
            'errors': errors,
            'warnings': warnings,
    })
    return mainHTML
    
# View for the list of categorize by keywords feature
def new_training_setup(request):
    errors = []
    warnings = []
    form = None
    valid = False
    hasInputFile = False
    columnList = None
    sampleFileHTML = None
    inputFileHTML = None

    inFileName = 'newTrainingInput'
    inFolderName = '../in/'
    fileType = '.xlsx'
    
    # Submit File View Setup
    if(request.method == "POST" and request.POST.get('upload')): 
        form = UploadFileForm(request.POST, request.FILES)
        inputFile = request.FILES['file']
        if form.is_valid():
            inputFile = request.FILES['file']
            targetSheetName = request.POST.get('target-sheet')
            inputFileDF = pd.read_excel(inputFile, targetSheetName)
            columnList = list(inputFileDF.columns)
            inputFileDF.to_excel(inFolderName + inFileName + fileType, index=False)
            inputFileHTML = inputFileDF.head(50).to_html()
        try:       
            if(inputFile):
                inputFile.close()
        except Exception:
            valid = False
            errors.append("The process cannot access the input file because it is being used by another process.")
        hasInputFile = True

    # Step 2 View
    elif(request.method == "POST" and request.POST.get('finish')): 
        trainingSetName = request.POST.get('training-set-name')
        targetClassificationColumnName = targetClassificationOldColumnName = request.POST.get('target-column-classification')
        targetTitlesColumnName = request.POST.get('target-column-titles')
        targetAbstractsColumnName = request.POST.get('target-column-abstracts')
        targetIndependentClaimsColumnName = request.POST.get('target-column-independent-claims')
 
        df = pd.read_excel(inFolderName + inFileName + fileType, 'Sheet1')
        df = df.rename(index=str, columns={
            targetClassificationColumnName: "CLASSIFICATIONS", 
            targetTitlesColumnName: "TITLES",
            targetAbstractsColumnName: "ABSTRACTS",
            targetIndependentClaimsColumnName: "INDEPENDENT CLAIMS",
        })
        dbq.insertTrainingPatents(df, trainingSetName, targetClassificationOldColumnName)
        hasInputFile = True
        valid = True
        
        trainingSetNames = []
        trainingDataSets = TrainingDatasets.objects.all()
        for trainingDataSet in trainingDataSets:
            trainingSetNames.append(trainingDataSet.name)

        templateHTML = 'data_tools/view_training_sets.html'
        mainHTML = render_to_string(
            templateHTML, {
                'trainingSetNames': trainingSetNames,
                'errors': errors,
                'warnings': warnings,
        })
        return mainHTML

    # Default View
    else:
        form = UploadFileForm()
        sampleFileDF = pd.read_excel('../out/Sample File for Training Set.xlsx', 'Sheet1')
        sampleFileHTML = sampleFileDF.head().to_html()

    templateHTML = 'data_tools/new_training_setup.html'
    mainHTML = render_to_string(
        templateHTML, {
            'form': form,
            'valid': valid,
            'hasInputFile': hasInputFile,
            'errors': errors,
            'warnings': warnings,
            'columnList': columnList,
            'sampleFileHTML': sampleFileHTML,
            'inputFileHTML': inputFileHTML,
    })
    return mainHTML

# View for the lisst of training sets
def view_training_set(request, training_set):
    df = dbq.getTrainingSetPatents(training_set)
    dataHTML = df.head(50).to_html()

    categories = dbq.getTrainingSetPatentClassifications(training_set)

    return render(
        request,
        'data_tools/view.html',{
            'training_set': training_set,
            'categories': categories,
            'dataHTML': dataHTML
        }
    )

# View for Automated Patent Classification
def automated_patent_classification(request, data_set, training_set):
    errors = []
    warnings = []
    valid = False
    form = None
    hasDataSet = False
    dataSetNames = []
    trainingDataSetNames = []
    classificationHTML = None
    tagWordsHTML = None
    trainConfusionMatrixHTML = None
    testConfusionMatrixHTML = None
    trainCorrectness = None
    testCorrectness = None
    targetClassificationColumnName = None
    targetTitlesColumnName = None
    targetAbstractsColumnName = None
    targetIndependentClaimsColumnName = None
    targetTestSize = None
    targetFeatures = None

    outFileName = 'Automated Patent Classification'
    outCountFileName = 'classificationBarGraphInput'
    outAccuracyFileName = 'classificationAccuracyBarGraphInput'
    outTagWordsFileName = 'Tag Words'
    outFolderName = '../out/'
    inFolderName = '../in/'
    outCountFolderName = '../templates/visualization/'
    fileType = '.xlsx'
    outCountFileType = '.tsv'
    sheetName = 'Sheet1'

    # Data set selection view
    if(data_set == 'index' or training_set == 'index'):
        datasets = Datasets.objects.all()
        for dataset in datasets:
            dataSetNames.append(dataset.name)
        dataSetNames.insert(0, 'index')
        
        trainingDataSets = TrainingDatasets.objects.all()
        for trainingDataSet in trainingDataSets:
            trainingDataSetNames.append(trainingDataSet.name)
        trainingDataSetNames.insert(0, 'index')

    # Model setup view
    elif(not data_set == 'index' and not request.method == 'POST'):
        hasDataSet = True

    # Process setup view
    elif(request.method == "POST"): 
        targetIDsColumnName = 'ids'
        targetTitlesColumnName = 'Titles'
        targetPublicationNumbersColumnName = 'Publication Numbers'
        targetAbstractsColumnName = 'Abstracts'
        targetIndependentClaimsColumnName = 'Independent Claims'
        targetClassificationColumnName = 'Categories'
        targetFeatures = request.POST.getlist('features')
        targetTestSize = request.POST.get('target-test-size')
        targetMethod = request.POST.get('method')
        targetNumberOfEstimators = request.POST.get('target-n-estimator')
        targetLearningRate = request.POST.get('target-learning-rate')
        targetNGram1 = request.POST.get('target-n-gram-1')
        targetNGram2 = request.POST.get('target-n-gram-2')

        df = dbq.getDataSetPatents(data_set)
        trainDF = dbq.getTrainingSetPatents(training_set)
        # trainDF = dbq.getTrainingSetPatents2(training_set)
        df, tagWordsDF, trainConfusionMatrix, testConfusionMatrix = pp.classifyPatents( df, trainDF,
                            targetClassificationColumnName, 
                            targetTitlesColumnName, 
                            targetAbstractsColumnName, 
                            targetIndependentClaimsColumnName, 
                            targetFeatures, 
                            float(targetTestSize), 
                            targetMethod, 
                            int(targetNumberOfEstimators), 
                            float(targetLearningRate), 
                            int(targetNGram1), 
                            int(targetNGram2))
        
        # # Update database
        # dataSet = Datasets.objects.filter(name=data_set)
        # ids = df['ids']
        # categories = df['Predicted Classifications'].tolist()
        # for idx, category in zip(ids, categories):
        #     Patents.objects.filter(dataset_id=dataSet[0].id, id=idx).update(predicted_categories=category)

        if(float(targetTestSize) > 0):
            testCorrectness = testConfusionMatrix['Correct'].sum()/(testConfusionMatrix['Correct'].sum() + testConfusionMatrix['Incorrect'].sum())
            testConfusionMatrix = testConfusionMatrix.drop(columns=['Correct', 'Incorrect'])
            testConfusionMatrix.reset_index().to_csv(outCountFolderName + outAccuracyFileName + outCountFileType, sep='\t', index=False)
            testConfusionMatrixHTML = testConfusionMatrix.to_html()

        trainCorrectness = trainConfusionMatrix['Correct'].sum()/(trainConfusionMatrix['Correct'].sum() + trainConfusionMatrix['Incorrect'].sum())

        classificationHTML = df.head(50).to_html()
        if(tagWordsDF.empty):
            tagWordsHTML = None
        else:
            tagWordsHTML = tagWordsDF.to_html()
            tagWordsDF.to_excel(outFolderName + outTagWordsFileName + fileType)
        trainConfusionMatrixHTML = trainConfusionMatrix.to_html()
        df.to_excel(outFolderName + outFileName + fileType)
        allClassifications = []
        # for classificationList in df['Predicted Classifications'].tolist():
        #     for classification in classificationList:
        #         allClassifications.append(classification)
        # expandedDF = pd.DataFrame()
        # expandedDF['classification'] = allClassifications
        # groupSizes = expandedDF.groupby(['classification']).size().sort_values(ascending=False)
        # groupSizes.rename(
        #     columns={0: 'Count'}, inplace=True)
        # groupSizes.reset_index().to_csv(outCountFolderName + outCountFileName + outCountFileType, sep='\t', index=False)
        
        hasDataSet = True
        valid = True
    
    templateHTML = 'data_tools/automated_patent_classification.html'
    mainHTML = render_to_string(
        templateHTML, {
            'form': form,
            'valid': valid,
            'errors': errors,
            'warnings': warnings,
            'data_set': data_set,
            'training_set': training_set,
            'hasDataSet': hasDataSet,
            'dataSetNames': dataSetNames,
            'trainingDataSetNames': trainingDataSetNames,
            'classificationHTML': classificationHTML,
            'tagWordsHTML': tagWordsHTML,
            'trainConfusionMatrixHTML': trainConfusionMatrixHTML,
            'testConfusionMatrixHTML': testConfusionMatrixHTML,
            'trainCorrectness': trainCorrectness,
            'testCorrectness': testCorrectness,
    })
    return mainHTML

def input_classification_bar_graph(request):
    categoryBarGraphInput = None
    outFileName = 'classificationBarGraphInput'
    outFolderName = '../templates/visualization/'
    fileType = '.tsv'
    with open(outFolderName  + outFileName + fileType, 'r') as myfile:
        categoryBarGraphInput=myfile.read()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'filename="' + outFolderName + outFileName + fileType + '"'
    response.write(categoryBarGraphInput)
    return response
    
def input_classification_accuracy_bar_graph(request):
    categoryBarGraphInput = None
    outFileName = 'classificationAccuracyBarGraphInput'
    outFolderName = '../templates/visualization/'
    fileType = '.tsv'
    with open(outFolderName  + outFileName + fileType, 'r') as myfile:
        categoryBarGraphInput=myfile.read()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'filename="' + outFolderName + outFileName + fileType + '"'
    response.write(categoryBarGraphInput)
    return response
    
# function for downloading CPC extractor sample file as Excel file
def download_sample_cpc_extractor(request):
    outFileName = 'Sample File for CPC and Descriptions Extractor'
    outFolderName = '../out/'
    fileType = '.xlsx'
    path = outFolderName + outFileName + fileType
    if os.path.exists(path):
        with open(path, "rb") as excel:
            data = excel.read()
        response = HttpResponse(data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=' + outFileName + fileType
        return response

# function for downloading Co-Occurrent sample file as Excel file
def download_sample_co_occurrence(request):
    outFileName = 'Sample File for Co-Occurrence Matrix'
    outFolderName = '../out/'
    fileType = '.xlsx'
    path = outFolderName + outFileName + fileType
    if os.path.exists(path):
        with open(path, "rb") as excel:
            data = excel.read()
        response = HttpResponse(data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=' + outFileName + fileType
        return response

# function for downloading CPC extractor results as Excel file
def download_cpc_extractor(request):
    outFileName = 'CPC Nodes with Descriptions'
    outFolderName = '../out/'
    fileType = '.xlsx'
    path = outFolderName + outFileName + fileType
    if os.path.exists(path):
        with open(path, "rb") as excel:
            data = excel.read()
        response = HttpResponse(data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=' + outFileName + fileType
        return response

# function for downloading co-occurrence matrix results as Excel file
def download_co_occurrence(request):
    outFileName = 'Co-Occurrence Matrix'
    outFolderName = '../out/'
    fileType = '.xlsx'
    path = outFolderName + outFileName + fileType
    if os.path.exists(path):
        with open(path, "rb") as excel:
            data = excel.read()
        response = HttpResponse(data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=' + outFileName + fileType
        return response

# function for downloading categorize by keywords results as Excel file
def download_sample_category_keywords(request):
    outFileName = 'Category Keywords'
    outFolderName = '../out/'
    fileType = '.xlsx'
    path = outFolderName + outFileName + fileType
    if os.path.exists(path):
        with open(path, "rb") as excel:
            data = excel.read()
        response = HttpResponse(data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=' + outFileName + fileType
        return response

# function for downloading categorize by keywords results as Excel file
def download_categorize_by_keywords(request):
    outFileName = 'Categorize by Keywords'
    outFolderName = '../out/'
    fileType = '.xlsx'
    path = outFolderName + outFileName + fileType
    if os.path.exists(path):
        with open(path, "rb") as excel:
            data = excel.read()
        response = HttpResponse(data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=' + outFileName + fileType
        return response

# function for downloading Classification results as Excel file
def download_classification(request):
    outFileName = 'Automated Patent Classification'
    outFolderName = '../out/'
    fileType = '.xlsx'
    path = outFolderName + outFileName + fileType
    if os.path.exists(path):
        with open(path, "rb") as excel:
            data = excel.read()
        response = HttpResponse(data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=' + outFileName + fileType
        return response

# function for downloading tag words as Excel file
def download_tag_words(request):
    outFileName = 'Tag Words'
    outFolderName = '../out/'
    fileType = '.xlsx'
    path = outFolderName + outFileName + fileType
    if os.path.exists(path):
        with open(path, "rb") as excel:
            data = excel.read()
        response = HttpResponse(data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=' + outFileName + fileType
        return response

