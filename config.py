# coding:utf-8

"""
Page number that you crawl from those websites.
* if your crawl task is not heavy, set page_num=2~5
* if you'd like to keep a proxies pool, page_num=10 can meet your need.
"""
page_num = 1

# ip test timeout.
timeout = 2

# database host
host = 'localhost'

# database host
port = 5432

# db user
user = 'postgres'

# db password
passwd = 'root'

# db name
DB_NAME = 'linzi'

# schema name
SCHEMA_NAME = 'jiake'

# table name
TABLE_NAME = 'proxy_ips'

# max failure times of an ip, if exceed, delete it from db.
USELESS_TIME = 4

# lowest success rate of an ip, if exceed, delete it from db.
SUCCESS_RATE = 0.8

# timeout punishment
TIME_OUT_PENALTY = 10

# ip quality assessment time interval. (currently once per day.)
CHECK_TIME_INTERVAL = 6*3600
