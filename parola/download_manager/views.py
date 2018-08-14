from django.shortcuts import render
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, JsonResponse

import os

def index(request):
    return render(
        request,
            'download_manager/index.html',
        {}
    )

# function for downloading chart raw data
def download_chart_raw_data(request, app_name, file_name, file_type):
    inFolderName = '../templates/' + app_name
    path = inFolderName + '/' + file_name + '.' + file_type
    print(path)
    if os.path.exists(path):
        with open(path, "rb") as excel:
            data = excel.read()
        response = HttpResponse(data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=' + file_name + '.' + file_type
        return response