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
# python 05FSFProjectRelatedParser.py <datasource_id> <password>
#
# purpose:
# Gets the related projects of each category in each FSF project
################################################################

import re
import sys
import pymysql
from bs4 import BeautifulSoup

datasource_id = '122'  # sys.argv[1]


def run():
    try:
        cursor.execute(insertQuery,
                       (proj_num,
                        related_project_name,
                        datasource_id))
        db.commit()
        print(proj_num, " inserted into project related table!\n")
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

insertQuery = 'INSERT INTO fsf_project_related (proj_num, \
                                                related_project_name, \
                                                datasource_id, \
                                                date_collected) \
                VALUES(%s, %s, %s, now())'

try:
    cursor.execute(selectQuery)
    listOfProjects = cursor.fetchall()

    for project in listOfProjects:
        proj_num = project[0]
        html = project[1]
        print('\nworking on ', proj_num)

        soup = BeautifulSoup(html, 'html.parser')

        div = soup.find('div', style='column-count:2;-moz-column-count:2;-webkit-column-count:2;margin:2px 2px 2px 2px;')
        if div:
            for d in div:
                a = d.find_all('a')
                for line in a:
                    related_project_name = line.contents[0]
                    print('related_project_name: ', related_project_name)
                    run()

except pymysql.Error as err:
    print(err)
