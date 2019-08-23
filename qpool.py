# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 08:36:26 2019

@author: Megan.Francis
"""

import pandas as pd
import pyodbc as pyo

def get_conn():
    conn = pyo.connect('DSN=BoardingServerTest;Trusted_Connection=yes;')
        
    return conn

def get_data(pool, stage, fields):
    data = pd.DataFrame()
    conn = get_conn()
    query = 'SELECT ' + fields + 'FROM Pool' + pool + '..Boardingtape_' + stage 
    data = pd.read_sql(query,conn)
    conn.close()
    
    return data

def get_prod_data(fields, loan_list):
    data = pd.DataFrame()
    conn = get_conn()
    query = 'SELECT ' + fields + ' FROM MARS..vw_loans WHERE Account IN (' + loan_list + ')'
    data = pd.read_sql(query,conn)
    conn.close()
    
    return data

def get_delta(pool, stages, fields):
    data = pd.DataFrame()
    conn = get_conn()
    query = 'SELECT ' + fields + 'FROM Pool' + pool + '..Boardingtape_' + stages[0] # + write alias
    for stage in stages:
        query = query + 'LEFT JOIN (SELECT ' + fields + 'FROM Pool' + pool + '..Boardingtape_' + stage[1:] + ') as ' # + write alias and join on account 
    data = data.append(pd.read_sql(query,conn))
    conn.close()
    
    return data