from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from wsgiref.util import FileWrapper
from django import forms
from django.template.loader import render_to_string

from data_sets.models import Patents
from data_sets.models import Datasets

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

class UploadFileForm(forms.Form):
    file = forms.FileField()

# View for the list of data tools
def index(request):

    return render(
        request,
        'parola_refine/index.html',
        {
        }
    )

# View for Parola Refine Reference Update
def reference_update(request):
    errors = []
    warnings = []
    valid = False
    inputFile = None
    referenceTableHTML = None
    sampleFileHTML = None
    
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
            inputFileDF = pd.read_excel(inputFile, targetSheetName)
            dbq.insertAssigneeKeywords(inputFileDF)
        try:       
            if(inputFile):
                inputFile.close()
        except Exception:
            valid = False
            errors.append("The process cannot access the input file because it is being used by another process.")
        valid = True

        templateHTML = 'parola_refine/index.html'
        mainHTML = render_to_string(
            templateHTML, {
        })
        return mainHTML

    # Submit File View
    elif(request.method == "POST" and request.POST.get('process')): 
        targetColumnName = request.POST.get('target-column')

    # Default View
    else:
        form = UploadFileForm()

    templateHTML = 'parola_refine/reference_update.html'
    mainHTML = render_to_string(
        templateHTML, {
        'form': form,
        'valid': valid,
        'errors': errors,
        'warnings': warnings,
        'inputFile': inputFile,
        'sampleFileHTML': sampleFileHTML,
    })
    return mainHTML

# View for Parola Refine Assignee Grouping
def assignee_grouping(request, data_set):
    form = None
    errors = []
    warnings = []
    valid = False
    inputFile = None
    referenceTableHTML = None
    assigneeGroupingHTML = None
    assigneeGroupingSummaryHTML = None
    sampleFileHTML = None
    dataSetNames = []
    
    outFileName = 'Assignee Grouping'
    outFolderName = '../out/'
    fileType = '.xlsx'
    sheetName = 'Sheet1'

    datasets = Datasets.objects.all()
    for dataset in datasets:
        dataSetNames.append(dataset.name)
    dataSetNames.insert(0, 'index')

    if(not data_set == 'index'):
        df = pd.DataFrame()
        df = dbq.getDataSetPatentAssignees(data_set, df)
        keywordsDF = dbq.getAllAssigneeKeywords()
        df = pp.updateAssigneeGrouping(df, keywordsDF)
        dbq.updateCleanCurrentAssignees(data_set, df)
        df.to_excel(outFolderName + outFileName + fileType)
        assigneeGroupingHTML = df.head(10).to_html(index=False)
        valid = True
    #     for CAs in df[targetColumnName].tolist():
    #         if(CAs == CAs):
    #             tempCAList = []
    #             CAList = str(CAs).splitlines()
    #             for CA in CAList:
    #                 group = pp.getAssgineeGroup(CA, referenceDF)
    #                 if(CA.lower().lstrip().rstrip() != group.lower().lstrip().rstrip()):
    #                     allCounts[allGroups.index(group)] = allCounts[allGroups.index(group)] + 1
    #                 tempCAList.append(group)
    #             tempCAListString = str(tempCAList).lstrip().rstrip().replace("'", '')
    #             newCAs.append(tempCAListString)
    #         else:
    #             newCAs.append(None)
    #     df['Assignee Group'] = newCAs
    #     referenceDF['Counts'] = allCounts
    # df.to_excel(outFolderName + outFileName + fileType)
    # assigneeGroupingHTML = df.to_html(index=False)
    # referenceDF = referenceDF.drop(columns = ['Contains',  'Does Not Contain'])
    # assigneeGroupingSummaryHTML = referenceDF.to_html(index=False)

    templateHTML = 'parola_refine/assignee_grouping.html'
    mainHTML = render_to_string(
        templateHTML, {
        'form': form,
        'valid': valid,
        'errors': errors,
        'warnings': warnings,
        'data_set': data_set,
        'dataSetNames': dataSetNames,
        'assigneeGroupingHTML': assigneeGroupingHTML,
    })
    return mainHTML

# function for downloading Assignee Grouping sample file as Excel file
def download_sample_assignee_grouping(request):
    outFileName = 'Sample File for Assignee Grouping'
    outFolderName = '../out/'
    fileType = '.xlsx'
    path = outFolderName + outFileName + fileType
    if os.path.exists(path):
        with open(path, "rb") as excel:
            data = excel.read()
        response = HttpResponse(data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=' + outFileName + fileType
        return response

# function for downloading Assignee Grouping results as Excel file
def download_assignee_grouping(request):
    outFileName = 'Assignee Grouping'
    outFolderName = '../out/'
    fileType = '.xlsx'
    path = outFolderName + outFileName + fileType
    if os.path.exists(path):
        with open(path, "rb") as excel:
            data = excel.read()
        response = HttpResponse(data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=' + outFileName + fileType
        return response

