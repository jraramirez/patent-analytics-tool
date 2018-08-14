from data_sets.models import Patents
from data_sets.models import Datasets
from data_sets.models import Assignees
from data_sets.models import RefCpcDescriptions
from data_sets.models import RefCategoryKeywords
from data_sets.models import RefAssigneeKeywords
from data_sets.models import TrainingDatasets
from data_sets.models import TrainingPatents
from data_sets.models import CategorySet
from data_sets.models import CategorySetKeywords

from django.db import transaction

import pandas as pd
import datetime

import CategoriesCleaner as catc

# Insert functions
def insertPatents(df, dataSetName, sourceName):
    with transaction.atomic():
        t = Datasets(name=dataSetName, source=sourceName)
        t.save()
        dataSetID = t.id
        # Patents.objects.all().delete()
        for index, row, in df.iterrows():
            t = Patents(
                current_assignee=row['CA'],
                publication_numbers=row['PUBLICATION NUMBER'],
                year=row['YEAR'],
                # main_cpc=row['MAIN CPC'],
                cpc=row['CPC'],
                category=row['CATEGORY'],
                # market_segment=row['MARKET SEGMENT'],
                titles=row['TITLES'],
                abstracts=row['ABSTRACTS'],
                independent_claims=row['INDEPENDENT CLAIMS'],
                # main_cpc_description=row['MAIN CPC DESCRIPTION'],
                # cpc_descriptions=row['CPC DESCRIPTIONS'],
                # technical_concepts=row['TECHNICAL CONCEPTS'],
                patent_type=row['TYPE'],
                clean_current_assignees=row['Assignee Group'],
                dataset_id=dataSetID
            )
            t.save()

def insertCPCDescriptions():
    df = pd.read_excel('../in/CPC Descriptions.xlsx')
    # RefCpcDescriptions.objects.all.delete()
    for index, row in df.iterrows():
        t = RefCpcDescriptions(
            cpc=row['CPC'],
            # default_cpc=row['default CPC'],
            # level=int(row['Level']),
            description=row['CPC Description'],
        )
        t.save()

def insertAssigneeKeywords(df):
    with transaction.atomic():
        RefAssigneeKeywords.objects.all().delete()
        for index, row, in df.iterrows():
            t = RefAssigneeKeywords(
                group=row['Group'],
                keywords=row['Keywords'],
            )
            t.save()

def insertCategoryKeywords(df, CategorySetName):
    with transaction.atomic():
        t = CategorySet(
            name=CategorySetName
        )
        t.save()
        categorySetID = t.id
        for index, row, in df.iterrows():
            t = CategorySetKeywords(
                category=row['Category'],
                keywords=row['Keywords'],
                category_set_id=categorySetID
            )
            t.save()

def insertTrainingPatents(df, trainingSetName, classificationName):
    with transaction.atomic():
        t = TrainingDatasets(
            name=trainingSetName,
            classification=classificationName
        )
        t.save()
        trainingSetID = t.id
        for index, row, in df.iterrows():
            t = TrainingPatents(
                titles=row['TITLES'],
                abstracts=row['ABSTRACTS'],
                independent_claims=row['INDEPENDENT CLAIMS'],
                classification=row['CLASSIFICATIONS'],
                training_datasets_id=trainingSetID
            )
            t.save()

# Get functions
def getDataSetPatents(data_set):
    dataSet = Datasets.objects.filter(name=data_set)
    patents = Patents.objects.filter(dataset_id=dataSet[0].id)
    
    df = pd.DataFrame()
    df['ids'] = [d[0] for d in list(patents.values_list('id'))]
    df['Years'] = [d[0] for d in list(patents.values_list('year'))]
    df['Publication Numbers'] = [d[0] for d in list(patents.values_list('publication_numbers'))]
    df['Titles'] = [d[0] for d in list(patents.values_list('titles'))]
    df['Abstracts'] = [d[0] for d in list(patents.values_list('abstracts'))]
    df['Independent Claims'] = [d[0] for d in list(patents.values_list('independent_claims'))]
    technicalConcepts = [d[0] for d in list(patents.values_list('technical_concepts'))]
    df['Technical Concepts'] = catc.stringListToList(technicalConcepts)
    df['Main CPC'] = [d[0] for d in list(patents.values_list('main_cpc'))]
    df['Main CPC Description'] = [d[0] for d in list(patents.values_list('main_cpc_description'))]
    CPCs = [d[0] for d in list(patents.values_list('cpc'))]
    df['CPCs'] = catc.splitLinesToList(CPCs)
    CPCDescriptions = [d[0] for d in list(patents.values_list('cpc_descriptions'))]
    df['CPC Descriptions'] = catc.stringListToList(CPCDescriptions)
    df['Current Assignees'] = [d[0] for d in list(patents.values_list('current_assignee'))]
    df['Predicted Market Segments'] = [d[0] for d in list(patents.values_list('predicted_market_segments'))]
    df['Predicted Topics'] = [d[0] for d in list(patents.values_list('predicted_topic'))]
    df['Types'] = [d[0] for d in list(patents.values_list('patent_type'))]
    
    categories = [d[0] for d in list(patents.values_list('category'))]
    df['Categories'] = catc.stringListToList(categories)
    marketSegments = [d[0] for d in list(patents.values_list('market_segment'))]
    df['Market Segments'] = catc.stringListToList(marketSegments)
    categoryByKeywords = [d[0] for d in list(patents.values_list('category_by_keywords'))]
    df['Category by Keywords'] = catc.stringListToList(categoryByKeywords)
    predictedCategories = [d[0] for d in list(patents.values_list('predicted_categories'))]
    df['Predicted Categories'] = catc.stringListToList(predictedCategories)

    categories = [d[0] for d in list(patents.values_list('category2'))]
    df['Categories2'] = catc.stringListToList(categories)
    categories = [d[0] for d in list(patents.values_list('category3'))]
    df['Categories3'] = catc.stringListToList(categories)
    categories = [d[0] for d in list(patents.values_list('category4'))]
    df['Categories4'] = catc.stringListToList(categories)
    cleanAssignees = [d[0] for d in list(patents.values_list('clean_current_assignees'))]
    df['Clean Assignees List'] = catc.stringListToList(cleanAssignees)
    cleanAssigneesString = [str(d).replace("'", '').replace("[", '').replace("]", '') for d in cleanAssignees]
    df['Clean Assignees'] = cleanAssigneesString
    return df

def getDataSetPatentsBySource(df, sourceName):
    dataSets = Datasets.objects.filter(source=sourceName)
    ids = dates = titles = abstracts = CPCs = assignees = cleanAssignees = types = []
    for dataSet in dataSets:
        patents = Patents.objects.filter(dataset_id=dataSet.id)        
        ids = ids +  [d[0] for d in list(patents.values_list('id'))]
        dates = dates + [d[0] for d in list(patents.values_list('year'))]
        titles = titles +  [d[0] for d in list(patents.values_list('titles'))]
        abstracts = abstracts + [d[0] for d in list(patents.values_list('abstracts'))]
        CPCs = CPCs + [d[0] for d in list(patents.values_list('cpc'))]
        assignees = assignees + [d[0] for d in list(patents.values_list('current_assignee'))]
        cleanAssignees = cleanAssignees + [d[0] for d in list(patents.values_list('clean_current_assignees'))]
        types = types + [d[0] for d in list(patents.values_list('patent_type'))]
    df['ids'] = ids
    df['Dates'] = [str(datetime.datetime.strptime(d, '%B %d, %Y')).replace('-', '').split(' ')[0] for d in dates]
    df['Titles'] = titles
    df['Abstracts'] = abstracts
    df['CPCs'] = catc.splitLinesToList(CPCs)
    df['Types'] = types
    df['Current Assignees'] = assignees
    df['Clean Assignees List'] = catc.stringListToList(cleanAssignees)
    cleanAssigneesString = [str(d).replace("'", '').replace("[", '').replace("]", '') for d in cleanAssignees]
    df['Clean Assignees'] = cleanAssigneesString
    return df

def getDataSetPatentColumn(data_set, df, columnName):
    dataSet = Datasets.objects.filter(name=data_set)
    patents = Patents.objects.filter(dataset_id=dataSet[0].id)
    df['ids'] = [d[0] for d in list(patents.values_list('id'))]
    classes = []
    if(columnName == 'cpc' or columnName == 'clean_current_assignees'):
        for d in list(patents.values_list(columnName)):
            if(d[0]):
                classes.append(d[0].upper())
            else:
                classes.append(None)        
    else:
        for d in list(patents.values_list(columnName)):
            if(d[0]):
                classes.append(d[0].title())
            else:
                classes.append(None)
    stringType = 'lines'
    for c in classes:
        if(c and '[' in c):
            stringType = 'list'
            break
        elif(c and ';' in c):
            stringType = 'semiColon'
            break
    if(stringType == 'list'):
        df[columnName] = catc.stringListToList(classes)
    elif(stringType == 'semiColon'):
        df[columnName] = catc.splitToList(classes, ';')
    else:
        df[columnName] = catc.splitLinesToList(classes)
    return df

def getDataSetPatentYears(data_set, df):
    dataSet = Datasets.objects.filter(name=data_set)
    patents = Patents.objects.filter(dataset_id=dataSet[0].id)    
    df['ids'] = [d[0] for d in list(patents.values_list('id'))]
    df['Years'] = [d[0] for d in list(patents.values_list('year'))]
    # for i in df['Years'].tolist():
    #     print(i)
    #     print(int(float(str(i)[0:4])))
    if(dataSet[0].source == 'orbit'):
        years = [int(float(str(i)[0:4])) if i!='nan' else 0 for i in df['Years'].tolist()]
        df['Years'] = years
    else:
        years = [int(float(str(i)[-4:])) if i!='nan' else 0 for i in df['Years'].tolist()]
        df['Years'] = years
    return df

def getDataSetPatentAssignees(data_set, df):
    dataSet = Datasets.objects.filter(name=data_set)
    patents = Patents.objects.filter(dataset_id=dataSet[0].id)
    df['ids'] = [d[0] for d in list(patents.values_list('id'))]
    df['Current Assignees'] = [d[0] for d in list(patents.values_list('current_assignee'))]
    cleanAssignees = [d[0] for d in list(patents.values_list('clean_current_assignees'))]
    df['Clean Assignees List'] = catc.stringListToList(cleanAssignees)
    cleanAssigneesString = [str(d).replace("'", '').replace("[", '').replace("]", '') for d in cleanAssignees]
    df['Clean Assignees'] = cleanAssigneesString
    return df

def getDataSetPatentTypes(data_set, df):
    dataSet = Datasets.objects.filter(name=data_set)
    patents = Patents.objects.filter(dataset_id=dataSet[0].id)
    df['ids'] = [d[0] for d in list(patents.values_list('id'))]
    df['Types'] = [d[0] for d in list(patents.values_list('patent_type'))]
    return df

def getDataSetPatentCategories(data_set, df):
    dataSet = Datasets.objects.filter(name=data_set)
    patents = Patents.objects.filter(dataset_id=dataSet[0].id)
    df['ids'] = [d[0] for d in list(patents.values_list('id'))]
    categories = [d[0] for d in list(patents.values_list('category'))]
    df['Categories'] = catc.stringListToList(categories)
    return df

def getDataSetPatentPredictedCategories(data_set):
    dataSet = Datasets.objects.filter(name=data_set)
    patents = Patents.objects.filter(dataset_id=dataSet[0].id)
    
    df = pd.DataFrame()
    df['ids'] = [d[0] for d in list(patents.values_list('id'))]
    predictedCategories = [d[0] for d in list(patents.values_list('predicted_categories'))]
    df['Predicted Categories'] = catc.stringListToList(predictedCategories)
    return df

def getDataSetPatentMarketSegments(data_set, df):
    dataSet = Datasets.objects.filter(name=data_set)
    patents = Patents.objects.filter(dataset_id=dataSet[0].id)
    df['ids'] = [d[0] for d in list(patents.values_list('id'))]
    marketSegments = [d[0] for d in list(patents.values_list('market_segment'))]
    df['Market Segments'] = catc.stringListToList(marketSegments)
    return df

def getDataSetPatentCategoryByKeywords(data_set, df):
    dataSet = Datasets.objects.filter(name=data_set)
    patents = Patents.objects.filter(dataset_id=dataSet[0].id)
    df['ids'] = [d[0] for d in list(patents.values_list('id'))]
    categoryByKeywords = [d[0] for d in list(patents.values_list('category_by_keywords'))]
    df['Category by Keywords'] = catc.stringListToList(categoryByKeywords)
    return df

def getDataSetPatentTACs(data_set, df):
    dataSet = Datasets.objects.filter(name=data_set)
    patents = Patents.objects.filter(dataset_id=dataSet[0].id)
    
    df['ids'] = [d[0] for d in list(patents.values_list('id'))]
    df['Titles'] = [d[0] for d in list(patents.values_list('titles'))]
    df['Abstracts'] = [d[0] for d in list(patents.values_list('abstracts'))]
    df['Independent Claims'] = [d[0] for d in list(patents.values_list('independent_claims'))]
    return df

def getDataSetPatentCPCs(data_set, df):
    dataSet = Datasets.objects.filter(name=data_set)
    patents = Patents.objects.filter(dataset_id=dataSet[0].id)
    df['ids'] = [d[0] for d in list(patents.values_list('id'))]
    CPCs = [d[0] for d in list(patents.values_list('cpc'))]
    hasSemiColon = False
    for c in CPCs:
        if(c and ';' in c):
            hasSemiColon = True
            break
    if(hasSemiColon):
        df['CPCs'] = catc.stringToList(CPCs, ';')
    else:
        df['CPCs'] = catc.splitLinesToList(CPCs)
    return df

def getDataSetPatentCPCDescriptions(data_set, df):
    dataSet = Datasets.objects.filter(name=data_set)
    patents = Patents.objects.filter(dataset_id=dataSet[0].id)
    df['ids'] = [d[0] for d in list(patents.values_list('id'))]
    CPCs = [d[0] for d in list(patents.values_list('cpc'))]
    df['CPC Descriptions'] = catc.splitLinesToList(CPCs)
    return df

def getDataSetPatentTechnicalConcepts(data_set, df):
    dataSet = Datasets.objects.filter(name=data_set)
    patents = Patents.objects.filter(dataset_id=dataSet[0].id)
    df['ids'] = [d[0] for d in list(patents.values_list('id'))]
    technicalConcepts = [d[0] for d in list(patents.values_list('technical_concepts'))]
    df['Technical Concepts'] = catc.stringListToList(technicalConcepts)
    return df

def getAllCPCDescription():
    descriptions = RefCpcDescriptions.objects.all()
    df = pd.DataFrame()
    df['cpc'] = [d[0] for d in list(descriptions.values_list('cpc'))]
    df['description'] = [d[0] for d in list(descriptions.values_list('description'))]
    return df

def getAllCategoryKeywords(category_set):
    categorySet = CategorySet.objects.filter(name=category_set)
    categoryKeywords = CategorySetKeywords.objects.filter(category_set_id=categorySet[0].id)
    df = pd.DataFrame()
    df['Group'] = [d[0] for d in list(categoryKeywords.values_list('category'))]
    keywords = [d[0] for d in list(categoryKeywords.values_list('keywords'))]
    keywords = [d.split(', ') for d in keywords]
    finalKeywords = []
    for keywordList in keywords:
        tempKeywordList = []
        for keyword in keywordList:
            if(keyword == keyword and keyword != None and keyword != 'None' and keyword != 'nan'):
                tempKeywordList.append(keyword.lower().lstrip().rstrip())
        finalKeywords.append(tempKeywordList)
    df['Keywords'] = finalKeywords
    return df

def getAllAssigneeKeywords():
    assigneeKeywords = RefAssigneeKeywords.objects.all()
    df = pd.DataFrame()
    df['Group'] = [d[0] for d in list(assigneeKeywords.values_list('group'))]
    keywords = [d[0] for d in list(assigneeKeywords.values_list('keywords'))]
    keywords = [d.split('; ') for d in keywords]
    finalKeywords = []
    for keywordList in keywords:
        tempKeywordList = []
        for keyword in keywordList:
            if(keyword == keyword and keyword != None and keyword != 'None' and keyword != 'nan'):
                tempKeywordList.append(keyword.lower().lstrip().rstrip())
        finalKeywords.append(tempKeywordList)
    df['Keywords'] = finalKeywords
    return df

def getTrainingSetClassification(training_set):
    trainingSet = TrainingDatasets.objects.filter(name=training_set)
    return list(trainingSet.values_list('classification'))[0]

def getTrainingSetPatentClassifications(training_set):
    trainingSet = TrainingDatasets.objects.filter(name=training_set)
    patents = TrainingPatents.objects.filter(training_datasets_id=trainingSet[0].id)
    categories = [d[0] for d in list(patents.values_list('classification'))]
    categories = catc.splitLinesToList(categories)
    allCategories = []
    for categoryList in categories:
        allCategories = allCategories + categoryList
    return list(set(allCategories))

def getTrainingSetPatents(training_set):
    trainingSet = TrainingDatasets.objects.filter(name=training_set)
    patents = TrainingPatents.objects.filter(training_datasets_id=trainingSet[0].id)
    
    df = pd.DataFrame()
    df['ids'] = [d[0] for d in list(patents.values_list('id'))]
    df['Titles'] = [d[0] for d in list(patents.values_list('titles'))]
    df['Abstracts'] = [d[0] for d in list(patents.values_list('abstracts'))]
    df['Independent Claims'] = [d[0] for d in list(patents.values_list('independent_claims'))]
    categories = [d[0] for d in list(patents.values_list('classification'))]
    if(('[' in categories[0] and ']' in categories[0]) or ('(' in categories[0] and ')' in categories[0])):
        df['Categories'] = catc.stringListToList(categories)
    else:
        df['Categories'] = catc.splitLinesToList(categories)

    return df

def getTrainingSetPatents2(training_set):
    trainingSet = TrainingDatasets.objects.filter(name=training_set)
    patents = TrainingPatents.objects.filter(training_datasets_id=trainingSet[0].id)
    
    df = pd.DataFrame()
    df['ids'] = [d[0] for d in list(patents.values_list('id'))]
    df['Titles'] = [d[0] for d in list(patents.values_list('titles'))]
    df['Abstracts'] = [d[0] for d in list(patents.values_list('abstracts'))]
    df['Independent Claims'] = [d[0] for d in list(patents.values_list('independent_claims'))]
    categories = [d[0] for d in list(patents.values_list('classification'))]

    return df

def getClassificationList():
    return [
        'category',
        'predicted_categories',
        'market_segment',
        'cpc',
        'cpc_descriptions',
        'technical_concepts',
        'category_by_keywords',
        'clean_current_assignees',
    ]

def getAssigneeSectorIndustry():
    assignees = Assignees.objects.all()
    assigneeNames = [d[0] for d in list(assignees.values_list('name'))]
    assigneeGroups = [d[0] for d in list(assignees.values_list('group'))]
    assigneeSectors = [d[0] for d in list(assignees.values_list('sector'))]
    assigneeIndustries = [d[0] for d in list(assignees.values_list('industry'))]
    assigneeRanks = [d[0] for d in list(assignees.values_list('rank'))]
    keywords = [d[0] for d in list(assignees.values_list('keywords'))]
    keywords = [d.split('; ') for d in keywords]
    finalKeywords = []
    for keywordList in keywords:
        tempKeywordList = []
        for keyword in keywordList:
            if(keyword == keyword and keyword != None and keyword != 'None' and keyword != 'nan'):
                tempKeywordList.append(keyword.lower().lstrip().rstrip())
        finalKeywords.append(tempKeywordList)
    df = pd.DataFrame()
    df['Assignee Names'] = assigneeNames
    df['Groups'] = assigneeGroups
    df['Sectors'] = assigneeSectors
    df['Industries'] = assigneeIndustries
    df['Ranks'] = assigneeRanks
    df['Assignee Keywords'] = finalKeywords
    return df

# Update functions
def updateCleanCurrentAssignees(data_set, df):
    dataSet = Datasets.objects.filter(name=data_set)
    ids = df['ids']
    assignees = df['Assignee Group']
    for idx, assignee in zip(ids, assignees):
        Patents.objects.filter(dataset_id=dataSet[0].id, id=idx).update(clean_current_assignees=assignee)

def updateCategoryByKeywords(data_set, df):
    dataSet = Datasets.objects.filter(name=data_set)
    ids = df['ids']
    categories = df['Category by Keywords']
    for idx, category in zip(ids, categories):
        Patents.objects.filter(dataset_id=dataSet[0].id, id=idx).update(category_by_keywords=category)

def updateDataSetCategories(data_set, df, publicationNumberColumnName, categoryColumnName):
    df[categoryColumnName] = catc.stringListToList(df[categoryColumnName].tolist())
    dataSet = Datasets.objects.filter(name=data_set)
    publicationNumbers = df[publicationNumberColumnName].tolist()
    categories = df[categoryColumnName].tolist()
    for publicationNumber, category in zip(publicationNumbers, categories):
        Patents.objects.filter(dataset_id=dataSet[0].id, publication_numbers=publicationNumber).update(predicted_categories=category)
        # Patents.objects.filter(dataset_id=dataSet[0].id)

def updateAssigneesRankSectorIndustry(df):
    with transaction.atomic():
        Assignees.objects.all().delete()
        for index, row, in df.iterrows():
            t = Assignees(
                name=row['Name'],
                group=row['Group'],
                keywords=row['Keywords'],
                sector=row['Sector'],
                industry=row['Industry'],
                rank=row['Rank']
            )
            t.save()