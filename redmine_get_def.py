#!C:\Python382\bin\python
#*********************************************************************
# COPYRIGHT (C) 2017 Joohyun Lee (juehyun@etri.re.kr)
# 
# MIT License
# 
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#********************************************************************/
#
#-- python script for downloading & synchronizing redmine issues
#--    * attachment files
#--    * issue page (.url shortcut & .html)
#
#-- Created by Joohyun Lee (juehyun@etri.re.kr)
#
#----------------------------------------------------------------------
#--Revision History Here
#----------------------------------------------------------------------
#--Rev              Date              Comments
#                   20200529          juehyun: add color to "saved to:"
#
#**********************************************************************

#----------------------------------------------------------------------
# import
#----------------------------------------------------------------------
import grequests
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import os
import wget
import urllib.request
import win32clipboard
import re
import validators
import getpass
import pathlib
import time
import shutil
import timeit
import datetime
import sys
import unicodedata

#----------------------------------------------------------------------
# Functions
#----------------------------------------------------------------------
def printErr(f_str):
    print(f'[31mERROR: {f_str}[0m')

def printMsg(f_str):
    print(f'[32minfo : {f_str}[0m')

def printMhl(f_str):
    print(f'[35minfo : {f_str}[0m')

def get_redmine_issue_url():
    """
    take redmine issue's URL from clipbard
    check whether valid url and linked to redmine issue
    """
    win32clipboard.OpenClipboard()
    url = win32clipboard.GetClipboardData()
    win32clipboard.CloseClipboard()
    # check the URL http:xxx.xxx.xxx.xx:8080/redmine/issues/1234
    path, issue_num = os.path.split(url)
    path, issue     = os.path.split(path)
    path, redmine   = os.path.split(path)
    # check the URL is redmine issues
    if validators.url(url) and issue_num.isdigit() and issue=='issues' and redmine=='redmine' :
        URL = url;
        print(f'URL for redmine issue (get from Clipboard)')
        print(f'{URL}')
    else:
        print(f'Clipboard contents :')
        if validators.url(url):
            print(f'\t{url}')
        else:
            print(f'\tnon-url data')
        print(f'\n')
        print(f'Usage: Copy (e.g. Ctrl+C) redmine issue URL (e.g. http://192.168.0.1:8080/redmine/issues/1234 ) to clipboard and execute script')
        URL = ""

    return URL

def check_redmine_issue_url(inUrl):
    """
    check the inputURL is valid internet url pointing to redmine issue
    """
    path, issue_num = os.path.split(inUrl)
    path, issue     = os.path.split(path)
    path, redmine   = os.path.split(path)
    # check the URL is redmine issues
    if validators.url(inUrl) and issue_num.isdigit() and issue=='issues' and redmine=='redmine' :
        printMsg(f'url for redmine issue                  : {inUrl}')
        return(True)
    else:
        printErr(f'invalid url: {inUrl}')
        return(False)

def is_download_finished(folder):
    """
    check previous chrome downloading is completed
    only necessary if you use CHROME selenium webdriver for downloading files (not needed for requests, grequests)
    """
    firefox_temp_file = sorted(pathlib.Path(folder).glob('*.part'))
    chrome_temp_file = sorted(pathlib.Path(folder).glob('*.crdownload'))
    downloaded_files = sorted(pathlib.Path(folder).glob('*.*'))
    if (len(firefox_temp_file) == 0) and \
       (len(chrome_temp_file) == 0) and \
       (len(downloaded_files) >= 1):
        return True
    else:
        return False

def strip_html(raw_html):
    #cleanr = re.compile('<.*?>')
    cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def clear_html(raw_html):
    cleantext = BeautifulSoup(raw_html, "lxml").text
    return cleantext

def clean_filename(in_filename):
    out_filename = re.sub(r'[\\/:*?"<>|]+','',in_filename)
    return out_filename

def parse_http_code(code):
    if   (code==100): 
        return ('Continue')
    elif (code==101): 
        return ('Switching Protocols')
    elif (code==102): 
        return ('Processing')
    elif (code==103): 
        return ('Early Hints')
    elif (104<code and code<199): 
        return ('Unassigned')
    elif (code==200): 
        return ('OK')
    elif (code==201): 
        return ('Created')
    elif (code==202): 
        return ('Accepted')
    elif (code==203): 
        return ('Non-Authoritative Information')
    elif (code==204): 
        return ('No Content')
    elif (code==205): 
        return ('Reset Content')
    elif (code==206): 
        return ('Partial Content')
    elif (code==207): 
        return ('Multi-Status')
    elif (code==208): 
        return ('Already Reported')
    elif (209<code and code<225): 
        return ('Unassigned')
    elif (code==226): 
        return ('IM Used')
    elif (code==227<code and code<299): 
        return ('Unassigned')
    elif (code==300): 
        return ('Multiple Choices')
    elif (code==301): 
        return ('Moved Permanently')
    elif (code==302): 
        return ('Found')
    elif (code==303): 
        return ('See Other')
    elif (code==304): 
        return ('Not Modified')
    elif (code==305): 
        return ('Use Proxy')
    elif (code==306): 
        return ('(Unused)')
    elif (code==307): 
        return ('Temporary Redirect')
    elif (code==308): 
        return ('Permanent Redirect')
    elif (309<code and code<399): 
        return ('Unassigned')
    elif (code==400): 
        return ('Bad Request')
    elif (code==401): 
        return ('Unauthorized')
    elif (code==402): 
        return ('Payment Required')
    elif (code==403): 
        return ('Forbidden')
    elif (code==404): 
        return ('Not Found')
    elif (code==405): 
        return ('Method Not Allowed')
    elif (code==406): 
        return ('Not Acceptable')
    elif (code==407): 
        return ('Proxy Authentication Required')
    elif (code==408): 
        return ('Request Timeout')
    elif (code==409): 
        return ('Conflict')
    elif (code==410): 
        return ('Gone')
    elif (code==411): 
        return ('Length Required')
    elif (code==412): 
        return ('Precondition Failed')
    elif (code==413): 
        return ('Payload Too Large')
    elif (code==414): 
        return ('URI Too Long')
    elif (code==415): 
        return ('Unsupported Media Type')
    elif (code==416): 
        return ('Range Not Satisfiable')
    elif (code==417): 
        return ('Expectation Failed')
    elif (418<code and code<420): 
        return ('Unassigned')
    elif (code==421): 
        return ('Misdirected Request')
    elif (code==422): 
        return ('Unprocessable Entity')
    elif (code==423): 
        return ('Locked')
    elif (code==424): 
        return ('Failed Dependency')
    elif (code==425): 
        return ('Too Early')
    elif (code==426): 
        return ('Upgrade Required')
    elif (code==427): 
        return ('Unassigned')
    elif (code==428): 
        return ('Precondition Required')
    elif (code==429): 
        return ('Too Many Requests')
    elif (code==430): 
        return ('Unassigned')
    elif (code==431): 
        return ('Request Header Fields Too Large')
    elif (432<code and code<450): 
        return ('Unassigned')
    elif (code==451): 
        return ('Unavailable For Legal Reasons')
    elif (452<code and code<499): 
        return ('Unassigned')
    elif (code==500): 
        return ('Internal Server Error')
    elif (code==501): 
        return ('Not Implemented')
    elif (code==502): 
        return ('Bad Gateway')
    elif (code==503): 
        return ('Service Unavailable')
    elif (code==504): 
        return ('Gateway Timeout')
    elif (code==505): 
        return ('HTTP Version Not Supported')
    elif (code==506): 
        return ('Variant Also Negotiates')
    elif (code==507): 
        return ('Insufficient Storage')
    elif (code==508): 
        return ('Loop Detected')
    elif (code==509): 
        return ('Unassigned')
    elif (code==510): 
        return ('Not Extended')
    elif (code==511): 
        return ('Network Authentication Required')
    elif (512<code and code<599): 
        return ('Unassigned')
    else            : 
        return ('Unrecognized code')

#--------------------------------------------------------------------------------
# Get the redmine issue page, download the attachment files to folder
#--------------------------------------------------------------------------------
def redmine_get_issue_page_and_download_files(chrome, n_issue, url_server, user_id, passwd, cloning):
    print('')

    #0:use chrome selenium driver / 1:use requests single thread / 2:use grequests multiple thread
    download_method = 1

    #--------------------------------------------------------------------------------
    # Get URL for target redmine issue
    #--------------------------------------------------------------------------------
    url_issue = url_server + '/redmine/issues/' + n_issue
    url_login = url_server + '/redmine/login' # needed for requests, grequests session

    if(not check_redmine_issue_url(url_issue)):
        close_all(chrome)

    #--------------------------------------------------------------------------------
    # get page and description
    #--------------------------------------------------------------------------------
    chrome.get(url_issue)
    if(chrome.title.split(' ')[0] == '404'):
        printErr(f'webdriver fail to open redmine issue page: {url_issue}) - page not found')
        printErr(f'please check issue number')
        close_all(chrome)
    else:
        printMsg(f'webdriver success to open redmine issue: {chrome.title}')
    
    proj_folder    = strip_html( chrome.find_element_by_class_name('current-project').get_attribute('outerHTML') )
    issue_auth     = strip_html( chrome.find_element_by_class_name('author' ).find_element_by_tag_name('a' ).get_attribute('outerHTML') )
    issue_title    = strip_html( chrome.find_element_by_class_name('subject').find_element_by_tag_name('h3').get_attribute('outerHTML') )
    issue_title_fn = f'#{n_issue.rjust(5,"0")} _____________ {issue_auth}-{issue_title}'
    issue_title_fn = clean_filename(issue_title_fn)               # remove illegal char in filename
    issue_title_fn = unicodedata.normalize('NFC', issue_title_fn) # correct Mac hangul separation problem

    #---------------------------------------------------------------------------------
    # go to project folder to save files
    #---------------------------------------------------------------------------------
    workdir = os.getcwd()
    cd_projfolder(proj_folder)
    
    #---------------------------------------------------------------------------------
    # issue page (and its .url short-cut) always overwritten
    #---------------------------------------------------------------------------------
    with open(f'{issue_title_fn}.html', mode='w', buffering=-1, encoding='utf-8') as f:
        f.write(chrome.page_source)
        f.close()
    
    with open(f'{issue_title_fn}.url', mode='w', buffering=-1, encoding='utf-8') as f:
        f.write(f'[InternetShortcut]\nURL={url_issue}\n')
        f.close()
    
    printMsg(f'save redmine issue page (.html, .url)  : {issue_title_fn}')
    
    #---------------------------------------------------------------------------------
    # extract issue page information
    #---------------------------------------------------------------------------------
    # old version, xpath may different b/w issues
    #a_files     = chrome.find_elements_by_xpath('//*[@id="content"]/div[2]/div[5]/table/tbody/tr[*]/td[1]/a[1]')  # attached filename
    #a_urls      = chrome.find_elements_by_xpath('//*[@id="content"]/div[2]/div[5]/table/tbody/tr[*]/td[1]/a[2]')  # download button, url of file
    #a_descs     = chrome.find_elements_by_xpath('//*[@id="content"]/div[2]/div[5]/table/tbody/tr[*]/td[3]/span')  # description (author, date, time)
    
    downloadit = True
    a_section   = chrome.find_elements_by_class_name('attachments')
    if(len(a_section) == 0):
        print   (f'no attachment files from page, skip it : {url_issue}')
        downloadit = False
    elif(len(a_section) > 1):
        printErr(f'multiple attachment section found      : {len(a_section)}, {url_issue}')
        printErr(f'abnormal case, contact to juehyun')
        downloadit = False
    else:
        a_files     = a_section[0].find_elements_by_class_name('icon-attachment')
        a_urls      = a_section[0].find_elements_by_class_name('icon-download')
        a_descs     = a_section[0].find_elements_by_class_name('author')
        printMsg(f'number of found attachment files       : {len(a_files)}') # selenium chrome webdriver doesnot provide status_code
    
    #--------------------------------------------------------------------------------
    # download files (use chrome browser)
    #--------------------------------------------------------------------------------
    if (download_method==0 and downloadit):
        for i in range(len(a_files)) :
            orgf  = a_files[i].get_attribute('text')
            url   = a_urls[i].get_attribute('href')
            desc  = a_descs[i].get_attribute('innerHTML')   # '이주현, 04/01/2020 09:30'
            (auth,date,uptime) = re.sub(r'[,:]','',desc).split(' ')
            (date_m,date_d,date_y) = re.split('/',date)
    
            #------------------------------
            # local filename format
            #------------------------------
            newf  = f'#{n_issue.rjust(5,"0")} {date_y}{date_m}{date_d}_{uptime} {auth}-{orgf}'
            newf  = unicodedata.normalize('NFC', newf) # correct Mac hangul separation problem
    
            if( cloning or (not os.path.exists(newf)) ): # clone mode or file not exist -> download
                # get file
                chrome.get(url)
                time.sleep(1)
                # wiat until download completion
                while not (is_download_finished(dir_sav)):
                    time.sleep(0.5)
                    print(f'.')
    
                if( os.path.exists(newf) ):
                    print(f'detect duplicated file, replaced with new file : {newf}')
                    os.remove(newf)
                os.rename(orgf, newf)
                print   (f'[{i:03}] original : {orgf}')
                printMsg(f'      saved to : {newf}')
                print   (f'')
            else:
                print(f'[{i:03}] skip existing file : {newf}')
    
    #--------------------------------------------------------------------------------
    # download files (use python/requests module, single thread)
    #--------------------------------------------------------------------------------
    elif (download_method==1 and downloadit):
    
        #----------------------------
        # Login to redmine (requests)
        #----------------------------
        rs   = requests.Session()
        req  = rs.get(url_login)
        html = req.text
        soup = BeautifulSoup(html,'html.parser')
        csrf = soup.find('input', {'name':'authenticity_token'}) # find tag(meta), key(name) - value(csrf-token) pair / e.g.   < meta ... name=csrf-token ... content=blurblur...  >
        csrftoken = csrf['value']
        LOGINKEY  = { 'authenticity_token':csrftoken, 'username':user_id, 'password':passwd }
        req  = rs.post(url_login, data=LOGINKEY) # try to login
    
        if (req.status_code != 200):
            printErr(f'python/requests fail to login redmine  : {parse_http_code(req.status_code)}')
            close_all(chrome)
        else:
            printMsg(f'python/requests try to login redmine   : {parse_http_code(req.status_code)}')
    
        #----------------------------
        # Download
        #----------------------------
        for i in range(len(a_files)) :
            orgf  = a_files[i].get_attribute('text')
            url   = a_urls[i].get_attribute('href')
            desc  = a_descs[i].get_attribute('innerHTML')   # '이주현, 04/01/2020 09:30'
            (auth,date,uptime) = re.sub(r'[,:]','',desc).split(' ')
            (date_m,date_d,date_y) = re.split('/',date)
            #------------------------------
            # local filename format
            #------------------------------
            newf  = f'#{n_issue.rjust(5,"0")} {date_y}{date_m}{date_d}_{uptime} {auth}-{orgf}'
            newf  = unicodedata.normalize('NFC', newf) # correct Mac hangul separation problem
    
    
            if( cloning or (not os.path.exists(newf)) ): # clone mode or file not exist -> download
                # get file
                req = rs.get(url)
    
                # write to disk
                if( os.path.exists(newf) ):
                    print(f'detect duplicated file, replaced with new file : {newf}')
                    #os.remove(newf)
                with open(f'{newf}','wb') as f:
                    f.write(req.content)
                    f.close()
                print   (f'[{i:03}] original : {orgf}')
                printMsg(f'      saved to : {newf}')
                print   (f'')
            else:
                print(f'[{i:03}] skip existing file : {newf}')
    
    #--------------------------------------------------------------------------------
    # download files (use python/grequets module, multiple thread)
    #--------------------------------------------------------------------------------
    elif (download_method==2 and downloadit):
    
        #----------------------------
        # Login to redmine (requests)
        #----------------------------
        rs  = requests.Session()
        req = rs.get(url_login)
        html = req.text
        soup = BeautifulSoup(html,'html.parser')
        csrf = soup.find('input', {'name':'authenticity_token'}) # find tag(meta), key(name) - value(csrf-token) pair / e.g.   < meta ... name=csrf-token ... content=blurblur...  >
        csrftoken = csrf['value']
        LOGINKEY  = { 'authenticity_token':csrftoken, 'username':user_id, 'password':passwd }
        req  = rs.post(url_login, data=LOGINKEY) # try to login
    
        if (req.status_code != 200):
            printErr(f'python/requests fail to login redmine  : {parse_http_code(req.status_code)}')
            close_all(chrome)
        else:
            printMsg(f'python/requests success to login       : {parse_http_code(req.status_code)}')
    
        #----------------------------
        # Download
        #----------------------------
        list_orgf = list()
        list_url  = list()
        list_desc = list()
        list_newf = list()
    
        for i in range(len(a_files)) :
            orgf  = a_files[i].get_attribute('text')
            url   = a_urls[i].get_attribute('href')
            desc  = a_descs[i].get_attribute('innerHTML')   # '이주현, 04/01/2020 09:30'
            (auth,date,uptime) = re.sub(r'[,:]','',desc).split(' ')
            (date_m,date_d,date_y) = re.split('/',date)
    
            #------------------------------
            # local filename format
            #------------------------------
            newf  = f'#{n_issue.rjust(5,"0")} {date_y}{date_m}{date_d}_{uptime} {auth}-{orgf}'
            newf  = unicodedata.normalize('NFC', newf) # correct Mac hangul separation problem
    
            list_orgf.append(orgf)
            list_url.append(url)
            list_desc.append(desc)
            list_newf.append(newf)
    
        # get files using Asyncronous HTTP
        reqs  = ( grequests.get(u, session=rs) for u in list_url )
        resps = grequests.map(reqs)
    
        # write to disk
        i=0
        for p in resps:
            if( cloning or (not os.path.exists(list_newf[i])) ): # clone mode or file not exist -> download
                if( os.path.exists(list_newf[i]) ):
                    print(f'detect duplicated file, replaced with new file : {list_newf[i]}')
                    #os.remove(list_newf[i])
                with open(list_newf[i],'wb') as f:
                    f.write(p.content)
                    f.close()
                print   (f'[{i:03}] original : {list_orgf[i]}')
                printMsg(f'      saved to : {list_newf[i]}')
                print   (f'\n');
            else:
                print(f'[{i:03}] skip existing file : {list_newf[i]}')
            i+=1

    os.chdir(workdir)

def create_browser(path_chrome_drive):
    #--------------------------------------------------------------------------------
    # option setting : Chrome w/o GUI (headless mode)
    #--------------------------------------------------------------------------------
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    #options.add_argument('window-size=1920x1080')
    #options.add_argument("disable-gpu")
    #options.add_argument("--start-maximized")
    options.add_experimental_option("prefs", { "download.default_directory": os.getcwd() })
    #options.add_experimental_option("prefs", { "download.default_directory": def_dir_sav })

    #--------------------------------------------------------------------------------
    # option setting : Chrome not to wait until full page loading
    #--------------------------------------------------------------------------------
    caps = DesiredCapabilities().CHROME
    #caps["pageLoadStrategy"] = "normal"  # complete
    caps["pageLoadStrategy"] = "eager"   # interactive
    #caps["pageLoadStrategy"] = "none"     # you need "chrome.implicitly_wait(3)" statement (some site's full loading time is so long)

    #--------------------------------------------------------------------------------
    # Launch Chrome Driver
    #--------------------------------------------------------------------------------
    ch = webdriver.Chrome(path_chrome_drive, desired_capabilities=caps, options=options) # non-def-pageLoadStrategy, Headless(no-GUI)
    #ch = webdriver.Chrome(path_chrome_drive, desired_capabilities=caps)
    #ch = webdriver.Chrome(path_chrome_drive, options=options)
    #ch = webdriver.Chrome(path_chrome_drive)
    #ch.implicitly_wait(3) # An implicit wait tells WebDriver to poll the DOM for a certain amount of time when trying to find any element (or elements) not immediately available. The default setting is 0. Once set, the implicit wait is set for the life of the WebDriver object.

    return(ch)

def parse_argv():

    # default value
    run_mode_prj = False
    run_mode_iss = False
    get_closed_issue = False
    cloning = False
    list_proj_id = list()
    list_issue_n = list()

    # parse argv
    for arg in sys.argv:
        if('-pr' in arg):
            run_mode_prj = True
            run_mode_iss = False
        elif('-is' in arg):
            run_mode_prj = False
            run_mode_iss = True
        elif('-an' in arg):
            get_closed_issue = True
        elif('-cl' in arg):
            cloning = True
        else:
            if(run_mode_prj):
                list_proj_id.append(arg)
            elif(run_mode_iss):
                list_issue_n.append(arg)

    #--------------------------------------------------------------------------------
    # check argv
    #--------------------------------------------------------------------------------
    if (len(sys.argv)==1 or (len(list_proj_id)==0 and len(list_issue_n)==0) ):
        print(f'''
#----------------------------------------------------------------------
# Usage
#----------------------------------------------------------------------
# python {sys.argv[0]} -proj_id [options] [proj_id   | proj_id   | ... ]
# python {sys.argv[0]} -issue_n [options] [issue_num | issue_num | ... ]
#         -proj_id
#               download issues from specified projects and its sub-projects
#               find "proj_id" from redmine url : http://???.???.??.???:8080/redmine/projects/proj_abc
#                                                                                             ^^^^^^^^
#               list of some "proj_id" of redmine server
#
#         -issue_n
#               download only specified issues
#
#     options :
#         -any_issue
#               download all (open and closed) issues
#               otherwise, download only open issues
#         -clone
#               re-download all files and overwrite existing files
#               otherwise, download only new files (update)
#
# Example)
# python {sys.argv[0]} -pr proj_vic proj_abc -is 1234 2346 -cl -an
# python {sys.argv[0]} -pr ab11
# python {sys.argv[0]} -is 1234 1295 1325
# python {sys.argv[0]} -is 345  465 -pr ab11''')
        quit()

    #--------------------------------------------------------------------------------
    # User information
    #--------------------------------------------------------------------------------
    user_id =           input('redmine id =')
    pw = getpass.getpass('redmine pw =') # hide input

    #--------------------------------------------------------------------------------
    # print information
    #--------------------------------------------------------------------------------
    printMsg(f'User ID       : {user_id}')
    printMsg(f'Project IDs   : {list_proj_id}')
    printMsg(f'Issue numbers : {list_issue_n}')
    printMsg(f'cloning mode  : {cloning} (re-download all issues and overwrite it)')
    printMsg(f'get any_issues: {get_closed_issue} (also download closed issues)')
    
    #--------------------------------------------------------------------------------
    # return
    #--------------------------------------------------------------------------------
    return([user_id, pw, cloning, get_closed_issue, list_proj_id, list_issue_n])

def redmine_login(chrome, url_server, user_id, passwd):
    #--------------------------------------------------------------------------------
    # Login to redmine (Chrome)
    #--------------------------------------------------------------------------------
    url_login = url_server + '/redmine/login'
    chrome.get(url_login)
    
    if(chrome.title != 'AI SoC Research Division'):
        printErr(f'webdriver fail to open redmine login page: {url_login})')
        printErr(f'please check server address')
        close_all(chrome)
    else:
        printMsg(f'webdriver success to open login page   : {chrome.title}')
    
    el_id = chrome.find_element_by_xpath('//*[@id="username"]')
    el_pw = chrome.find_element_by_xpath('//*[@id="password"]')
    el_bt = chrome.find_element_by_xpath('//*[@id="login-submit"]')
    
    el_id.send_keys(user_id)
    el_pw.send_keys(passwd)
    el_bt.click()
    
    if(chrome.title != 'My page - AI SoC Research Division'):
        printErr(f'webdriver login failed, {url_login}, check ID/PW, ')
        close_all(chrome)
    else:
        printMsg(f'webdriver success to login redmine svr : {chrome.title}') # selenium chrome webdriver doesnot provide status_code

def redmine_get_all_issues( chrome, url_server, proj_id, download_closed_issue):

    #--------------------------------------------------------------------------------
    # get project page
    #--------------------------------------------------------------------------------
    url_proj = url_server + '/redmine/projects/' + proj_id
    printMsg(f'webdriver access to project page       : {url_proj}')
    chrome.get( url_proj )

    # check the page is available
    if(chrome.title.split(' ')[0] == '404'):
        printErr(f'webdriver fail to open redmine project   : {url_proj}) - page not found')
        printErr(f'please check project id')
        close_all(chrome)
    else:
        printMsg(f'webdriver success to open redmine proj : {chrome.title}')
    
    #--------------------------------------------------------------------------------
    # Click "Projects"
    #--------------------------------------------------------------------------------
    #el_proj = chrome.find_element_by_class_name('projects')
    #el_proj.click()
    
    #--------------------------------------------------------------------------------
    # Click "Issues"
    #--------------------------------------------------------------------------------
    el_proj_issues = chrome.find_elements_by_class_name('issues') # class_name="issues selected"

    if(len(el_proj_issues)==0):
        printErr(f'can not find "Issues" menu in proj page ({url_proj})')
        return([]);
    else:
        el_proj_issue  = el_proj_issues[0] # get the 1st webelement
        chrome.get(el_proj_issue.get_attribute('href'))

    if('<p class="nodata">No data to display</p>' in chrome.page_source ):
        printErr(f'No data to display, No issues in proj page ({url_proj})')
        return([]);
    
    if( download_closed_issue ):
        el_filter = chrome.find_element_by_xpath('//*[@id="operators_status_id"]/option[5]') # select "any" filter option
        el_filter.click()
        el_apply = chrome.find_element_by_xpath('//*[@id="query_form_with_buttons"]/p/a[1]')
        el_apply.click()
    
    #--------------------------------------------------------------------------------
    # get dictionary of {issues number, project name} from all pages
    #--------------------------------------------------------------------------------
    #dict_issue_projdir = dict()
    list_issue_projdir = list()
    n_page = 1
    flag_end_of_page = 0

    t_start = timeit.default_timer()
    while not (flag_end_of_page):
        #------------------------------------------------------
        # processing page (update dictionary {issue, projdir} )
        #------------------------------------------------------
        issues_fr_cur_page = chrome.find_elements_by_xpath('/html/body/div/div[2]/div[1]/div[4]/div[2]/form[2]/div/table/tbody/tr[*]')
        #for iss in issues_fr_cur_page:
        #    dict_issue_projdir.update( {iss.find_element_by_class_name('id').text :  iss.find_element_by_class_name('project').text } )
        for iss in issues_fr_cur_page:
            html = re.sub(r'<[^<]+?>','', iss.get_attribute('innerHTML') )
            list_issue_projdir.append( re.sub(r'\n( )*', '\n', html).split('\n')[2:4] )
    
        #------------------------------------------------------
        # check last page
        #------------------------------------------------------
        el_pages = chrome.find_element_by_class_name('pagination')
        if(len(el_pages.text) < 20): # check only single page,
            printMsg(f'Processed page [{n_page}] ... (last page)')
            flag_end_of_page = 1
        else:
            el_next = el_pages.find_element_by_class_name('next')  # find the class 'next page' : space can not be used in find_element_by_class_name()
            el_next_html = el_next.get_attribute('innerHTML')

            if(len(el_next_html) < 50): # "<span>Next >><span>"
                printMsg(f'Processed page [{n_page}] ... (last page)')
                flag_end_of_page = 1
            else:
                printMsg(f'Processed page [{n_page}] ... ')
                n_page = n_page + 1
                el_next.click()
    t_end = timeit.default_timer()
    printMsg(f'Time Elapsed {t_end - t_start:.2f} sec')

    #--------------------------------------------------------------------------------
    # print collected issues 
    #--------------------------------------------------------------------------------
    #for pair in sorted(dict_issue_projdir.items(), key=lambda x: x[1], reverse=True):
    #    print( pair )
    #return(dict_issue_projdir)

    i = 0
    print(f'[   #] folder\t#issue')
    for pair in sorted(list_issue_projdir, key=lambda x: x[1], reverse=False):
        print(f'[{i:4}] {pair[1]}\t{pair[0]}')
        i= i+1

    return(list_issue_projdir)

def cd_projfolder(projdir):
    if not os.path.exists(projdir):
        printMhl(f'downloading folder (create new dir)    : {projdir}')
        os.makedirs(projdir)
    else:
        printMhl(f'downloading folder (use existing dir)  : {projdir}')

    os.chdir(projdir)

def close_all(chrome):
    printMsg(f'Terminate web driver ... ')
    chrome.quit()
    quit()

def del_repeated_str(in_str):
    out_str = re.sub(r'(.+?)\1+(.*)$',r'\1\2', in_str)
    return(out_str)
