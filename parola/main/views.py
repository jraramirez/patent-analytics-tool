from django.shortcuts import render
from django.template.loader import render_to_string, get_template
from django.views.decorators.csrf import csrf_exempt

from data_sets import views as data_sets_views
from uspto import views as uspto_views
from data_tools import views as data_tools_views
from parola_refine import views as parola_refine_views
from visualization import views as visualization_tools_views

import pandas as pd
import urllib

pd.options.display.max_colwidth = 1000

# View for the list of patent analytics tools
@csrf_exempt
def index(request):
    mainHTML = None
    path = request.path[1:]
    if(len(path.split('/'))>1):
        url = path.split('/')[0] + '/' + path.split('/')[1]
        parameters = path.split('/')[2:]

        # Data set features
        if(url == 'data_sets/new_data_setup'):
            mainHTML = data_sets_views.new_data_setup(request)

        elif(url == 'data_sets/view_data_sets'):
            data_set = parameters[0]
            mainHTML = data_sets_views.view_data_sets(request, data_set)

        elif(url == 'data_sets/index'):
            mainHTML = data_sets_views.index(request)

        elif(url == 'uspto/general_trends'):
            date = parameters[0]
            mainHTML = uspto_views.general_trends(request, date)

        elif(url == 'uspto/assignee_trends'):
            date = parameters[0]
            mainHTML = uspto_views.assignee_trends(request, date)

        elif(url == 'uspto/sector_trends'):
            date = parameters[0]
            mainHTML = uspto_views.sector_trends(request, date)

        elif(url == 'uspto/sector_trends'):
            date = parameters[0]
            mainHTML = uspto_views.sector_trends(request, date)

        # Data tools features
        elif(url == 'data_tools/view_category_sets'):
            category_set = parameters[0]
            mainHTML = data_tools_views.view_category_sets(request, category_set)

        elif(url == 'data_tools/new_category_set_keywords'):
            mainHTML = data_tools_views.new_category_set_keywords(request)

        elif(url == 'data_tools/categorize_by_keywords'):
            data_set = parameters[0]
            category_set = parameters[1]
            mainHTML = data_tools_views.categorize_by_keywords(request, data_set, category_set)

        elif(url == 'data_tools/automated_patent_classification'):
            data_set = parameters[0]
            training_set = parameters[1]
            mainHTML = data_tools_views.automated_patent_classification(request, data_set, training_set)

        elif(url == 'data_tools/new_training_setup'):
            mainHTML = data_tools_views.new_training_setup(request)

        elif(url == 'data_tools/view_training_sets'):
            mainHTML = data_tools_views.view_training_sets(request)

        elif(url == 'parola_refine/reference_update'):
            mainHTML = parola_refine_views.reference_update(request)

        elif(url == 'parola_refine/assignee_grouping'):
            data_set = parameters[0]
            mainHTML = parola_refine_views.assignee_grouping(request, data_set)

        # Visualization tools features
        elif(url == 'visualization/dataset_statistics'):
            data_set = parameters[0]
            classification = parameters[1]
            mainHTML = visualization_tools_views.dataset_statistics(request, data_set, classification)

        elif(url == 'visualization/category_statistics'):
            data_set = parameters[0]
            classification = parameters[1]
            category = parameters[2]
            mainHTML = visualization_tools_views.category_statistics(request, data_set, classification, category)

        elif(url == 'visualization/assignee_statistics'):
            data_set = parameters[0]
            classification = parameters[1]
            assignee = parameters[2]
            mainHTML = visualization_tools_views.assignee_statistics(request, data_set, classification, assignee)

        # Visualization tools features
        elif(url == 'visualization/cluster_map'):
            data_set = parameters[0]
            classification1 = parameters[1]
            classification2 = parameters[2]
            mainHTML = visualization_tools_views.cluster_map(request, data_set, classification1, classification2)

        elif(url == 'visualization/word_cluster_map'):
            data_set = parameters[0]
            column = parameters[1]
            mainHTML = visualization_tools_views.word_cluster_map(request, data_set, column)

        elif(url == 'visualization/landscape_map'):
            data_set = parameters[0]
            mainHTML = visualization_tools_views.landscape_map(request, data_set)

        # Default welcome page
        else:
            mainHTML = render_to_string('main/welcome.html')

    # Default welcome page
    else:
        mainHTML = render_to_string('main/welcome.html')
    
    return render(
        request,
            'main/index.html',{
            'mainHTML': mainHTML,
        }
    )