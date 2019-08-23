# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 12:21:31 2019

@author: Megan.Francis
"""


import pandas as pd
import re

#Sections_re contains a list of regular expressions for known section names in the 2-FW
sections_re = ['               MORTGAGOR BILLING                                                              ALTERNATE DEBTORS\n',
            '0  BANKRUPTCY SETUP DATE:  \d\d/\d\d/\d\d\n',
            ' -------------------------------\n0-------------\* MOTION FOR RELIEF DATES \*--------------------  TRUSTEE\n',
            'BANKRUPTCY CLAIM INFORMATION:\n -----------------------------\n0------------------------\* PRE-PETITION CLAIM \*------------------------------\n',
            '[0, ]?-------------------------------\* PROCESS NOTES \*-------------------------------\n',
            '[0, ]?PROCESSOR CODE/NAME       CHAPTER  STATUS  FILING DATE   BANKRUPTCY CASE #\n',
            '[0, ]?\s?NOTICE     MEETING OF  PROOF OF CLAIM   CONFIRMATION   REPAYMENT  AUTOMATIC    PAYMENTS    ASSET   REGION\n',
            '\s?\s?RECEIVED    CREDITORS    FILING DATE     HEARING DATE    PERIOD    STAY LIFT   INSIDE PLAN  CASE     CODE\n',
            '[0, ]?\s?ESTIMATED   ------ FNMA LASER -------    -- CREDIT BUREAU --   MAN    OFFICE    CLASS\n',
            '\s?\s?DISCHARGE   CODE    DATE     CHANGED     IND CMNT STAT MTGRS   CODE    CODE     CODE\n',
            ' BANKRUPTCY HISTORY LEDGER:\n[0, ]?\s?--------------------------'
            '[0, ]?MORTGAGE COMPANY ATTORNEY NAME AND ADDRESS:\n[0, ]?\s?-------------------------------------------',
            '0DEBTOR ATTORNEY NAME AND ADDRESS:\n[0, ]?\s? ---------------------------------',
            '0TRUSTEE NAME AND ADDRESS:\n[0, ]?\s?-------------------------',
            '0COURT ADDRESS:\n[0, ]?\s?--------------']

#page_breaks_re contains a list of regular expressions for known page or data breaks
page_breaks_re = ['\n?\d?P\d\d\d\d-1BW\s+[A-Z, ,,]+\s+\d\d/\d\d/\d\d\n',
                  '\n?\s?LN SERV SOLD ID GREG\d\d\d\d\d\d\s+[A-Z, ,,]+\s+PAGE\s*\d+\n\n?',
                  '\n?[0, ]?LOAN NUMBER\s*\d+\s*NEW SERVICER LOAN NUMBER\s*[0-9,-]*\n',
                  '------------------------------------------------------------------------------------------------------------------------------------',
                  '----------------------------------------------------- MSP TRANSACTION HISTORY ------------------------------------------------------\n',
                  '[0, ]?-------------------------------\* PROCESS NOTES \*-------------------------------\n',
                  ]

def read_data(filename):
    with open(file) as f:
        data = f.read()
    return data[1:]

def get_loans(data):
    loans = data.split('               MORTGAGOR BILLING                                                              ALTERNATE DEBTORS')  
    return loans[1:]

def get_sections(loan,sections):
    for section in sections:
        loan = re.sub(section, '----------------------------- Smitty Werbenjagermanjensen -----------------------------', loan, 1)
    for item in page_breaks_re:
        loan = re.sub(item,'',loan) 
    loan = loan.split('----------------------------- Smitty Werbenjagermanjensen -----------------------------')   
    return loan
        
def write_BK_comments():
    i = -1    
    comments = pd.DataFrame(columns = ['Borrower TIN','DATE','TIME','COMMENT'])
    for loan in loans:      
        loan = get_sections(loan, sections_re)
        notes = loan[9].split('\n')
        borrower_tin = loan[0].split('SSN:')[3][0:14].strip()
        for note in notes:
            if re.search(r'^\s?(\d\d\/?){3}\s\s(\d\d:?){3}\s\s[A-Z,0-9,(]{3}\s\s',note) != None:
                i = i + 1
                comments.loc[i,'Borrower TIN'] = re.sub('-','',borrower_tin)
                comments.loc[i,'DATE'] = note[0:9].strip()
                comments.loc[i,'TIME'] = note[10:18].strip()
                comments.loc[i,'COMMENT'] = note[24:len(note)].strip()
            if re.search(r'^\s?(\d\d\/?){3}\s\s(\d\d:?){3}\s\s[A-Z,0-9,(]{3}\s\s',note) == None:
                comments.loc[i,'COMMENT'] = comments.loc[i,'COMMENT'] + ' ' + note[23:len(note)].strip()
        
    return comments    

def write_BK_main():
    i = 0
    main = pd.DataFrame(columns = [#These are from the borrower and property information section. There are more than are listed here
                                   'MORTGAGOR NAME','MORTGAGOR SSN',
                                   #These are from the section below BANKRUPTCY SETUP DATE
                                   'CHAPTER','STATUS','FILING DATE','BANKRUPTCY CASE #',
                                   'PROOF OF CLAIM FILING DATE','FILING STATE','FILING DISTRICT'])
    for loan in loans:
        loan = get_sections(loan, sections_re)
        court = loan[12].split('\n')
        main.loc[i,'MORTGAGOR SSN'] = re.sub('-','',loan[0].split('SSN:')[3][0:14].strip())
        main.loc[i,'CHAPTER'] = loan[2][27:34].strip()
        main.loc[i,'STATUS'] = loan[2][36:42].strip()
        main.loc[i,'FILING DATE'] = loan[2][44:55].strip()
        main.loc[i,'BANKRUPTCY CASE #'] = loan[2][56:].strip()
        main.loc[i,'PROOF OF CLAIM FILING DATE'] = loan[4][25:36].strip()
        main.loc[i,'FILING STATE'] = re.sub('STATE','',court[8]).strip()
        main.loc[i,'FILING DISTRICT'] = re.sub('\s?DIST[A-Z, ,-]*','',re.sub('\s*NAME 2\s*','',re.sub('\.','DIST',court[3])))
        i = i + 1
    
    return main

def check_data(dataframe):
    dataframe.to_clipboard()
    check = input("Data for one or all loans is on your clipboard. Please paste the data into a spreadsheet and verify that it looks correct. If correct, enter Y. Otherwise, enter N and correct code.")
    if check == 'Y':
        return True
    return False


file = input("Where is the 1-BW?")
data = read_data(file)
loans = get_loans(data)
