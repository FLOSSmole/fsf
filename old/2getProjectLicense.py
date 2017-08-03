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
        dbh2 = pymysql.connect(host='',
                               database='',
                               user='',
                               password=password,
                               charset='utf8')
    except pymysql.Error as err:
        print(err)
    cursor2 = dbh2.cursor()

    # =======
    # REMOTE
    # =======
    try:
        dbh3 = pymysql.connect(host='',
                               database='',
                               user='',
                               password=password,
                               charset='utf8')
    except pymysql.Error as err:
        print(err)
    cursor3 = dbh3.cursor()

    insertQuery = "INSERT INTO `fsf_project_licenses_1`(`datasource_id`,\
    `proj_unixname`, `license`, `date_collected`) VALUES (%s,%s,%s,%s)"

    fileloc = datasource_id + "/test.xml"

    soup = BeautifulSoup(open(fileloc), "lxml")

    text = str(soup)
    text = str(text)
    text = text[5:]
    text = text[:-6]
    text = text.split("\\n")
    skip = 50
    swivt = 0
    title = None
    title = None
    lic = None
    for line in text:
        findEnd = re.search("(\\\\t</swivt:subject>)", line)
        if findEnd:
            swivt = swivt + 1

        findTitle = re.search('\\\\t\\\\t<rdfs:label>(.+)</rdfs:label>', line)
        if findTitle:
            title = findTitle.group(1)

        findLicense = re.search('\\\\t\\\\t<property:license rdf:resource="&' +
                                'amp;wiki;(.+)"></property:license>', line)
        if findLicense:
            lic = findLicense.group(1)
        if lic is not None:
            print(datasource_id)
            print(title)
            print(lic)
            print(datetime.datetime.now())
            # ======
            # LOCAL
            # ======
            try:
                cursor2.execute(insertQuery, (datasource_id,
                                              title,
                                              lic,
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
                                              lic,
                                              datetime.datetime.now()))
                dbh2.commit()
            except pymysql.Error as error:
                print(error)
                dbh3.rollback()

            lic = None
        if swivt == 1:
            title = None
        skip = skip - 1

else:
    print("You need both a datasource_id and password.")
    exit
cursor2.close()
cursor3.close()

dbh2.close()
dbh3.close()
