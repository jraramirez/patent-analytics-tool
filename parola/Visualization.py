import pandas as pd
import numpy as np
import re
import ast

# Function for obtaining the N most common technical concepts
def getTopNNodes(strings, n):
    allNodes = []
    for nList in strings:
        if(nList == nList):
            for node in set(nList):
                allNodes.append(node)
    expandedDF = pd.DataFrame()
    expandedDF['allNodes'] = allNodes
    grouped = expandedDF.groupby(['allNodes']).size().reset_index(name='counts')
    topNNodes = grouped.nlargest(n, 'counts')['allNodes'].tolist()
    return topNNodes
