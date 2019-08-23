# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 07:26:17 2019

@author: Megan.Francis
"""

import pandas as pd
import re
import qpool as qp

#Sections_re contains a list of regular expressions for known section names in the 5-SB
page_breaks_re = ['\n ------------------------------------------------------------------------------------------------------------------------------------',
            '\n                                                                    BALANCES:          SUSPENSE:      DUE DATE:         CORP ADV:',
            '\n LOAN NO.         MORT NAME     BK  INV  LN        PRINCIPAL         ESCROW              MSP            LOAN            NONRECOV',
            '\n   CASE NO           REGION     CH  MAN  TP        BALANCE       PRE-PET UNPAID         DEBTOR        POST-PET         MTGR RECOV',
            '\n NEW SERV LOAN NO             PROCESSOR                   ATTORNEY                      TRUSTEE                      3RD PTY RECOV',
            '\n?\d?S\d{4}-5SB\s*[A-Z, ]*\s*(\d\d/?){3}',
            '\n LN SERV SOLD ID [A-Z,0-9, ]*\s*SERVICING TRANSFER BANKRUPTCY TRIAL BALANCE \s?FOR GREGORY FUNDING LLC\s*PAGE\s*\d*',
            '\n?0?[A-Z, ]*TOTAL\s*\d*\s*[0-9,,,.]*\s*[0-9,,,.]*-\s*[0-9,,,.]*\s*NONRECOV:\s*[0-9,,,.]*',
            '\n\s*[0-9,,,.]*\s*[0-9,,,.]*\s*MTGR RECOV:\s*[0-9,,,.]*',
            '\n\s*[0-9,,,.]*\s*[0-9,,,.]*\s*3RD PTY RECOV:\s*[0-9,,,.]*']

def read_data(filename):
    with open(file) as f:
        data = f.read()
    return data[1:]

def get_loans(data):
    for item in page_breaks_re:
        data = re.sub(item,'',data)
    loans = data.split('\n0')  
    return loans[1:]

def get_extract(loan_data):
    extract = pd.DataFrame(columns = ['OldLoanNumber','Case Number','Chapter'])
    i =  0
    for loan in loan_data:
        extract.loc[i,'OldLoanNumber'] = loan[1:10]
        extract.loc[i,'Case Number'] = loan[135:144]
        extract.loc[i,'Chapter'] = loan[31:33]
        i = i + 1
        
    return extract    

def get_comm(loan_data, pool, stage, fields):
    comm = pd.DataFrame(columns = ['Account','Case Number','Chapter','Filing State','Filing District','POC Filed Date','TIN','First Name','MI','Last Name','CB First Name','CB MI','CB Last Name','Property Street','Property City','Property State','Property Zip'])
    borrower_data = qp.get_data(pool, stage, fields).set_index('OldLoanNumber')
    i =  0
    for loan in loan_data:
        comm.loc[i,'Account'] = borrower_data.loc[loan[0:10],'Account']
        comm.loc[i,'Case Number'] = loan[135:144]
        comm.loc[i,'Chapter'] = loan[31:33]
        comm.loc[i,'TIN'] = borrower_data.loc[loan[0:10],'TIN']
        comm.loc[i,'First Name'] = borrower_data.loc[loan[0:10],'FirstName']
        comm.loc[i,'MI'] = borrower_data.loc[loan[0:10],'MI']
        comm.loc[i,'Last Name'] = borrower_data.loc[loan[0:10],'LastName']
        comm.loc[i,'CB TIN'] = borrower_data.loc[loan[0:10],'CB_TIN']
        comm.loc[i,'CB First Name'] = borrower_data.loc[loan[0:10],'CB_FirstName']
        comm.loc[i,'CB MI'] = borrower_data.loc[loan[0:10],'CB_MI']
        comm.loc[i,'CB Last Name'] = borrower_data.loc[loan[0:10],'CB_LastName']
        comm.loc[i,'Property Street'] = borrower_data.loc[loan[0:10],'Street']
        comm.loc[i,'Property City'] = borrower_data.loc[loan[0:10],'City']
        comm.loc[i,'Property State'] = borrower_data.loc[loan[0:10],'State']
        comm.loc[i,'Property Zip'] = borrower_data.loc[loan[0:10],'ZipCode']
        i = i + 1
        
    return comm.drop_duplicates()        

file = input("Where is the 5-SB?")
data = read_data(file)
loan_data = get_loans(data)

pool = '569' 
stage = "Original WHERE Stage_Status = 'P' and OldLoanNumber is not NULL"
fields = 'Account,OldLoanNumber,Street,City,State,ZipCode,TIN,FirstName,MI,LastName,CB_TIN,CB_FirstName,CB_MI,CB_LastName'