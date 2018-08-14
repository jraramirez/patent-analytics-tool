import pandas as pd
import numpy as np
import re

import CategoriesCleaner as catc
import ClaimsCleaner as cc
import ItemSelector as ise
import DBQueries as dbq

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.pipeline import FeatureUnion
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from nltk.corpus import stopwords 
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem import SnowballStemmer
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem.porter import PorterStemmer
from nltk import ngrams
import string

# Function for creating custom confusion matrix 
def getCustomConfusionMatrix(categoriesDF, categoriesColumnName, predictedColumnName):
    uniqueCategories = []
    for c in categoriesDF[categoriesColumnName]:
        if(c and c == c):
            uniqueCategories.extend(c)
    uniqueCategories = list(sorted(set(uniqueCategories)))
    categoryFrequencies = pd.DataFrame(index=uniqueCategories)
    categoryFrequencies['Correct'] = 0
    categoryFrequencies['Incorrect'] = 0
    for index, row in categoriesDF.iterrows():
        if(row[categoriesColumnName] and row[categoriesColumnName] == row[categoriesColumnName]):
            for pc in row[predictedColumnName]:
                if(pc in uniqueCategories):
                    if pc in row[categoriesColumnName]:
                        categoryFrequencies['Correct'][pc] = categoryFrequencies['Correct'][pc] + 1
                    else:
                        categoryFrequencies['Incorrect'][pc] = categoryFrequencies['Incorrect'][pc] + 1
    categoryFrequencies['% Correct'] = categoryFrequencies['Correct']/(categoryFrequencies['Correct'] + categoryFrequencies['Incorrect'])
    return categoryFrequencies

# Function for obtaining a CPC descriptions
def getCPCDescription(CPCs):
    CPCDescriptions = []
    descriptions = dbq.getAllCPCDescription()
    for cpc in CPCs:
        descriptionsString = ''
        finalCPC = (str(cpc)[0:4] + str(cpc)[5:str(cpc).find('/')].replace('0', '') + str(cpc)[str(cpc).find('/')+1:].replace('/', '')).upper()
        description = descriptions.loc[descriptions['cpc'] == finalCPC]['description']
        if(len(description) > 0):
            descriptionsString = description.tolist()[0]
        CPCDescriptions.append(descriptionsString)
    return CPCDescriptions

# Function for obtaining the CPC descriptions
def getCPCDescriptions(df):
    CPCDescriptions = []
    descriptions = dbq.getAllCPCDescription()
    for index, row in df.iterrows():
        descriptionsString = ''
        cpc = row['MAIN CPC']
        finalCPC = str(cpc)[0:4] + str(cpc)[5:str(cpc).find('/')].replace('0', '') + str(cpc)[str(cpc).find('/')+1:].replace('/', '')
        description = descriptions.loc[descriptions['cpc'] == finalCPC]['description']
        if(len(description) > 0):
            descriptionsString = description.tolist()[0]
        CPCDescriptions.append(descriptionsString)
    return CPCDescriptions

# Function for obtaining the CPC descriptions
def getCPCListDescriptions(df):
    CPCDescriptions = []
    descriptions = dbq.getAllCPCDescription()
    for index, row in df.iterrows():
        descriptionsList = []
        descriptionsString = ''
        cpcList = str(row['CPC']).splitlines()
        for cpc in cpcList:
            finalCPC = cpc[0:4] + cpc[5:cpc.find('/')].replace('0', '') + cpc[cpc.find('/')+1:].replace('/', '')
            description = descriptions.loc[descriptions['cpc'] == finalCPC]['description']
            if(len(description) > 0):
                descriptionsString = description.tolist()[0]
            descriptionsList.append(descriptionsString)
        descriptionsString = str(descriptionsList)
        CPCDescriptions.append(descriptionsString)
    return CPCDescriptions

# Function for normalizing documents
def normalizeCorpus(corpus, wordList):
    stop = set(stopwords.words('english'))
    exclude = set(string.punctuation) 
    lemma = WordNetLemmatizer()
    stemmer = PorterStemmer()
    def clean(phrase):
        stop_free = " ".join([i for i in str(phrase).lower().split() if i not in stop])
        punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
        word_free = " ".join([i for i in punc_free.split() if i not in wordList])
        normalized = " ".join(lemma.lemmatize(word) for word in word_free.split())
        stemmed = " ".join(stemmer.stem(word) for word in normalized.split())
        return stemmed.split()
    nomalizedCorpus = [clean(textList) for textList in corpus] 
    return nomalizedCorpus

# Function for normalizing documents
def normalizeCorpusAsStrings(corpus, wordList):
    stop = set(stopwords.words('english'))
    exclude = set(string.punctuation) 
    lemma = WordNetLemmatizer()
    def clean(phrase):
        stop_free = " ".join([i for i in str(phrase).lower().split() if i not in stop])
        punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
        normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())
        word_free = " ".join([i for i in normalized.split() if i not in wordList])
        return word_free
    nomalizedCorpus = [clean(textList) for textList in corpus] 
    return nomalizedCorpus

# Function for classifying patents
def classifyPatents(df, trainDF,
    targetClassificationColumnName, 
    targetTitlesColumnName, 
    targetAbstractsColumnName, 
    targetIndependentClaimsColumnName, 
    targetFeatures, 
    targetTestSize, 
    targetMethod, 
    targetNumberOfEstimators, 
    targetLearningRate, 
    targetNGram1, 
    targetNGram2):
    trainFeaturesDF = pd.DataFrame()
    testFeaturesDF = pd.DataFrame()
    featuresDF = pd.DataFrame()
    originalDF = df.copy()
        
    wordList = []
    f = open('../out/words.txt', 'r')
    for line in f:
        wordList.append(line.rstrip())
    f.close()

    # Filter data
    trainDF = trainDF.dropna(subset=[targetClassificationColumnName])

    if('titles' in targetFeatures):        
        temp = cc.removePublicationNumbers(df[targetTitlesColumnName])
        temp = normalizeCorpusAsStrings(temp, wordList)
        df[targetTitlesColumnName] = cc.remove2LetterWords(temp)
        temp = cc.removePublicationNumbers(trainDF[targetTitlesColumnName])
        temp = normalizeCorpusAsStrings(temp, wordList)
        trainDF[targetTitlesColumnName] = cc.remove2LetterWords(temp)
        # temp = cc.removePublicationNumbers(df[targetTitlesColumnName])
        # temp = cc.removeWords(temp, wordList)
        # temp = cc.removeSpecialCharacters(temp)
        # df[targetTitlesColumnName] = temp
        # temp = cc.removePublicationNumbers(trainDF[targetTitlesColumnName])
        # temp = cc.removeWords(temp, wordList)
        # temp = cc.removeSpecialCharacters(temp)
        # trainDF[targetTitlesColumnName] = temp

    if('abstracts' in targetFeatures):        
        temp = cc.removePublicationNumbers(df[targetAbstractsColumnName])
        temp = normalizeCorpusAsStrings(temp, wordList)
        df[targetAbstractsColumnName] = cc.remove2LetterWords(temp)
        temp = cc.removePublicationNumbers(trainDF[targetAbstractsColumnName])
        temp = normalizeCorpusAsStrings(temp, wordList)
        trainDF[targetAbstractsColumnName] = cc.remove2LetterWords(temp)
        # temp = cc.removePublicationNumbers(df[targetAbstractsColumnName])
        # temp = cc.removeWords(temp, wordList)
        # temp = cc.removeSpecialCharacters(temp)
        # df[targetAbstractsColumnName] = temp
        # temp = cc.removePublicationNumbers(trainDF[targetAbstractsColumnName])
        # temp = cc.removeWords(temp, wordList)
        # temp = cc.removeSpecialCharacters(temp)
        # trainDF[targetAbstractsColumnName] = temp

    if('independentclaims' in targetFeatures):        
        temp = cc.removePublicationNumbers(df[targetIndependentClaimsColumnName])
        temp = normalizeCorpusAsStrings(temp, wordList)
        temp = cc.remove2LetterWords(temp)
        df[targetIndependentClaimsColumnName] = cc.removeDigits(temp)
        temp = cc.removePublicationNumbers(trainDF[targetIndependentClaimsColumnName])
        temp = normalizeCorpusAsStrings(temp, wordList)
        temp = cc.remove2LetterWords(temp)
        trainDF[targetIndependentClaimsColumnName] = cc.removeDigits(temp)
        # temp = cc.removePublicationNumbers(df[targetIndependentClaimsColumnName])
        # temp = cc.removeWords(temp, wordList)
        # temp = cc.removeSpecialCharacters(temp)
        # df[targetIndependentClaimsColumnName] = temp
        # temp = cc.removePublicationNumbers(trainDF[targetIndependentClaimsColumnName])
        # temp = cc.removeWords(temp, wordList)
        # temp = cc.removeSpecialCharacters(temp)
        # trainDF[targetIndependentClaimsColumnName] = temp

    # Split to training and test data
    train, test = train_test_split(trainDF, test_size=float(targetTestSize), random_state=42)
    # train.to_excel('test.xlsx')
    if('titles' in targetFeatures):    
        trainFeaturesDF[targetTitlesColumnName] = train[targetTitlesColumnName]
        testFeaturesDF[targetTitlesColumnName] = test[targetTitlesColumnName]
        featuresDF[targetTitlesColumnName] = df[targetTitlesColumnName]
    if('abstracts' in targetFeatures):
        trainFeaturesDF[targetAbstractsColumnName] = train[targetAbstractsColumnName]
        testFeaturesDF[targetAbstractsColumnName] = test[targetAbstractsColumnName]
        featuresDF[targetAbstractsColumnName] = df[targetAbstractsColumnName]
    if('independentclaims' in targetFeatures):        
        trainFeaturesDF[targetIndependentClaimsColumnName] = train[targetIndependentClaimsColumnName]
        testFeaturesDF[targetIndependentClaimsColumnName] = test[targetIndependentClaimsColumnName]
        featuresDF[targetIndependentClaimsColumnName] = df[targetIndependentClaimsColumnName]
    trainClassificationsDF = pd.DataFrame()
    testClassificationsDF = pd.DataFrame()
    # cleanL2Categories, cleanL3Categories = catc.getL2L3Categories(train[targetClassificationColumnName])
    trainClassificationsDF[targetClassificationColumnName] = train[targetClassificationColumnName]
    # trainClassificationsDF.to_excel('test2.xlsx')
    testClassificationsDF[targetClassificationColumnName] = test[targetClassificationColumnName]

    # Model fitting
    model = None
    if(targetMethod == 'gradientboosting'):
        # model = OneVsRestClassifier(GradientBoostingClassifier(n_estimators=targetNumberOfEstimators, learning_rate=targetLearningRate, max_features=15))
        model = OneVsRestClassifier(GradientBoostingClassifier(
            n_estimators=targetNumberOfEstimators, 
            learning_rate=targetLearningRate, 
            # max_depth=5, 
            # subsample=0.8,
            # min_samples_leaf = 0.05, 
            max_features=15,
            random_state=17))
    elif(targetMethod == 'mlpclassifier'):
        model = OneVsRestClassifier(MLPClassifier(hidden_layer_sizes=(200,), learning_rate='adaptive', verbose=True, solver='lbfgs'))
        # model = MLPClassifier(learning_rate='adaptive', verbose=True, solver='adam')
    else:
        model = OneVsRestClassifier(RandomForestClassifier(n_estimators=targetNumberOfEstimators))

    transformerList = []
    transformerWeights = {}
    if('titles' in targetFeatures):    
        transformerList.append(
            ('titles', Pipeline([
                ('selector', ise.ItemSelector(key=targetTitlesColumnName)),
                ('vectorizer', TfidfVectorizer(stop_words='english', lowercase=True, ngram_range=(targetNGram1, targetNGram2), max_df=0.90)),
                # ('vectorizer', TfidfVectorizer(stop_words='english', lowercase=True, ngram_range=(targetNGram1, targetNGram2))),
        ])))
        transformerWeights['titles'] = 0.2
    if('abstracts' in targetFeatures):
        transformerList.append(
            ('abstracts', Pipeline([
                ('selector', ise.ItemSelector(key=targetAbstractsColumnName)),
                ('vectorizer', TfidfVectorizer(stop_words='english', lowercase=True, ngram_range=(targetNGram1, targetNGram2), max_df=0.90)),
                # ('vectorizer', TfidfVectorizer(stop_words='english', lowercase=True, ngram_range=(targetNGram1, targetNGram2))),
        ])))
        transformerWeights['abstracts'] = 0.2
    if('independentclaims' in targetFeatures):
        transformerList.append(
            ('independent claims', Pipeline([
                ('selector', ise.ItemSelector(key=targetIndependentClaimsColumnName)),
                ('vectorizer', TfidfVectorizer(stop_words='english', lowercase=True, ngram_range=(targetNGram1, targetNGram2), max_df=0.90)),
                # ('vectorizer', TfidfVectorizer(stop_words='english', lowercase=True, ngram_range=(targetNGram1, targetNGram2))),
        ])))  
        transformerWeights['independent claims'] = 0.6
    pipeline = Pipeline([
        ('union', FeatureUnion(
            transformer_list=transformerList,
            transformer_weights=transformerWeights,
        )),
        ('clf', model),
    ])
    mlb = MultiLabelBinarizer()
    Y = mlb.fit_transform(trainClassificationsDF[targetClassificationColumnName])
    pipeline.fit(trainFeaturesDF, Y)
    predicted = pipeline.predict(trainFeaturesDF)
    allCategories = mlb.inverse_transform(predicted)

    # Tag words
    tagWordsDF = pd.DataFrame()
    if(targetMethod == 'mlpclassifier'):
        tagWordsDF = pd.DataFrame()
    else:
        allClasses = []
        allRank = []
        allWords = []
        allImportances = []
        words = []
        for transformer in pipeline.steps[0][1].transformer_list:
            words = words + transformer[1].named_steps['vectorizer'].get_feature_names()
        for c in mlb.classes_:
            if(str(pipeline.named_steps['clf'].estimators_[list(mlb.classes_).index(c)]) == "_ConstantPredictor()"):
                continue
            importances = pipeline.named_steps['clf'].estimators_[list(mlb.classes_).index(c)].feature_importances_
            indices = np.argsort(importances)[::-1]
            for i in range(15):
                word = words[indices[i]]
                importance = importances[indices[i]]
                if(importance):
                    allClasses.append(c)
                    allRank.append(i + 1)
                    allWords.append(word)
                    allImportances.append(importance)
                else:
                    break
        tagWordsDF['Classification'] = allClasses
        tagWordsDF['Rank'] = allRank
        tagWordsDF['Tag Word'] = allWords
        tagWordsDF['Importance'] = allImportances
    
    # Confusion Matrix for training data set
    allCategoriesDF = pd.DataFrame()
    allCategoriesDF[targetClassificationColumnName] = trainClassificationsDF[targetClassificationColumnName]
    allCategoriesDF['Predicted ' + targetClassificationColumnName] = allCategories
    trainConfusionMatrix  = getCustomConfusionMatrix(allCategoriesDF, targetClassificationColumnName, 'Predicted ' + targetClassificationColumnName)
    # Use the model built in train data to the test data
    testConfusionMatrix = None
    if(targetTestSize >0):
        predicted = pipeline.predict(testFeaturesDF)
        allCategories = mlb.inverse_transform(predicted)

        # Confusion Matrix for test data set
        allCategoriesDF = pd.DataFrame()
        allCategoriesDF[targetClassificationColumnName] = testClassificationsDF[targetClassificationColumnName]
        allCategoriesDF['Predicted ' + targetClassificationColumnName] = allCategories
        testConfusionMatrix  = getCustomConfusionMatrix(allCategoriesDF, targetClassificationColumnName, 'Predicted ' + targetClassificationColumnName)

    # Use the model built in train data to all the data
    predicted = pipeline.predict(featuresDF)
    allCategories = mlb.inverse_transform(predicted)
    originalDF['Predicted Classifications'] = allCategories

    return originalDF, tagWordsDF, trainConfusionMatrix, testConfusionMatrix

def categorizeByKeywords(df, keywordsDF, targetFeatures):
    wordList = []
    f = open('../out/words.txt', 'r')
    for line in f:
        wordList.append(line.rstrip())
    f.close()

    categoriesList = []
    keywordsFoundList = []
    weightsList = []
    titles = cc.removePublicationNumbers(df['Titles'])
    normalizedTitles = normalizeCorpus(titles, wordList)
    abstracts = cc.removePublicationNumbers(df['Abstracts'])
    normalizedAbstracts = normalizeCorpus(abstracts, wordList)
    independentClaims = cc.removePublicationNumbers(df['Independent Claims'])
    normalizedIndependentClaims = normalizeCorpus(independentClaims, wordList)

    # for title, abstract, independentClaim in zip(titles, abstracts, independentClaims):
    #     for index, row in keywordsDF.iterrows():
    #         r = re.compile('|'.join(row['Keywords']), re.IGNORECASE)
    #         inTitles = inAbstracts = inIndependentClaims = False
    #         if('titles' in targetFeatures):
    #             inTitles = r.search(title) 
    #         if('abstracts' in targetFeatures):
    #             inAbstracts = r.search(abstract) 
    #         if('independentclaims' in targetFeatures):
    #             inIndependentClaims=  r.search(independentClaim)
    #         if(inTitles or inAbstracts or inIndependentClaims):
    #             categories.append(row['Group'])

    # comparisonsDF = pd.DataFrame()
    # raws = []
    # rawkeywords = []
    # keywords = []
    # strings = []
    # decisions = []
    # for t, title, a, abstract, i, independentClaim in zip(titles, normalizedTitles, abstracts, normalizedAbstracts, independentClaims, normalizedIndependentClaims):
    for title, abstract, independentClaim in zip(normalizedTitles, normalizedAbstracts, normalizedIndependentClaims):
    # for title, abstract, independentClaim, categories in zip(titles, abstracts, independentClaims):
        categories = []
        keywordsFound = []
        weights = []
        keywordsListList = keywordsDF['Keywords'].tolist()
        groups = keywordsDF['Group'].tolist()
        titleSet = [[a] for a in title]
        abstractSet = [[a] for a in abstract]
        independentClaimSet = [[a] for a in independentClaim]
        if('titles' in targetFeatures):
            titlestwograms = ngrams(title, 2)
            titlesthreegrams = ngrams(title, 3)
            titlesfourgrams = ngrams(title, 4)
            titleSet = titleSet + [list(twogram) for twogram in titlestwograms]
            titleSet = titleSet + [list(threegram) for threegram in titlesthreegrams]
            titleSet = titleSet + [list(fourgram) for fourgram in titlesfourgrams]
        if('abstracts' in targetFeatures):
            abstractstwograms = ngrams(abstract, 2)
            abstractsthreegrams = ngrams(abstract, 3)
            abstractsfourgrams = ngrams(abstract, 4)
            abstractSet = abstractSet + [list(twogram) for twogram in abstractstwograms]
            abstractSet = abstractSet + [list(threegram) for threegram in abstractsthreegrams]
            abstractSet = abstractSet + [list(fourgram) for fourgram in abstractsfourgrams]
        if('independentclaims' in targetFeatures):
            independentclaimstwograms = ngrams(independentClaim, 2)
            independentclaimsthreegrams = ngrams(independentClaim, 3)
            independentclaimsfourgrams = ngrams(independentClaim, 4)
            independentClaimSet = independentClaimSet + [list(twogram) for twogram in independentclaimstwograms]
            independentClaimSet = independentClaimSet + [list(threegram) for threegram in independentclaimsthreegrams]
            independentClaimSet = independentClaimSet + [list(fourgram) for fourgram in independentclaimsfourgrams]
        for keywordsList, group in zip(keywordsListList, groups):
            keywordFound = None
            inTitles = inAbstracts = inIndependentClaims = False
            for keyword in keywordsList:
                # if(keyword == keyword and keyword != None and keyword != 'None' and keyword != 'nan'):
                if(keyword == keyword and keyword != None and keyword != 'None' and keyword != 'nan'):
                    keywordSet = keyword.lower().lstrip().rstrip().split()
                    if('titles' in targetFeatures):
                        # if(keyword in t):
                            # raws.append(str(t))
                            # rawkeywords.append(str(keyword))
                            # keywords.append(str(keywordSet))
                            # strings.append(str(titleSet))
                            # b = 'False'
                            # if(keywordSet in titleSet):
                            #     b = 'True'
                            # decisions.append(b)
                        if(keywordSet in titleSet):
                            inTitles = True
                            keywordFound = keyword
                    if('abstracts' in targetFeatures):
                        if(keywordSet in abstractSet):
                            inAbstracts = True
                            keywordFound = keyword
                    if('independentclaims' in targetFeatures):
                        if(keywordSet in independentClaimSet):
                            inIndependentClaims = True
                            keywordFound = keyword
            weight = 0
            if(inIndependentClaims):
                weight = weight + 0.5
            if(inAbstracts):
                weight = weight + 0.5
            if(inTitles):
                weight = weight + 0.5
            if(weight >= 0.5):
                categories.append(group)
                keywordsFound.append(keywordFound)
                weights.append(weight)
            # if(inTitles or inAbstracts or inIndependentClaims):
            #     categories.append(group)
            #     keywordsFound.append(keywordFound)
        categoriesList.append(list(set(categories)))
        keywordsFoundList.append(list(set(keywordsFound)))
        weightsList.append(list(set(weights)))
    # comparisonsDF['Raw Keywords'] = rawkeywords
    # comparisonsDF['Raw Titles'] = raws
    # comparisonsDF['Keywords'] = keywords
    # comparisonsDF['Titles'] = strings
    # comparisonsDF['Decisions'] = decisions
    # comparisonsDF.to_excel('../out/comparisons.xlsx')
    df['Category by Keywords'] = categoriesList
    df['Found Keywords'] = keywordsFoundList
    df['Weights'] = weightsList
    return df

# # Function for obtaining the appropriate group of an assignee
# def getAssgineeGroup(CA, referenceDF):
#     group = CA
#     for index, row in referenceDF.iterrows():
#         contains = []
#         antiWords = []
#         hasContains = False
#         antiWordsFree = True
#         if(row['Contains'] == row['Contains']):
#             contains = str(row['Contains']).split(",")
#         if(row['Does Not Contain'] == row['Does Not Contain']):
#             antiWords = str(row['Does Not Contain']).split(",")
#         for c in contains:
#             if(c.lower().lstrip().rstrip() in CA.lower().lstrip().rstrip()):
#                hasContains = True
#                break
#         for a in antiWords:
#             if(a.lower().lstrip().rstrip() in CA.lower().lstrip().rstrip()):
#                antiWordsFree = False
#                break
#         if(hasContains and antiWordsFree):
#             group = str(row['Assignee']).upper()
#     return group

def assigneeGrouping(df, keywordsDF):
    cleanCAListList = []
    CAListList = catc.splitLinesToList(df['CA'].tolist())
    keywordsListList = keywordsDF['Keywords'].tolist()
    groups = keywordsDF['Group'].tolist()
    for CAList in CAListList:
        updatedCAList = []
        for CA in CAList:
            if(CA and CA!='NAN' and CA!='nan'):
                CAWords = CA.lower().split()
                updatedCA = CA
                for keywordsList, group in zip(keywordsListList, groups):
                    for keyword in keywordsList:
                        for word in CAWords:
                            if(keyword.lower() == word or keyword.lower() == CA.lower()):
                                updatedCA = group
                                break
                updatedCAList.append(updatedCA.upper())
        updatedCAList = list(set(updatedCAList))
        cleanCAListList.append(updatedCAList)
    df['Assignee Group'] = cleanCAListList
    return df

def updateAssigneeGrouping(df, keywordsDF):
    cleanCAListList = []
    CAListList = catc.splitLinesToList(df['Current Assignees'].tolist())
    keywordsListList = keywordsDF['Keywords'].tolist()
    groups = keywordsDF['Group'].tolist()
    for CAList in CAListList:
        updatedCAList = []
        for CA in CAList:
            if(CA and CA!='NAN' and CA!='nan'):
                CAWords = CA.lower().split()
                updatedCA = CA
                for keywordsList, group in zip(keywordsListList, groups):
                    for keyword in keywordsList:
                        for word in CAWords:
                            if(keyword.lower() == word or keyword.lower() == CA.lower()):
                                updatedCA = group
                                break
                updatedCAList.append(updatedCA.upper())
        updatedCAList = list(set(updatedCAList))
        cleanCAListList.append(updatedCAList)
    df['Assignee Group'] = cleanCAListList
    return df

def assignAssigneeSectorIndustry(df, assigneeSectorsIndustries, source):
    sectorList = []
    industryList = []
    CAList = df['Current Assignees'].tolist()
    keywordsListList = assigneeSectorsIndustries['Assignee Keywords'].tolist()
    sectors = assigneeSectorsIndustries['Sectors'].tolist()
    names = assigneeSectorsIndustries['Assignee Names'].tolist()
    industries = assigneeSectorsIndustries['Industries'].tolist()
    for CA in CAList:
        if(CA and CA!='NAN' and CA!='nan'):
            assignedSector = None
            assignedIndustry = None
            if(source == 'orbit'):
                CAWords = CA.lower().split()
                for keywordsList, sector, industry in zip(keywordsListList, sectors, industries):
                    for keyword in keywordsList:
                        for word in CAWords:
                            if(keyword.lower() == word or keyword.lower() == CA.lower()):
                                assignedSector = sector
                                assignedIndustry = industry
                                break
            else:
                for name, sector, industry in zip(names, sectors, industries):
                    if(name.lower() == CA.lower()):
                        assignedSector = sector
                        assignedIndustry = industry
                        break
        sectorList.append(assignedSector)
        industryList.append(assignedIndustry)
    df['Sectors'] = sectorList
    df['Industries'] = industryList
    return df
