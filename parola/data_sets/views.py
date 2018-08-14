from django.shortcuts import render
from django.template.loader import render_to_string
from django import forms
from django.db import transaction
from django.template.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt


import pandas as pd

from data_sets.models import Patents
from data_sets.models import Datasets

import PatentProcessing as pp
import CategoriesCleaner as catc
import ClaimsCleaner as cc
import ItemSelector as ise
import DBQueries as dbq

class UploadFileForm(forms.Form):
    file = forms.FileField()

# View for the list of data set actions
def index(request):
    df = pd.read_excel('../out/Assignee Sectors and Industries.xlsx', 'Sheet1')
    dbq.updateAssigneesRankSectorIndustry(df)
    # dbq.insertCPCDescriptions()
    dataSetNames = []
    datasets = Datasets.objects.all()
    for dataset in datasets:
        dataSetNames.append(dataset.name)
    dataSetNames.sort()

    templateHTML = 'data_sets/index.html'
    mainHTML = render_to_string(
        templateHTML, {
        'dataSetNames': dataSetNames,
    })
    return mainHTML

def new_data_setup(request):
    errors = []
    warnings = []
    form = None
    valid = False
    hasInputFile = False
    columnList = None
    dataSetName = None
    targetYearColumnName = None
    targetAssigneeColumnName = None
    sampleFileHTML = None
    inputFileHTML = None
    inFileName = 'newDataInput'
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
            columnList.append('Not Applicable')
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
        dataSetName = request.POST.get('data-set-name')
        sourceName = request.POST.get('target-source')
        targetPublicationNumberColumnName = request.POST.get('target-column-publication-number')
        targetAssigneeColumnName = request.POST.get('target-column-assignee')
        targetYearColumnName = request.POST.get('target-column-year')
        targetMainCPCColumnName = request.POST.get('target-main-cpc')
        targetCPCColumnName = request.POST.get('target-column-cpc')
        targetCategoryColumnName = request.POST.get('target-column-category')
        targetTitlesColumnName = request.POST.get('target-column-titles')
        targetAbstractsColumnName = request.POST.get('target-column-abstracts')
        targetIndependentClaimsColumnName = request.POST.get('target-column-independent-claims')
        targetTechnicalConceptColumnName = request.POST.get('target-column-technical-concepts')
        df = pd.read_excel(inFolderName + inFileName + fileType, 'Sheet1')
        if(targetPublicationNumberColumnName == 'Not Applicable'):
            df['PUBLICATION NUMBER'] = ''
        else:
            df = df.rename(index=str, columns={targetPublicationNumberColumnName: "PUBLICATION NUMBER"})
        if(targetAssigneeColumnName == 'Not Applicable'):
            df['CA'] = ''
        else:
            df = df.rename(index=str, columns={targetAssigneeColumnName: "CA"})
        if(targetYearColumnName == 'Not Applicable'):
            df['YEAR'] = ''
        else:
            df = df.rename(index=str, columns={targetYearColumnName: "YEAR"})
        if(targetMainCPCColumnName == 'Not Applicable'):
            df['MAIN CPC'] = ''
        else:
            df = df.rename(index=str, columns={targetMainCPCColumnName: "MAIN CPC"})
        if(targetCPCColumnName == 'Not Applicable'):
            df['CPC'] = ''
        else:
            df = df.rename(index=str, columns={targetCPCColumnName: "CPC"})
        if(targetCategoryColumnName == 'Not Applicable'):
            df['CATEGORY'] = ''
        else:
            df = df.rename(index=str, columns={targetCategoryColumnName: "CATEGORY"})
        if(targetTitlesColumnName == 'Not Applicable'):
            df['TITLES'] = ''
        else:
            df = df.rename(index=str, columns={targetTitlesColumnName: "TITLES"})
        if(targetAbstractsColumnName == 'Not Applicable'):
            df['ABSTRACTS'] = ''
        else:
            df = df.rename(index=str, columns={targetAbstractsColumnName: "ABSTRACTS"})
        if(targetIndependentClaimsColumnName == 'Not Applicable'):
            df['INDEPENDENT CLAIMS'] = ''
        else:
            df = df.rename(index=str, columns={targetIndependentClaimsColumnName: "INDEPENDENT CLAIMS"})
        if(targetTechnicalConceptColumnName == 'Not Applicable'):
            df['TECHNICAL CONCEPTS'] = ''
        else:
            df = df.rename(index=str, columns={targetTechnicalConceptColumnName: "TECHNICAL CONCEPTS"})
        # df['MAIN CPC DESCRIPTION'] = pp.getCPCDescriptions(df)
        # df['CPC DESCRIPTIONS'] = pp.getCPCListDescriptions(df)
        # temp = cc.removePublicationNumbers(df['TECHNICAL CONCEPTS'].tolist())
        # temp = cc.removeConceptPostfix(temp)
        # temp = cc.getTechnicalConcepts(temp)
        # df['TECHNICAL CONCEPTS'] = temp
        df['TYPE'] = cc.getDocumentTypes(df['PUBLICATION NUMBER'], 9)

        keywordsDF = dbq.getAllAssigneeKeywords()
        df = pp.assigneeGrouping(df, keywordsDF)
        # dbq.updateCleanCurrentAssignees(dataSetName, df)
        dbq.insertPatents(df, dataSetName, sourceName)
        hasInputFile = True
        valid = True
        
        dataSetNames = []
        datasets = Datasets.objects.all()
        for dataset in datasets:
            dataSetNames.append(dataset.name)
        dataSetNames.sort()

        templateHTML = 'data_sets/index.html'
        mainHTML = render_to_string(
            templateHTML, {
            'dataSetNames': dataSetNames,
        })
        return mainHTML

    # Default View
    else:
        form = UploadFileForm()
        sampleFileDF = pd.read_excel('../out/Small Sample File.xlsx', 'Sheet1')
        sampleFileHTML = sampleFileDF.head().to_html()

    templateHTML = 'data_sets/new_data_setup.html'
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

def view_data_set(request, data_set):

    df = dbq.getDataSetPatents(data_set)
    dataHTML = df.head(50).to_html()
    return render(
        request,
        'data_sets/view.html',{
            'data_set': data_set,
            'dataHTML': dataHTML
        }
    )

def view_data_sets(request, data_set):
    templateHTML = 'data_sets/view_data_sets.html'
    mainHTML = render_to_string(
        templateHTML, {
        'data_set': data_set,
    })
    return mainHTML