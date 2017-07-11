# -*- coding: utf-8 -*-
# Copyright (C) 2004-2017 Megan Squire <msquire@elon.edu>
# License: GPLv3
# 
# Contribution from:
# Caroline Frankel
#
# We're working on this at http://flossmole.org - Come help us build
# an open and accessible repository for data and analyses for free and open
# source projects.
#
# If you use this code or data for preparing an academic paper please
# provide a citation to:
#
# Howison, J., Conklin, M., & Crowston, K. (2006). FLOSSmole:
# A collaborative repository for FLOSS research data and analyses.
# International Journal of Information Technology and Web Engineering, 1(3),
# 17–26.
#
# and
#
# FLOSSmole: a project to provide research access to
# data and analyses of open source projects.
# Available at http://flossmole.org
#
################################################################
# usage:
# python 02FSFProjectsParser.py <datasource_id> <password>
#
# purpose:
# to get the release date, project long name, project web name and long description of each FSF project
################################################################

import re
import sys
import pymysql
from bs4 import BeautifulSoup

datasource_id = '272'  # sys.argv[1]


def regexMaker(regex):
    line = re.findall(regex, str(soup))
    if line:
        word = line[0]
        return word


def month_converter(month):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return months.index(month) + 1


def run():
    try:
        cursor.execute(insertQuery,
                       (released_on,
                        proj_long_name,
                        proj_web_name,
                        desc_long,
                        proj_num,
                        datasource_id))
        db.commit()
        print(proj_num, " inserted into projects table!\n")
    except pymysql.Error as err:
        print(err)
        db.rollback()

# establish database connection: SYR
try:
    db = pymysql.connect(host='flossdata.syr.edu',
                         user='',
                         passwd='',
                         db='',
                         use_unicode=True,
                         charset="utf8mb4")
    cursor = db.cursor()
except pymysql.Error as err:
    print(err)

selectQuery = 'SELECT proj_num, indexhtml FROM fsf_project_indexes'


insertQuery = 'UPDATE fsf_projects SET released_on = %s, \
                                        proj_long_name = %s, \
                                        proj_web_name = %s, \
                                        desc_long = %s, \
                                        date_collected = now() \
                WHERE proj_num = %s AND datasource_id = %s'

try:
    cursor.execute(selectQuery)
    listOfProjects = cursor.fetchall()

    for project in listOfProjects:
        proj_num = project[0]
        html = project[1]
        print('\nworking on ', proj_num)

        soup = BeautifulSoup(html, 'html.parser')
        
        try:
            releasedLine = regexMaker('/>released on (.*?)\s*</p>')
            releasedSplit = releasedLine.split(' ')
            day = releasedSplit[0]
            monthName = releasedSplit[1]
            month = month_converter(monthName[:3])
            year = releasedSplit[2]
            released_on = '{}-{}-{}'.format(year, month, day)
            print('released on: ', released_on)
        except:
            released_on = None
            print('released on: ', released_on)

        proj_long_name = regexMaker('\"wgTitle\":\"(.*?)\"')
        print('project long name: ', proj_long_name)

        proj_web_name = regexMaker('\"wgPageName\":\"(.*?)\"')
        print('project web name: ', proj_web_name)

        try:
            div = soup.find('div', id='Overview')
            p = div.find_all('p')
            desc_long = ''
            for line in p:
                if len(line) == 1:
                    desc_long = desc_long.strip() + line.contents[0]
            print('desc long: ', desc_long)
        except:
            desc_long = None

        run()

except pymysql.Error as err:
    print(err)
