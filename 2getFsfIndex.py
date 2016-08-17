# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 12:28:16 2016

@author: eashwell2
"""

import sys
import pymysql
import datetime
import time
import os
import codecs
from bs4 import BeautifulSoup
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

datasource_id = str(sys.argv[1])
password = str(sys.argv[2])

if datasource_id:
    # ======
    # Collector
    # ======
    try:
        dbh1 = pymysql.connect(host='grid6.cs.elon.edu',
                               database='test',
                               user='eashwell',
                               password=password,
                               charset='utf8')
    except pymysql.Error as err:
        print(err)
    cursor1 = dbh1.cursor()
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
                               database='test',
                               user='test',
                               password=password,
                               charset='utf8')
    except pymysql.Error as err:
        print(err)
    cursor3 = dbh3.cursor()

    selectQuery = "SELECT `url` FROM `fsf_projects_1`"

    insertQuery = "INSERT INTO `fsf_project_indexes_1`(`datasource_id`,\
    `proj_unixname`, `indexhtml`, `date_collected`) VALUES (%s,%s,%s,%s)"

    os.mkdir("Projects")

    cursor1.execute(selectQuery)

    total = cursor1.fetchall()

    for url in total:
        title = str(url)[32:-3]

        url_stem = str(url)[2:-3]

        print(url_stem)

        try:
            html1 = urllib2.urlopen(url_stem).read()
        except urllib2.HTTPError as error:
            print(error)
        else:
            fileloc = "Projects" + "/Index.html"
            outfile = codecs.open(fileloc, 'w')
            outfile.write(str(html1))
            outfile.close()

        soup = BeautifulSoup(open(fileloc), "lxml")
        # ======
        # LOCAL
        # ======
        try:
            cursor2.execute(insertQuery, (datasource_id, title,
                                          str(soup), datetime.datetime.now()))
            dbh2.commit()
        except pymysql.Error as error:
            print(error)
            dbh2.rollback()
        # =======
        # REMOTE
        # =======
        try:
            cursor3.execute(insertQuery, (datasource_id, title,
                                          str(soup), datetime.datetime.now()))
            dbh3.commit()
        except pymysql.Error as error:
            print(error)
            dbh3.rollback()
        time.sleep(10)
else:
    print("You need both a datasource_id and password.")
    exit
cursor1.close()
cursor2.close()
cursor3.close()

dbh1.close()
dbh2.close()
dbh3.close()
