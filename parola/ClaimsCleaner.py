import pandas as pd
import numpy as np
import re
# import nltk

# Function for obtaining all the independent claims given the column of all the claims
def getIndependentClaims(claims):

    independentClaimsList = []

    for c in claims:
        if(c is not None and c == c):
            enumeratedClaims = []
            dependentClaims = []
            independentClaims = []
            
            # Remove publication number
            index = str(c).find('\n')
            c = str(c)[index:len(str(c))]
            # Remove unecessary strings
            removeable = [
                '\n'
            ]
            big_regex = re.compile('|'.join(map(re.escape, removeable)))
            c = big_regex.sub("", str(c))

            # For each patent, enumerate and save claims to a new list
            # enumeratedClaims = re.findall(r'\d\.(.*?)(?:\d\.|$)', c, overlapped=True)
            enumeratedClaims = re.findall(r'(\d{1,2}(\.|\:|\-|\)).*?(\.|$|\(canceled\)))', str(c))

            # Classify each claim of each document
            for e in enumeratedClaims:
                e = e[0]
                hasClaim = re.search(r'(claims? \d{1,2}|previous claims?)', e)
                hasParagraph = re.search(r'paragraph \d{1,2}', e)
                if(not hasClaim and not hasParagraph):
                    independentClaims.append(e)
            independentClaimsList.append(independentClaims)
        else:
            independentClaimsList.append('')
    return independentClaimsList

# Function for obtaining all the dependent claims given the column of all the claims
def getDependentClaims(claims):

    dependentClaimsList = []

    for c in claims:
        if(c is not None and c == c):
            enumeratedClaims = []
            dependentClaims = []

            # Remove publication number
            index = str(c).find('\n')
            c = c[index:len(str(c))]
            # Remove unecessary strings
            removeable = [
                '\n'
            ]
            big_regex = re.compile('|'.join(map(re.escape, removeable)))
            c = big_regex.sub("", str(c))

            # For each patent, enumerate and save claims to a new list
            # enumeratedClaims = re.findall(r'\d\.(.*?)(?:\d\.|$)', c, overlapped=True)
            enumeratedClaims = re.findall(r'(\d{1,2}(\.|\:|\-|\)).*?(\.|$|\(canceled\)))', str(c))

            # Classify each claim of each document
            count=0
            for e in enumeratedClaims:
                e = e[0]
                hasClaim = re.search(r'(claims? \d{1,2}|previous claims?)', e)
                hasParagraph = re.search(r'paragraph \d{1,2}', e)
                if(hasClaim or hasParagraph):
                    dependentClaims.append(e)
                count=count+1
            dependentClaimsList.append(dependentClaims)
        else:
            dependentClaimsList.append('')
    return dependentClaimsList

# Function for removing list of words from a list of strings
def removeWords(strings, wordList):
    cleanedStringsList = []

    for s in strings:
        # Remove words enumerated in wordList
        big_regex = re.compile('|'.join(map(re.escape, wordList)), re.IGNORECASE)
        c = big_regex.sub("", str(s))
        cleanedStringsList.append(c)

    return cleanedStringsList

#Function for removing 2 letter words
def remove2LetterWords(strings):
    cleanedStringsList = []

    for s in strings:
        s = re.sub(r'\b\w{1,2}\b', '', str(s))
        cleanedStringsList.append(s)

    return cleanedStringsList

# Function for removing non-alphanumeric characters
def removeSpecialCharacters(strings):
    cleanedStringsList = []

    for s in strings:
        s = re.sub(r'([^\s\w]|_)+', ' ', str(s))
        cleanedStringsList.append(s)

    return cleanedStringsList

# Function for removing digits from a list of strings
def removeDigits(strings):
    cleanedStringsList = []

    for s in strings:
        s = ''.join([i for i in s if not i.isdigit()])
        cleanedStringsList.append(s)
    return cleanedStringsList

# Function for removing publication numbers from a list of strings
def removePublicationNumbers(strings):
    cleanedStringsList = []
    for s in strings:
        if(s and s == s):
            index = str(s).find('\n')
            if(index):
                c = str(s)[index+1:len(str(s))]
                cleanedStringsList.append(c)
            else:
                cleanedStringsList.append(s)
        else:
            cleanedStringsList.append('')
    return cleanedStringsList

# Function for obtaining the relevance scores of technical concepts
def getConceptRelevances(strings):
    conceptRelevancesList = []
    for t in strings:
        if(t):
            conceptsList = t.splitlines()
            conceptsAndRelevances = []
            for c in conceptsList:
                if(re.search(r'\((.*?)\,', c)):
                    r = re.search(r'\((.*?)\,', c).group(1)
                    c = re.sub(r'\([^)]*\)', '', c)
                    conceptsAndRelevances.append((c, r))
            conceptRelevancesList.append(conceptsAndRelevances)
        else:
            conceptRelevancesList.append('')
    return conceptRelevancesList

# Function for removing postfixes technical concepts
def removeConceptPostfix(strings):
    cleanTechnicalConcepts = []
    for t in strings:
        if(t and t == t):
            t = re.sub(r'\([^)]*\)', '', t)
            cleanTechnicalConcepts.append(str(t))
        else:
            cleanTechnicalConcepts.append('')
    return cleanTechnicalConcepts

# Function for obtaining the technical concepts
def getTechnicalConcepts(strings):
    cleanTechnicalConcepts = []

    for t in strings:
        if(t and t == t):
            conceptsList = t.splitlines()
            cleanTechnicalConcepts.append(conceptsList)
        else:
            cleanTechnicalConcepts.append('')
    return cleanTechnicalConcepts 

# Function for obtaining the top technical concepts based on a threshold
def getTopTechnicalConcepts(strings):
    topTechnicalConcepts = []

    for t in strings:
        if(t):
            filteredConceptsList = []
            conceptsList = t.splitlines()
            for c in conceptsList:
                if(re.search(r'\((.*?)\,', c)):
                    r = re.search(r'\((.*?)\,', c).group(1)
                    c = re.sub(r'\([^)]*\)', '', c)
                    if(int(r)>50):
                        filteredConceptsList.append(c)
            filteredConceptsList.sort()
            topTechnicalConcepts.append(filteredConceptsList)
        else:
            topTechnicalConcepts.append(None)
    return topTechnicalConcepts 

# Function for obtaining the N most common technical concepts
def getNCommonTechnicalConcepts(strings, n):
    nCommonTechnicalConcepts = []
    allConcepts = []

    conceptFrequencies = pd.DataFrame()
    conceptFrequencies['Frequency'] = 0

    iteration = 0
    for cs in strings:
        for c in cs:
            if(c and c == c):
                if(c in conceptFrequencies.index):
                    conceptFrequencies.loc[c, 'Frequency'] = conceptFrequencies.loc[c, 'Frequency'] + 1
                else:
                    conceptFrequencies.loc[c, 'Frequency'] = 1
                if(iteration%2000 == 0):
                    conceptFrequencies.drop(conceptFrequencies[conceptFrequencies['Frequency'] == 1].index, inplace=True)
                    print(len(conceptFrequencies.index))
                iteration = iteration + 1

    nCommonTechnicalConcepts = conceptFrequencies.sort_values(by=['Frequency'], ascending=False)
    return nCommonTechnicalConcepts.head(n=n)

# Function for obtaining the relevance of the N most common technical concepts
def getCommonTechnicalConceptsRelevance(conceptRelevances, nCommonTechnicalConcepts):
    commonTechnicalConceptsRelevance = []
    commonTechnicalConcepts = list(nCommonTechnicalConcepts.index)
    for cr in conceptRelevances:
        if(cr):
            conceptsAndRelevances = []
            for c in cr:
                if(c[0] in commonTechnicalConcepts):
                    conceptsAndRelevances.append((c[0], c[1]))
            commonTechnicalConceptsRelevance.append(conceptsAndRelevances)
    return commonTechnicalConceptsRelevance

# Function for obtaining the technical concepts as strings
def getTechnicalConceptsAsString(strings):
    stringTechnicalConcepts = []
    for s in strings:
        if(s):
            tcString = ''
            for tc in s:
                tcString = tcString + ' ' + str(tc)
            stringTechnicalConcepts.append(tcString)
        else:
            stringTechnicalConcepts.append('')
    return stringTechnicalConcepts

# Function for obtaining the type of document
def getDocumentTypes(publicationNumbers, pLength):
    documentTypes = []
    for pn in publicationNumbers:
        if(pn):
            dType = 'PA'
            pns = pn.splitlines()
            for p in pns:
                if(len(p) == pLength or ',' in p):
                    dType = 'P'
            documentTypes.append(dType)
        else:
            documentTypes.append(None)
    return documentTypes

# Function for obtaining the Publication number found at the start of strings
def getPublicationNumber(string):
    publicationNumber = ''
    ss = string.splitlines()
    if(len(ss) > 1):
        publicationNumber = ss[0][1:-1]
    return publicationNumber

# Function for identifying type of documents with special cases
def identifySpecialCases(df, titleColumnName, abstractColumnName, independentClaimColumnName):
    types = list(df['Type'])
    i = 0
    for index, row in df.iterrows():
        found = False
        titlePublicationNumber = getPublicationNumber(str(row[titleColumnName]))
        abstractPublicationNumber = getPublicationNumber(str(row[abstractColumnName]))
        if(titlePublicationNumber == abstractPublicationNumber):
            found = False
            icLines = str(row[independentClaimColumnName]).splitlines()
            for index, ic in enumerate(icLines):
                if(ic[1:-1] == titlePublicationNumber):
                    found = True
            if(not found):
                types[i] = '?'
        i = i + 1
    return types

def matchIndependentClaimPNtoPNs(df, publicationNumberColumnName, independentClaimColumnName):
    matches = []
    for index, row in df.iterrows():
        match = 'N'
        independentClaimPN = getPublicationNumber(row[independentClaimColumnName])
        pns = row[publicationNumberColumnName].splitlines()
        if(len(independentClaimPN) == 13):
            independentClaimPN = independentClaimPN[0:6] + independentClaimPN[7:]
        if(str(independentClaimPN) == str(pns[-1])):
            match = 'Y'
        print(independentClaimPN + ' ' + pns[-1] + ' ' + match)
        matches.append(match)
    return matches

# Function for obtaining the latest idependent claims based on publication numbers
def getLatestIndependentClaims(df, titleColumnName, abstractColumnName, independentClaimColumnName):
    latestIndependentClaims = []
    for index, row in df.iterrows():
        found = False
        titlePublicationNumber = getPublicationNumber(str(row[titleColumnName]))
        abstractPublicationNumber = getPublicationNumber(str(row[abstractColumnName]))
        if(titlePublicationNumber == abstractPublicationNumber):
            newIndependentClaims = row[independentClaimColumnName]
            icLines = str(row[independentClaimColumnName]).splitlines()
            for index, ic in enumerate(icLines):
                if(ic[1:-1] == titlePublicationNumber):
                    newIndependentClaims = '\n'.join(icLines[index:])
                    break
            latestIndependentClaims.append(newIndependentClaims)
    return latestIndependentClaims

# Function for obtaining the preambles of independent claims
def getPreamblesOfIndependentClaims(strings):
    preamblesOfIndependentClaims = []
    for ic in strings:
        if(ic):
            preambles = []
            icLines = str(ic).splitlines()
            for c in icLines:
                if('comprising' in c):
                    preambles.append(c[:c.index('comprising')+10])
                elif('comprising:' in c):
                    preambles.append(c[:c.index('comprising:')+11])
                else:
                    preambles.append(c)
            preambles = '\n'.join(preambles)
            preamblesOfIndependentClaims.append(preambles)
        else:
            preamblesOfIndependentClaims.append(None)
    return preamblesOfIndependentClaims

# # Function for obtaining the nouns
# def getNouns(strings):
#     nounsList = []
#     for s in strings:
#         s = nltk.word_tokenize(s)
#         nounsString = ''
#         posResult = nltk.pos_tag(s)
#         for p in posResult:
#             if(p[1] == 'NN'):
#                 nounsString = nounsString + ' ' + p[0]
#         nounsList.append(nounsString)
#     return nounsList

def getPublicationNumbers(strings):
    publicationNumbers = []
    for s in strings:
        pns = []
        if(s):
            pns = str(s).splitlines()
        publicationNumbers.append(pns)
    return publicationNumbers

# Function for obtaining the clean version of CPCs
def getCPCs(strings):
    CPCList = []
    CPC4List = []
    for s in strings:
        if(s):
            CPCs = []
            CPC4s = []
            sLines = str(s).splitlines()
            for CPC in sLines:
                if('/' in CPC):
                    tempCPC = CPC.split('/')[0]
                    CPCs.append(tempCPC)
                    CPC4s.append(tempCPC[0:4])
            CPCs = list(set(CPCs))
            CPC4s = list(set(CPC4s))
            CPCList.append(CPCs)
            CPC4List.append(CPC4s)
        else:
            CPCList.append(None)
            CPC4List.append(None)
    return CPCList, CPC4List

# Function for obtaining the clean version of CPCs
def getCPCL2s(strings):
    CPCList = []
    for s in strings:
        if(s):
            CPCs = []
            sLines = str(s).splitlines()
            for CPC in sLines:
                if('/' in CPC):
                    tempCPC = CPC.split('/')[0] + '/' + CPC.split('/')[1]
                    CPCs.append(tempCPC)
            CPCs = set(CPCs)
            CPCList.append(CPCs)
        else:
            CPCList.append(None)
    return CPCList

# Function for obtaining the clean version of CPCs
def getCPCAll(strings):
    CPCList = []
    for s in strings:
        if(s):
            CPCs = []
            sLines = str(s).splitlines()
            CPCList.append(sLines)
        else:
            CPCList.append(None)
    return CPCList

def cleanAssignees(strings):
    cleanedAssginees = []
    for s in strings:
        assignees = []
        if(s):
            assignees = str(s).splitlines()
        cleanedAssginees.append(assignees)
    return cleanedAssginees