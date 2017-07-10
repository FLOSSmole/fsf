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
# python 1FSFWebScraper.py <datasource_id> <password>
#
# purpose:
# get the project number, name, url, real url, and short description of each FSF project
# get the license information of each FSF project
# get the index html of each FSF project
################################################################

import re
import sys
import pymysql
from bs4 import BeautifulSoup
import ssl
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

datasource_id = '272'


def runProjects():
    try:
        cursor.execute(insertProjectsQuery,
                       (datasource_id,
                        proj_num,
                        proj_unixname,
                        url2,
                        real_url,
                        desc_short))
        db.commit()
        print(proj_unixname, " inserted into projects table!\n")
    except pymysql.Error as err:
        print(err)
        db.rollback()


def runIndexes():
    try:
        cursor.execute(insertIndexesQuery,
                       (proj_num,
                        datasource_id,
                        indexhtml))
        db.commit()
        print(proj_unixname, " inserted into indexes table!\n")
    except pymysql.Error as err:
        print(err)
        db.rollback()


def runLicenses():
    try:
        cursor.execute(insertLicensesQuery,
                       (proj_num,
                        licenses,
                        datasource_id))
        db.commit()
        print(proj_unixname, " inserted into licenses table!\n")
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

insertProjectsQuery = 'INSERT INTO fsf_projects (datasource_id, \
                                                 proj_num, \
                                                 proj_unixname, \
                                                 url, \
                                                 real_url, \
                                                 desc_short, \
                                                 date_collected) \
                        VALUES(%s, %s, %s, %s, %s, %s, now())'

insertIndexesQuery = 'INSERT INTO fsf_project_indexes (proj_num, \
                                                       datasource_id, \
                                                       indexhtml, \
                                                       date_collected) \
                        VALUES (%s, %s, %s, now())'

insertLicensesQuery = 'INSERT into fsf_project_licenses (proj_num, \
                                                         license, \
                                                         datasource_id, \
                                                         date_collected) \
                        VALUES (%s, %s, %s, now())'

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

try:
    urlResults = 'https://directory.fsf.org/wiki/All'
    req3 = urllib2.Request(urlResults, headers=hdr)
    html3 = urllib2.urlopen(req3, context=ssl._create_unverified_context()).read()
    soup2 = BeautifulSoup(html3, 'html.parser')
    num = 0
    numResults = 'There are currently (.*?) approved packages'
    results = re.findall(numResults, str(soup2))[0]

    while num < int(results):
        url = 'https://directory.fsf.org/wiki?title=Special:Ask&offset=' + str(num) + '&limit=500&q=%5B%5BName%3A%3A%2B%5D%5D&p=30px-5D-5D%2C%3DGNU-3F%2Fmainlabel%3D%2Fformat%3Dtable&po=%3FShort+description%3DDescription%0A%3FHomepage+URL%3DHomepage%0A%3FLicense%0A%3FIs+GNU%23%5B%5BFile%3AHeckert_gnu.small.png%0A'
        req = urllib2.Request(url, headers=hdr)
        html = urllib2.urlopen(req, context=ssl._create_unverified_context()).read()

        soup = BeautifulSoup(html, 'html.parser')

        table = soup.find('table', {'class': 'sortable wikitable smwtable'})

        tr = table.find_all('tr')
        for t in tr:
            regexProjNum = 'data-row-number=\"(.*?)\"'
            projNumFinder = re.findall(regexProjNum, str(t))
            if projNumFinder:
                proj_num = projNumFinder[0]
                print('project number: ', proj_num)

            td = t.find_all('td')

            proj_unixname = td[0].contents[0].contents[0]
            print('project unixname: ', proj_unixname)

            regexUrl = '<a href="/wiki/(.*?)"'
            urlFinder = re.findall(regexUrl, str(td[0]))
            if urlFinder:
                url2 = 'https://directory.fsf.org/wiki/' + urlFinder[0]
                req2 = urllib2.Request(url2, headers=hdr)
                indexhtml = urllib2.urlopen(req2, context = ssl._create_unverified_context()).read()

            desc_short = td[1].contents[0]
            print('short description: ', desc_short)

            real_url = td[2].contents[0].contents[0]
            print('real url: ', real_url)

            licenseLine = td[3]

            regex = 'title=\"(.*?)\"'
            regexFinder = re.findall(regex, str(licenseLine))
            if regexFinder:
                for r in regexFinder:
                    if '(page does not exist)' in r:
                        licenses = r.split(' (')[0]
                        print('license: ', licenses)
                        runLicenses()
                    else:
                        if 'License:' in r:
                            licenses = r.split(':')[1]
                            print('license: ', licenses)
                            runLicenses()
                        else:
                            licenses = r
                            print('license: ', licenses)
                            runLicenses()

            runIndexes()
            runProjects()
        num = num + 500

except pymysql.Error as err:
    print(err)
except urllib2.HTTPError as herror:
    print(herror)
