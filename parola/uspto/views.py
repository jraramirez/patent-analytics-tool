from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from django import forms

from data_sets.models import Patents
from data_sets.models import Datasets

import numpy as np
import pandas as pd
import PatentProcessing as pp
import CategoriesCleaner as catc
import ClaimsCleaner as cc
import Visualization as v
import ItemSelector as ise
import DBQueries as dbq
import ChartInputManager as cim

def general_trends(request, date):
    dates = []
    previousDate = None    
    yearData = None
    targetN = 10

    if(request.method == "POST"): 
        targetN = int(request.POST.get('target-n'))

    df = pd.DataFrame()
    df = dbq.getDataSetPatentsBySource(df, 'uspto')
    assigneeSectorsIndustries = dbq.getAssigneeSectorIndustry()

    for d in list(set(df['Dates'].tolist())):
        dates.append(str(d))
    dates.sort(reverse=True)
    date = dates[0]
    previousDate = dates[1]

    # Number of PPA per week for line graph
    yearData = cim.getGroupByInput(df, 'Dates', 'nPPA')

    # Assignee data preparation
    dfCopy = df.copy()
    dfCopy = dfCopy[dfCopy['Dates'].isin([date, previousDate])]
    dfCopy = pp.assignAssigneeSectorIndustry(dfCopy, assigneeSectorsIndustries, 'uspto')
    dfCopy = dfCopy.dropna(subset=['Sectors'])
    dfCopy['Current Assignees'] = dfCopy['Clean Assignees']
    dfCopy = dfCopy[['Dates', 'Current Assignees', 'ids']]
    assignees = list(set(dfCopy['Current Assignees'].tolist()))
    counts = dfCopy.groupby(['Dates', 'Current Assignees']).size().unstack(fill_value=0).stack().reset_index(name='nPPA')
    countBefore = counts['nPPA'].tolist()[:len(assignees)]
    countAfter = counts['nPPA'].tolist()[len(assignees):]
    differences = counts.groupby(['Current Assignees']).diff()[len(assignees):]
    totals = counts.groupby(['Current Assignees']).sum()
    assigneeData = pd.DataFrame()
    assigneeData['Current Assignees'] = assignees
    assigneeData = assigneeData.sort_values(by='Current Assignees')
    assigneeData['Before'] = countBefore
    assigneeData['After'] = countAfter
    assigneeData['Total'] = totals['nPPA'].tolist()
    assigneeData['Change'] = differences['nPPA'].tolist()
    assigneeData['PercentChange'] = assigneeData['Change']/assigneeData['Total']*100
    assigneeTopLosersData = assigneeData.sort_values(by='Change').head(targetN)
    assigneeData = assigneeData.sort_values(by='Change', ascending=False).head(targetN)
    assigneeLosersChanges = zip(assigneeTopLosersData['Current Assignees'], assigneeTopLosersData['Change'], assigneeTopLosersData['PercentChange'])
    assigneeChanges = zip(assigneeData['Current Assignees'], assigneeData['Change'], assigneeData['PercentChange'])

    # Sector data preparation
    dfCopy = df.copy()
    dfCopy = dfCopy[dfCopy['Dates'].isin([date, previousDate])]
    dfCopy = pp.assignAssigneeSectorIndustry(dfCopy, assigneeSectorsIndustries, 'uspto')
    dfCopy = dfCopy.dropna(subset=['Sectors'])
    dfCopy = dfCopy[['Dates', 'Sectors', 'ids']]
    sectors = list(set(dfCopy['Sectors'].tolist()))
    counts = dfCopy.groupby(['Dates', 'Sectors']).size().unstack(fill_value=0).stack().reset_index(name='nPPA')
    countBefore = counts['nPPA'].tolist()[:len(sectors)]
    countAfter = counts['nPPA'].tolist()[len(sectors):]
    differences = counts.groupby(['Sectors']).diff()[len(sectors):]
    totals = counts.groupby(['Sectors']).sum()
    sectorData = pd.DataFrame()
    sectorData['Sectors'] = sectors
    sectorData = sectorData.sort_values(by='Sectors')
    sectorData['Before'] = countBefore
    sectorData['After'] = countAfter
    sectorData['Total'] = totals['nPPA'].tolist()
    sectorData['Change'] = differences['nPPA'].tolist()
    sectorData['PercentChange'] = sectorData['Change']/sectorData['Total']*100
    sectorData = sectorData.sort_values(by='Change', ascending=False)
    sectorChanges = zip(sectorData['Sectors'], sectorData['Change'], sectorData['PercentChange'])

    templateHTML = 'uspto/general_trends.html'
    mainHTML = render_to_string(
        templateHTML, {
        'date': date,
        'dates': dates,
        'yearData': yearData,
        'sectorData': sectorData,
        'sectorChanges': sectorChanges,
        'assigneeChanges': assigneeChanges,
        'assigneeLosersChanges': assigneeLosersChanges,
        'targetN': targetN,
    })
    return mainHTML

def sector_trends(request, date):
    dates = []
    previousDate = None    
    areaData = None
    targetN = 20

    if(request.method == "POST"): 
        targetN = int(request.POST.get('target-n'))

    df = pd.DataFrame()
    df = dbq.getDataSetPatentsBySource(df, 'uspto')
    assigneeSectorsIndustries = dbq.getAssigneeSectorIndustry()

    for d in list(set(df['Dates'].tolist())):
        dates.append(str(d))
    dates.sort(reverse=True)
    date = dates[0]
    previousDate = dates[1]

    # Area chart data preparation
    dfCopy = df.copy()
    dfCopy = pp.assignAssigneeSectorIndustry(dfCopy, assigneeSectorsIndustries, 'uspto')
    dfCopy = dfCopy.dropna(subset=['Sectors'])
    areaData = dfCopy.groupby(['Dates', 'Sectors']).size().unstack(fill_value=0).stack().reset_index(name='nPPA')
    areaData =  areaData.to_json(orient="index")

    templateHTML = 'uspto/sector_trends.html'
    mainHTML = render_to_string(
        templateHTML, {
        'date': date,
        'dates': dates,
        'areaData': areaData,
        'targetN': targetN,
    })
    return mainHTML

def assignee_trends(request, date):
    dates = []
    previousDate = None    
    areaData = None
    targetN = 9

    if(request.method == "POST"): 
        targetN = int(request.POST.get('target-n'))

    df = pd.DataFrame()
    df = dbq.getDataSetPatentsBySource(df, 'uspto')
    assigneeSectorsIndustries = dbq.getAssigneeSectorIndustry()

    for d in list(set(df['Dates'].tolist())):
        dates.append(str(d))
    dates.sort(reverse=True)
    date = dates[0]
    previousDate = dates[1]

    # Area chart data preparation
    dfCopy = df.copy()
    dfCopy = pp.assignAssigneeSectorIndustry(dfCopy, assigneeSectorsIndustries, 'uspto')
    dfCopy = dfCopy.dropna(subset=['Sectors'])
    areaData = dfCopy.groupby(['Dates', 'Current Assignees']).size().unstack(fill_value=0).stack().reset_index(name='nPPA')
    grouped = dfCopy.groupby(['Current Assignees']).size().reset_index(name='nPPA')
    topNAssignees = grouped.nlargest(targetN, 'nPPA')['Current Assignees'].tolist()
    areaData = areaData[areaData['Current Assignees'].isin(topNAssignees)]
    areaData = areaData.rename(index=str, columns={
        'Current Assignees': "CurrentAssignees"
    })
    areaData =  areaData.to_json(orient="index")

    templateHTML = 'uspto/assignee_trends.html'
    mainHTML = render_to_string(
        templateHTML, {
        'date': date,
        'dates': dates,
        'areaData': areaData,
        'targetN': targetN,
    })
    return mainHTML
