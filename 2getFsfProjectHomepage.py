# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 11:53:41 2016

@author: eashwell2
"""
import sys
import pymysql
import re
import datetime
from bs4 import BeautifulSoup

datasource_id = str(sys.argv[1])
password = str(sys.argv[2])

if datasource_id:
    # ======
    # LOCAL
    # ======
    try:
        dbh2 = pymysql.connect(host='grid6.cs.elon.edu',
                               database='test',
                               user='eashwell',
                               password=password,
                               charset='utf8')
    except pymysql.Error as err:
        print(err)
    cursor2 = dbh2.cursor()

    # =======
    # REMOTE
    # =======
    try:
        dbh3 = pymysql.connect(host='flossdata.syr.edu',
                               database='bitcoin',
                               user='megan',
                               password=password,
                               charset='utf8')
    except pymysql.Error as err:
        print(err)
    cursor3 = dbh3.cursor()

    insertQuery = "INSERT INTO `fsf_project_real_url_1`(`datasource_id`,\
    `proj_unixname`, `real_url`, `date_collected`) VALUES (%s,%s,%s,%s)"

    fileloc = datasource_id + "/directory.xml"

    soup = BeautifulSoup(open(fileloc), "lxml")

    text = str(soup)
    text = str(text)
    text = text[5:]
    text = text[:-6]
    text = text.split("\\n")
    skip = 50
    swivt = 0

    for line in text:
        findEnd = re.search("(\\\\t</swivt:subject>)", line)
        if findEnd:
            swivt = swivt + 1

        findTitle = re.search('\\\\t\\\\t<rdfs:label>(.+)</rdfs:label>', line)
        if findTitle:
            title = findTitle.group(1)

        findHomePage = re.search('\\\\t\\\\t<property:homepage_url' +
                                 ' rdf:resource=' +
                                 '"(.+)"></property:homepage_url>', line)
        if findHomePage:
            homePage = ""
            homePage = findHomePage.group(1)
        if swivt == 1:
            swivt = 0

            if skip <= 0:

                # ======
                # LOCAL
                # ======
                try:
                    cursor2.execute(insertQuery, (datasource_id,
                                                  title,
                                                  homePage,
                                                  datetime.datetime.now()))
                    dbh2.commit()
                except pymysql.Error as error:
                    print(error)
                    dbh2.rollback()

                # =======
                # REMOTE
                # =======
                try:
                    cursor3.execute(insertQuery, (datasource_id,
                                                  title,
                                                  homePage,
                                                  datetime.datetime.now()))
                    dbh2.commit()
                except pymysql.Error as error:
                    print(error)
                    dbh3.rollback()

                title = None
                homePage = None
        skip = skip - 1

else:
    print("You need both a datasource_id and password.")
    exit
cursor2.close()
cursor3.close()

dbh2.close()
dbh3.close()
