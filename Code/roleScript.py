# -*- coding: utf-8 -*-
"""
Created on Tue Sep 18 18:55:15 2018

@author: Stephen Downhower

Input: Query
Output: matchId, partId, role dataframe
"""
# Constants
queryFilename = "ScriptQuery.txt"

# The query collects heartbeat data up to this endTime; Make sure to update the
#   number in the query text file if you change it here
endTime = 6;

# Import Statements
import pandas as pd
from sqlalchemy import create_engine

def query(queryFilePath = queryFilename):
    '''Query the match heartbeat data for times before endTime with SQL'''
    
    # Creates the connection to the DB
    engine = create_engine('mysql+pymysql://LOLMegaRead:'+'LaberLabsLOLquery'+'@lolsql.stat.ncsu.edu/lol')
    
    # Query straight into pandas data frame
    with open(queryFilePath, 'r') as myfile:
        queryCommand = myfile.read().replace('\n', ' ')
        
    data = pd.read_sql(queryCommand, engine)
    return data

def roleFinder(test = ""):
    '''Creates a DataFrame containing roles for all matches queried'''
    # Query the data, and add a teamId column using the addTeam() function
    data = query()
    data['teamId'] = data.apply(addTeam, axis = 1) # 1 = Blue, 2 = Red

    # Determine max jgMinionsKilled by each team, and assign the team member
    #   with the max jgMinionsKilled the JNG role

    jngData = pd.DataFrame(data.groupby(['matchId','teamId'])['jungleMinionsKilled'].max()).reset_index()
    jngData['role'] = 'JNG' 
    tempData = data[data['timestamp_minute']==6]    
    
    # Filter out matches where no jungle minions were killed at endTime (i.e, 
    #   filtering out where jungler is afk)
    matchErrors = jngData[jngData['jungleMinionsKilled'] == 0]['matchId']
    jngData = jngData[~jngData['matchId'].isin(matchErrors)]
    data = data[~data['matchId'].isin(matchErrors)]
    
    # Catches any errors that occur when joining to tempData
    try: 
        tempData = tempData.merge(jngData, how = 'inner')
    except Exception as inst:
        print(type(inst))
        print("Error occurred when when joining on the following role: JNG")
    
    # Update data; Filter newData by null role values (removes JNG)
    data = data.merge(tempData[['matchId','participantId','role']], how = 'left', on = ['matchId', 'participantId'])
    newData = data[pd.isnull(data.role)]
    
    # Determine and Remove Supports
    tempData = newData[newData['timestamp_minute']==6]
    tempData = tempData.drop(columns = ['role'])
    supData = pd.DataFrame(tempData.groupby(['matchId','teamId'])['minionsKilled'].min()).reset_index()
    supData['role'] = 'SUP'
    
    # Catches any errors that occur when joining to tempData
    try: 
        tempData = tempData.merge(supData, how = 'inner')
    except Exception as inst:
        print(type(inst))
        print("Error occurred when when joining on the following role: SUP")

    # Update data; Filter newData by null role values (removes SUP)
    data = updateData(data, tempData)
    newData = data[pd.isnull(data.role)]

    # Determine average y position of each participant; Determine the max 
    #   average y position on each team, and assign that member the TOP role
    avgY = pd.DataFrame(newData.groupby(['matchId', 'teamId','participantId'])['positiony'].mean()).reset_index()
    maxY = pd.DataFrame(avgY.groupby(['matchId','teamId'])['positiony'].max()).reset_index()
    maxY['role'] = 'TOP'
    
    # Catches any errors that occur when joining to tempData
    try: 
        tempData = avgY.merge(maxY, how = 'inner')
    except Exception as inst:
        print(type(inst))
        print("Error occurred when when joining on the following role: TOP")
    
    # Update data; Filter newData by null role values (removes TOP)
    data = updateData(data, tempData)
    newData = data[pd.isnull(data.role)]
    
    # Determine average y position of each participant; Determine the max 
    #   average y position on each team, and assign that member the MID role
    avgY = pd.DataFrame(newData.groupby(['matchId', 'teamId','participantId'])['positiony'].mean()).reset_index()
    maxY = pd.DataFrame(avgY.groupby(['matchId','teamId'])['positiony'].max()).reset_index()
    maxY['role'] = 'MID'

    # Catches any errors that occur when joining to tempData
    try: 
        tempData = avgY.merge(maxY, how = 'inner')
    except Exception as inst:
        print(type(inst))
        print("Error occurred when when joining on the following role: MID")
    
    # Update data; Fill remaining null role values with ADC
    data = updateData(data,tempData)
    data['role'] = data['role'].fillna('ADC')
    
    # Prepare and return the output table with matchId, partId, and role
    data = data[data['timestamp_minute']==1]
    finalData = data[['matchId','participantId','role']]
    if test == "hb":
        return data
    return finalData
    
def addTeam(row):
    '''Identifies teamId depending on the participantId of a given row'''
    # Assigns participantIds 1 thorugh 5 a value of 1 (Blue team)
    # Assigns participantIds 6 through 10 a value of 2 (Red team)
    if row['participantId'] <= 5:
        val = 1
    else:
        val = 2
        
    return val

def updateData(data, tempData):
    '''Updates the main dataFrame after a role is determined in RoleFinder()'''
    # Left joins the tempData to the data; Combines the role_x and role_y 
    #   columns into a single role column, and drops the role_x and role_y 
    #   columns
    data = data.merge(tempData[['matchId','participantId','role']],how='left',on=['matchId','participantId'])
    data['role'] = data['role_x'].fillna(data['role_y'])
    data = data.drop(columns = ['role_x','role_y'])
    
    return data