import pandas as pd

# Obtain a json data from a result of crosstab using one column
def getCrossTabInput(df, columnName1, columnName2, targetN):
    counts = pd.crosstab(df[columnName1], [df[columnName2]], margins=True).sort_values(by=['All'], ascending=False).reset_index()
    counts = counts.drop(['All'], axis=1).drop([0]).head(targetN)
    counts = counts.rename(index=str, columns={
        columnName1: "Categories"
    })
    json = counts.to_json(orient="index")
    return json

# Obtain a json data from a result of groupby using one column
def getGroupByInput(df, columnName, countColumnName):
    counts = df.groupby([columnName]).size().reset_index(name=countColumnName)
    json = counts.to_json(orient="index")
    return json

# Obtain a json data from a result of groupby using one column
def getGroupByInput2(df, columnName1, columnName2, countColumnName):
    counts = df.groupby([columnName1, columnName2]).size().reset_index(name=countColumnName)
    json = counts.to_json(orient="index")
    return json
