from django.shortcuts import render
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, JsonResponse

# Function for sending input in group by format
def getGroupByInput(request, df, columnName, countColumnName):
    json = None
    json = [
        {'Years': 2007, 'nPPA': 14},
        {'Years': 2008, 'nPPA': 7},
        {'Years': 2009, 'nPPA': 9},
        {'Years': 2010, 'nPPA': 31},
        {'Years': 2011, 'nPPA': 55},
        {'Years': 2012, 'nPPA': 42},
        {'Years': 2013, 'nPPA': 49},
        {'Years': 2014, 'nPPA': 34},
        {'Years': 2015, 'nPPA': 12},
        {'Years': 2016, 'nPPA': 16},
    ]

    return json
