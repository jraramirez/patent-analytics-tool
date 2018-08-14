import pandas as pd
import re
import ast

# Function for obtaining the clean version of L1 categories
def getL1Categories(categories):
    cleanL1Categories = []

    for c in categories:
        if(c):
            l1List = []
            templ1List = str(c).splitlines()
            for tl1c in templ1List:
                if(tl1c):
                    if('/' in tl1c):
                        tl1c = tl1c.split('/')[0]
                    if(str(tl1c.lower().rstrip().lstrip()) != '' and str(tl1c.lower().rstrip().lstrip()) != 'nan'):
                        l1List.append(str(tl1c.lower().rstrip().lstrip()))
                        l1List = list(set(l1List))
            cleanL1Categories.append(l1List)
        else:
            cleanL1Categories.append(None)
    return cleanL1Categories

def stringListToList(data):
    cleanData = []

    for d in data:
        if (d and d != '[]'):
            dataList = []
            for item in ast.literal_eval(d):
                if(item != '' and item != ' '):
                    dataList.append(item.rstrip().lstrip())
            cleanData.append(list(set(dataList)))
        else:
            cleanData.append(None)
    return cleanData

# Function for obtaining the list version of line separated data
def splitLinesToList(data):
    cleanData = []

    for d in data:
        if(d):
            dataList = []
            tempDataList = str(d).splitlines()
            for item in tempDataList:
                if(item != '' or item != 'nan' or item != ' '):
                    dataList.append(item.rstrip().lstrip())
            cleanData.append(list(set(dataList)))
        else:
            cleanData.append(None)
    return cleanData

# Function for obtaining the list version of line separated data
def splitToList(data, separator):
    cleanData = []

    for d in data:
        if(d):
            dataList = []
            tempDataList = str(d).split(separator)
            for item in tempDataList:
                if(item != '' or item != 'nan' or item != ' '):
                    dataList.append(item.rstrip().lstrip())
            cleanData.append(list(set(dataList)))
        else:
            cleanData.append(None)
    return cleanData

# Function for obtaining the clean version of L1 and L2 categories
def getL2L3Categories(categories):
    cleanL2Categories = []
    cleanL3Categories = []

    for c in categories:
        if(c):
            l2List = []
            l3List = []
            tempList = str(c).splitlines()
            for tlc in tempList:
                if(tlc):
                    if('/' in tlc):
                        if(len(tlc.split('/'))>1):
                            tl1c = tlc.split('/')[0]
                            tl2c = tlc.split('/')[1]
                            l2List.append(tl1c.lower().rstrip().lstrip() + '/'+tl2c.lower().rstrip().lstrip())
                        if(len(tlc.split('/'))>2):
                            tl1c = tlc.split('/')[0]
                            tl2c = tlc.split('/')[1]
                            tl3c = tlc.split('/')[2]
                            l3List.append(tl1c.lower().rstrip().lstrip() + '/' + tl2c.lower().rstrip().lstrip() + '/' + tl3c.lower().rstrip().lstrip())
            l2List = list(set(l2List))
            l3List = list(set(l3List))
            cleanL2Categories.append(l2List)
            cleanL3Categories.append(l3List)
        else:
            cleanL2Categories.append([])
            cleanL3Categories.append([])
    return cleanL2Categories, cleanL3Categories

# Function for obtaining the clean version of L1, L2, and L3 categories
def getCleanL1L2L3Categories(categories):
    cleanCategories = []

    for c in categories:
        if(c):
            cList = []
            tempList = []
            cList = str(c).splitlines()
            cList = list(filter(lambda a: a != '', cList))
            for c in cList:
                slashIndices = [i for i, x in enumerate(c) if x == '/']
                for i in slashIndices:
                    if(c[i-1] == ' '):
                        c = c[:i-1] + c[i:]
                    if(c[i+1] == ' '):
                        c = c[:i+1] + c[i+2:]
                tempList.append(c.lower().rstrip().lstrip())
            tempList = list(set(tempList))
            cleanCategories.append(tempList)
        else:
            cleanCategories.append(None)
    return cleanCategories

# Function for obtaining the clean version of L1 categories
def getMarketSegments(marketSegments):
    cleanMarketSegments = []

    for ms in marketSegments:
        if(ms):
            msList = []
            msList = str(ms).splitlines()
            msList = list(set(filter(lambda a: a != '', msList)))
            cleanMarketSegments.append(msList)
        else:
            cleanMarketSegments.append(None)
    return cleanMarketSegments
