# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 08:29:57 2019

@author: Megan.Francis
"""

import os
import shutil 
import re
import pandas as pd
import qpool as qp

def get_worklist():
    directory = input("Where are the files?")
    folders = os.walk(directory)
    worklist = pd.DataFrame(columns = ['File Path','File Name','Account'])
    i = 0    
    for folder in folders:
        folder_name = folder[0]
        files = folder[2]
        for file in files:
            if re.search(r'^\d{6}-\d{3}',file) != None:
                worklist.loc[i,'File Path'] = folder_name + '\\' + file
                worklist.loc[i,'File Name'] = file   
                worklist.loc[i,'Account'] = file[0:10]
                i = i + 1             
    return worklist

def get_folder_info(loans):
    borrower = qp.get_prod_data('Account, [Last Name], isActive', loans)
    
    return borrower.set_index(str('Account'))
    
def to_mod_folder(worklist):
    loans = qp.get_str_loans(worklist)
    folder_info = get_folder_info(loans)
    for item in worklist.index:
        account = worklist.loc[item]['Account']
        file_name = worklist.loc[item]['File Name']
        current_path = worklist.loc[item]['File Path']
        if re.search(r'_Note_',file_name) == None:
            try:
                isActive = folder_info.loc[account]['isActive']
                last_name = folder_info.loc[account]['Last Name']
            except:
                continue
            if isActive == True:
                new_location = '\\\\cottonwood\\Users\\Shared\\Loan Documents - Active\\' + account + ' - ' + last_name + '\\II. Servicing\\D. Amendments & Extensions'
            if isActive != True:
                new_location = '\\\\cottonwood\\Users\\Shared\\Loan Documents - Inactive\\' + account + ' - ' + last_name + '\\II. Servicing\\D. Amendments & Extensions'
            if not os.path.exists(new_location):
                log('File not copied-- folder ' + new_location + ' does not exist', 'File Mover Test - Directory Does not Exist 06-19-19.txt')
            if os.path.exists(new_location + '\\' + file_name):
                log('File not copied--' + file_name + ' already exists', 'File Mover Test - File Exists 06-19-19.txt')      
            if not os.path.exists(new_location + '\\' + file_name) and os.path.exists(new_location):
                shutil.copy2(current_path, new_location)
                log(file_name + '----->' + new_location + '\\' + file_name, 'File Mover Test - Moved 06-19-19.txt')            
    return True

def log(message, log_file_name):
    with open(log_file_name,'a') as f:
        f.write(message + '\n')
    return True