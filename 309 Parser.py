# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 09:41:34 2019

@author: Megan.Francis
"""


import pandas as pd
import re
import qpool as qp
import math

#This regex will capture all those columns of data in the 309

too_short = '(\n\s{2}[A-Z,0-9,#][A-Z,0-9,\-,,,&, ,.,#]{23}\s{2}[A-Z,0-9][A-Z,0-9,\-,,,&, ,.,#]{23}\s{2}[A-Z,0-9][A-Z,0-9,\-,,,&, ,.,#]{23}\s{2}[A-Z,0-9][A-Z,0-9,\-,,,&, ,.,#]{23}\s{2}[A-Z,0-9][A-Z,0-9,\-,,,&, ,.,#]{1,11})'

def read_data(filename):
    with open(file) as f:
        data = f.read()
        
    return data[1:]

def get_loan_columns(data):
    column_row = '(\n\s?\s{2}[A-Z,0-9][A-Z,0-9,\-,,,&, ,.,#]{23}\s{2}[A-Z,0-9][A-Z,0-9,\-,,,&, ,.,#]{23}\s{2}[A-Z,0-9][A-Z,0-9,\-,,,&, ,.,#]{23}\s{2}[A-Z,0-9][A-Z,0-9,\-,,,&, ,.,#]{23}\s{2}[A-Z,0-9][A-Z,0-9,\-,,,&, ,.,#]*)'
    columns = ''.join(re.findall(column_row,data))
    loan_columns = re.split('\s?\s{2}CLIENT-NO[A-Z,0-9, ,-]{15}',columns)
    
    return loan_columns[1:]


def get_headers():
    headers = []
    split = loan_columns[0].split('\n')
    for item in split:
        i = math.floor(len(item)/26)
        for int in range(0,i):
            start = int * 26 + 2
            end = int * 26 + 14 +1
            headers.append(item[start:end].strip())
        
    return headers
    
def write_columns():
    loan_columns = get_loan_columns(data)
    columns = pd.DataFrame()
    i = 0
    for loan in loan_columns:
        split = loan_columns[i].split('\n')
        for item in split:
            j = math.floor(len(item)/26) + 1
            for int in range(0,j):
                start = int * 26 + 2
                end = int * 26 + 14 +1
                columns.loc[i,item[start:end].strip()] = item[start + 13:end + 13].strip()
        i = i + 1
        
    return columns

#def write_tax():
    
    

#def get_change_history():

file = input("Where is the 309?")
data = read_data(file)

