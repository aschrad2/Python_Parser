# -*- coding: utf-8 -*-
"""
Created on Fri May 17 07:12:53 2019

@author: Megan.Francis
"""

import pandas as pd
import re

#Sections_re contains a list of regular expressions for known section names in the 2-FW
sections_re = ['[0, ]----------------------------- REMOVAL INFORMATION ------------------------------',
            '[0, ]?------------------------- PROPERTY INSPECTION DATE -----------------------------',
            '[0, ]?------------------------------ TRACKING STEPS ----------------------------------',
            '[0, ]?--------------------------- FORECLOSURE NOTES ----------------------------------\n[0,\n]STATUS NOTE:',
            '[0, ]?----------------------------------------------------- MSP TRANSACTION HISTORY ------------------------------------------------------',
            '[0, ]?------------------------- MSP FORECLOSURE ACCOUNTING ---------------------------',
            '[0, ]?--------------------------------[*] DESCRIPTIONS [*]--------------------------------',
            '[0, ]?------------------------------- MISCELLANEOUS ----------------------------------']

#page_breaks_re contains a list of regular expressions for known page or data breaks
page_breaks_re = ['\n?\d?S\d\d\d\d-2FW\s+[A-Z, ,,]+\s+\d\d/\d\d/\d\d\n',
                  '\n?\s?LOAN SERV SOLD ID GREG\d\d\d\d\d\d\s+[A-Z, ,,]+\s+PAGE\s*\d+\n\n?',
                  '\n?[0, ]?LOAN NO.\s*\d+\s*NEW SERVICER LOAN NUMBER\s*[0-9,-]*\n',
                  '\n\n',
                  '\n?\s?PROCESS-NOTES:\n',
                  '----------------------------------------------------- MSP TRANSACTION HISTORY ------------------------------------------------------',
                  '--------------------------- FORECLOSURE NOTES ----------------------------------']

def check_data(dataframe):
    dataframe.to_clipboard()
    check = input("Data for one or all loans is on your clipboard. Please paste the data into a spreadsheet and verify that it looks correct. If correct, enter Y. Otherwise, enter N and correct code.")
    if check == 'Y':
        return True
    return False

def read_data(filename):
    with open(file) as f:
        data = f.read()
    return data[1:]

def get_loans(data):
    loans = data.split('------------------------------------------------------------------------------------------------------------------------------------')  
    return loans[1:]

def get_sections(loan,sections):
    for section in sections:
        loan = re.sub(section, '------------------------------------------------------------------------------------------------------------------------------------', loan, 1)
    for item in page_breaks_re:
        loan = re.sub(item,'',loan)
    loan = loan.replace('--------------------------- FORECLOSURE NOTES ----------------------------------\n0','\n ')  
    loan = loan.split('------------------------------------------------------------------------------------------------------------------------------------')   
    return loan

def write_FC_descriptions():
    descriptions = pd.DataFrame(columns = ['OldLoanNumber','F/C STATUS','STATUS DATE','REMOVAL','PROCESS TYP','PROP DISP','CLAIM TYPE','DEFAULT','TEMPLATE','PROP DAMG','ATTORNEY NAME','ATTORNEY PHONE','PROP INSP','LAST/NEXT'])
    i = 0
    for loan in loans:
        descriptions.loc[i,'OldLoanNumber'] = loan[42:52]
        loan = get_sections(loan,sections_re)[1].split('\n')
        descriptions.loc[i,'F/C STATUS'] = loan[1][13:28].strip()
        descriptions.loc[i,'STATUS DATE'] = loan[1][29:38].strip()
        descriptions.loc[i,'REMOVAL'] = loan[1][47:len(loan[1])].strip()
        descriptions.loc[i,'PROCESS TYP'] = loan[2][13:36].strip()
        descriptions.loc[i,'PROP DISP'] = loan[2][47:len(loan[2])].strip()
        descriptions.loc[i,'CLAIM TYP'] = loan[3][13:38].strip()
        descriptions.loc[i,'DEFAULT'] = loan[3][47:len(loan[3])].strip()
        descriptions.loc[i,'TEMPLATE'] = loan[4][13:36].strip()
        descriptions.loc[i,'PROP DMG'] = loan[4][47:len(loan[4])].strip()
        descriptions.loc[i,'ATTORNEY NAME'] = loan[5][13:36].strip()
        descriptions.loc[i,'ATTORNEY PHONE'] = loan[6].strip()
        descriptions.loc[i,'PROP INSP'] = loan[7][13:len(loan[7])]
        descriptions.loc[i,'LAST/NEXT'] = loan[8][13:36].strip()       
        i = i + 1
    descriptions = descriptions.set_index('OldLoanNumber')   
    return descriptions

def write_FC_timeline():
    timeline =  pd.DataFrame(columns = ['OldLoanNumber','SCHEDULE DATE','ACTUAL DATE','COMPLETE','STEP CODE','STEP DESCRIPTION']) 
    i = 0
    for loan in loans:
        OldLoanNumber = loan[42:52]
        loan = get_sections(loan,sections_re)
        steps = loan[5].split('\n')
        for step in steps[3:]:
            timeline.loc[i,'OldLoanNumber'] = OldLoanNumber
            timeline.loc[i,'SCHEDULE DATE'] = step[0:9].strip()
            timeline.loc[i,'ACTUAL DATE'] = step[10:18].strip()
            timeline.loc[i,'COMPLETE'] = step[20:22].strip()
            timeline.loc[i,'STEP CODE'] = step[23:27].strip()
            timeline.loc[i,'DESCRIPTION'] = step[27:57].strip()
            i = i + 1
    timeline = timeline.set_index('OldLoanNumber')
    return timeline
        

def write_FC_comments():
    comments = pd.DataFrame(columns = ['OldLoanNumber','DATE','TIME','COMMENT']) 
    i = -1
    for loan in loans:
        OldLoanNumber = loan[42:52]
        loan = get_sections(loan, sections_re)
        notes = loan[4].split('\n')
        for note in notes:
            if re.search(r'^\s?(\d\d\/?){3}\s\s(\d\d:?){3}\s\s[A-Z,0-9,(]{3}\s\s',note) != None:
                i = i + 1
                comments.loc[i,'OldLoanNumber'] = OldLoanNumber
                comments.loc[i,'DATE'] = note[0:9].strip()
                comments.loc[i,'TIME'] = note[10:18].strip()
                comments.loc[i,'COMMENT'] = note[24:len(note)].strip()
            if re.search(r'^\s?(\d\d\/?){3}\s\s(\d\d:?){3}\s\s[A-Z,0-9,(]{3}\s\s',note) == None:
                comments.loc[i,'COMMENT'] = comments.loc[i,'COMMENT'] + ' ' + note[23:len(note)].strip()        
    comments = comments.set_index('OldLoanNumber')
    return comments


def write_data():
    location = input("Where do you want to store the output?")
    pool = input("Which pool?")
    name = location + '\\' + 'Pool' + '_' + pool + 'S-2FW.xlsx'
    with pd.ExcelWriter(name) as writer:
        write_FC_descriptions().to_excel(writer, sheet_name = 'Descriptions', engine = 'xlsxwriter')
        write_FC_timeline().to_excel(writer, sheet_name = 'Timeline', engine = 'xlsxwriter')     
        write_FC_comments().to_excel(writer, sheet_name = 'Comments', engine = 'xlsxwriter')  
    return True
    

file = input("Where is the S-2FW?")
data = read_data(file)
loans = get_loans(data)

