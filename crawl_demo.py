# coding:utf8
import requests
import psycopg2
import config as cfg
# import pymysql as mdb


# conn = mdb.connect(cfg.host, cfg.user, cfg.passwd, cfg.DB_NAME)
conn = psycopg2.connect(host=cfg.host, port=cfg.port, user=cfg.user, password=cfg.passwd,database=cfg.DB_NAME)
cursor = conn.cursor()

ip_list = []
try:
    cursor.execute("SELECT content FROM {}.{}".format(cfg.SCHEMA_NAME,cfg.TABLE_NAME))
    result = cursor.fetchall()
    for i in result:
        ip_list.append(i[0])
except Exception as e:
    print(e)
finally:
    cursor.close()
    conn.close()

for i in ip_list:
    proxy = {'http': 'http://'+i}
    url = "https://www.github.com/"
    r = requests.get(url, proxies=proxy, timeout=4)
    print(r.headers)