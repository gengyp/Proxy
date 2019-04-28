# coding:utf-8
import json
import time
import datetime
import requests
import psycopg2
import pandas as pd
import config as cfg
import random

'''
CREATE TABLE "jiake"."game_stmbuy_goods" (
"index" SERIAL PRIMARY KEY,
"on_seek_price_max" int8,
"on_seek_price_min" int8,
"market_name" text COLLATE "default",
"on_sale_price_max" int8,
"on_sale_price_min" int8,
"sale_count" int8,
"market_price" int8,
"on_sale_count" int8,
"on_seek_count" int8,
"last_price" int8,
"itime" timestamp(6),
"utime" timestamp(6),
"market_hash_name" text COLLATE "default",
"create_time" timestamp(6) DEFAULT CURRENT_TIMESTAMP
)WITH (OIDS=FALSE);
'''
def get_proxy():
  conn = psycopg2.connect(host=cfg.host, port=cfg.port, user=cfg.user, password=cfg.passwd,database=cfg.DB_NAME)
  cursor = conn.cursor()

  ip_list = []
  try:
      cursor.execute("SELECT content FROM {}.{}".format(cfg.SCHEMA_NAME,cfg.TABLE_NAME))
      result = cursor.fetchall()
      for i in result:
          ip_list.append(i[0])
  except Exception as e:
      print (e)
  finally:
      cursor.close()
      conn.close()
  return ip_list

def get_data(ip_lst):
    url = "https://api2.stmbuy.com/gameitem/list.json"
    headers = {
      'Origin': "https://www.stmbuy.com",
      'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"
      }

    for i in range(20):
      proxy = {'http': 'http://' + random.choice(ip_lst)}
      querystring = {"row":"20","page":"{}".format(i+1),"appid":"570","category_id":"","showseek":"1","filter":"{}","sort":"-on_seek_price_max"}
      r = requests.request("GET", url, headers=headers, proxies=proxy, params=querystring)
      save_data2db(json.loads(r.text))
      time.sleep(0.5)


def save_data2db(dts):
  lst = []
  for dt in dts['data']:
    on_seek_price_max = dt.get('on_seek_price_max',0)
    on_seek_price_min = dt.get('on_seek_price_min',0)
    market_name = dt.get('market_name','unknown').replace("'",'')
    on_sale_price_max = dt.get('on_sale_price_max',0)
    on_sale_price_min = dt.get('on_sale_price_min',0)
    sale_count = dt.get('sale_count',0)
    market_price = dt.get('market_price',0)
    on_sale_count = dt.get('on_sale_count',0)
    on_seek_count = dt.get('on_seek_count',0)
    last_price = dt.get('last_price',0)
    itime =  datetime.datetime.fromtimestamp(dt.get('itime',0))
    utime = datetime.datetime.fromtimestamp(dt.get('utime',0))
    market_hash_name = dt.get('market_hash_name','unknown').replace("'",'')

    lst.append([on_seek_price_max,on_seek_price_min,market_name,on_sale_price_max,on_sale_price_min,sale_count,
                market_price,on_sale_count,on_seek_count,last_price,itime,utime,market_hash_name])
  # new_col = ['on_seek_price_max','on_seek_price_min','market_name','on_sale_price_max','on_sale_price_min',
  #   'sale_count','market_price','on_sale_count','on_seek_count','last_price','itime','utime','market_hash_name']
  # df = pd.DataFrame(lst)
  # df.columns = col_name

  # store valid proxies into db.
  print ("\n>>>>>>>>>>>>>>>>>>>> Insert to database Start  <<<<<<<<<<<<<<<<<<<<<<")
  conn = psycopg2.connect(host=cfg.host, port=cfg.port, user=cfg.user, password=cfg.passwd,database=cfg.DB_NAME)
  cursor = conn.cursor()
  for i,t in enumerate(lst):
    sql = '''INSERT INTO jiake.game_stmbuy_goods(on_seek_price_max,on_seek_price_min,market_name,on_sale_price_max,on_sale_price_min,sale_count,
      market_price,on_sale_count,on_seek_count,last_price,itime,utime,market_hash_name) VALUES({},{}, '{}',{}, {},{}, {},{},
      {}, {},'{}','{}','{}')'''.format(*t)
    cursor.execute(sql)
    conn.commit()
    print (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"insert successfully."+str(i+1),end='\r')
  print( ">>>>>>>>>>>>>>>>>>>> Insert to database Ended  <<<<<<<<<<<<<<<<<<<<<<")

if __name__ == '__main__':
  ip_list = get_proxy()
  get_data(ip_list)

