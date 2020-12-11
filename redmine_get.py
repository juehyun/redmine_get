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
#-- python script for downloading & synchronizing redmine issues or projects
#--    * attachment files
#--    * issue page (.url shortcut & .html)
#
#-- Created by Joohyun Lee (juehyun@etri.re.kr)
#
#----------------------------------------------------------------------
# Installation
#----------------------------------------------------------------------
#
# Save python scripts ( redmine_get.py , redmine_get_def.py )
# 
# Save webdriver(.exe) to somewhere and chagne variable (PATH_CHROME_DRIVE) in redmine_get.py (this file)
#
# Install python3 ( not compatible with python 2.x )
#
# Install required package
#   > pip install grequests
#   > pip install requests
#   > pip install wget
#   > pip install selenium
#   > pip install bs4
#   > pip install validators
#   > pip install pathlib
#   > pip install os-win
#   > pip install pywin32
#   > ...
#
# Usage
#   > python path_to\redmine_get.py -proj  proj_a  proj_b  proj_c 
#   > python path_to\redmine_get.py -issue 1319 1573 1554
#   > python path_to\redmine_get.py -proj  proj_a  proj_c  -issue 1319 1513
#   > python path_to\redmine_get.py [Enter] to see usage
#
#----------------------------------------------------------------------
#--Revision History Here
#----------------------------------------------------------------------
#--Rev              Date              Comments
#
#**********************************************************************
from redmine_get_def import *

# redmine server url
URL_REDMINE_SERVER = 'http://xxx.xxx.xx.xxx:8080'
PATH_CHROME_DRIVE  = 'C:\..path\to\chromedriver_win32_87.0.4280.exe'

#----------------------------------------------------------------------
# download issue and attachment files
#----------------------------------------------------------------------
tic = timeit.default_timer()

(ID, PW, CLONING, GET_CLOSED_ISSUE, L_PROJ_ID, L_ISSUE_N ) = parse_argv()

chrome = create_browser(PATH_CHROME_DRIVE)

redmine_login(chrome, URL_REDMINE_SERVER, ID, PW)

# get project pages and download all issues from specified project
for proj_id in L_PROJ_ID:
    list_issue_projdir = redmine_get_all_issues(chrome, URL_REDMINE_SERVER, proj_id, GET_CLOSED_ISSUE )
    for iss_n in [i[0] for i in list_issue_projdir]:
        redmine_get_issue_page_and_download_files(chrome, iss_n, URL_REDMINE_SERVER, ID, PW, CLONING)

# download specified issues 
for iss_n in L_ISSUE_N:
    redmine_get_issue_page_and_download_files(chrome, iss_n, URL_REDMINE_SERVER, ID, PW, CLONING)

#----------------------------------------------------------------------
# close 
#----------------------------------------------------------------------
toc = timeit.default_timer()
printMsg(f'Job Completed ... Time Elapsed {str(datetime.timedelta(seconds=toc - tic))}')
close_all(chrome)
