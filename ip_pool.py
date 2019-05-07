# coding:utf-8
import time
import random
import requests
import datetime
import psycopg2

from lxml import etree
# import pymysql as mdb
from multiprocessing import Process, Manager
import config as cfg


class IPFactory(object):
    """
    * crawl
    * evaluation
    * storage
    """

    def __init__(self):
        self.page_num = cfg.page_num
        self.timeout = cfg.timeout
        self.all_ip = set()

        # init database
        # self.create_db()

    def create_db(self):
        """
        default database is linzi,default schema is jiake
        create table.
        """
        '''sql statement'''
        create_table_str = """CREATE TABLE {}.{}(
          id SERIAL PRIMARY KEY,
          content varchar(30) NOT NULL,
          test_times int NOT NULL DEFAULT 0,
          failure_times int NOT NULL DEFAULT 0,
          success_rate NUMERIC NOT NULL DEFAULT 0.00,
          avg_response_time NUMERIC NOT NULL DEFAULT 0,
          score NUMERIC NOT NULL DEFAULT 0.00,
          create_time DEFAULT CURRENT_TIMESTAMP
        );""".format(cfg.SCHEMA_NAME,cfg.TABLE_NAME)

        # database connection
        # conn = mdb.connect(cfg.host, cfg.user, cfg.passwd)  # mysql
        conn = psycopg2.connect(host=cfg.host, port=cfg.port, user=cfg.user, password=cfg.passwd,database=cfg.DB_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute(create_table_str)
            conn.commit()
        except OSError:
            print ("cannot create table! please check your connection.")
        finally:
            cursor.close()
            conn.close()

    def get_content(self, url, headers, url_xpath, port_xpath):
        """
        parse web html using xpath
        return ip list.
        """
        ip_list = []

        try:
            results = requests.get(url, headers=headers, timeout=4)
            tree = etree.HTML(results.text)

            # parse [ip:port] pairs.
            ips = [line.strip() for line in tree.xpath(url_xpath)]
            ports = [line.strip() for line in tree.xpath(port_xpath)]

            if len(ips) == len(ports):
                for i in range(len(ips)):
                    # match each ip with it's port to the format like "127.0.0.1:80"
                    full_ip = ips[i]+":"+ports[i]

                    # if current ip has been crawled
                    if full_ip in self.all_ip:
                        continue
                    ip_list.append(full_ip)
        except Exception as e:
            print ('get proxies error: ', e)

        return ip_list

    def get_all_ip(self):
        """
        merge the ip crawled from several websites.
        """
        current_all_ip = set()

        ##################################
        # 66ip (http://www.66ip.cn/)
        ###################################
        headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
          'Accept-Encoding': 'gzip, deflate',
          'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
          'Connection': 'keep-alive',
          'Cookie': '__jsluid=15b7448e51f7b794a2c866666c1ed9ec; __jsl_clearance=1556417585.047|0|%2BjpvyhSJn%2BGq843RJfT8JlA0heQ%3D; Hm_lvt_1761fabf3c988e7f04bec51acd4073f4=1556372899,1556378485,1556417587; Hm_lpvt_1761fabf3c988e7f04bec51acd4073f4=1556417596',
          'Host': 'www.66ip.cn',
          'Referer': 'http://www.66ip.cn/index.html',
          'Upgrade-Insecure-Requests': '1',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
        url_xpath_66 = '/html/body//table//tr[position()>1]/td[1]/text()'
        port_xpath_66 = '/html/body//table//tr[position()>1]/td[2]/text()'
        for i in range(self.page_num):
            url_66 = 'http://www.66ip.cn/' + str(i+1) + '.html'
            results = self.get_content(url_66, headers, url_xpath_66, port_xpath_66)
            print('current url is {} total num is {}'.format(url_66,len(results)))

            if len(results):
                self.all_ip.update(results)
                current_all_ip.update(results)
                # wait 0.5 secs.
                time.sleep(0.5)

        ##################################
        # xicidaili (http://www.xicidaili.com/nn/)
        ###################################
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
        url_xpath_xici = '//table//tr[position()>1]/td[2]/text()'
        port_xpath_xici = '//table//tr[position()>1]/td[position()=3]/text()'
        for i in range(self.page_num):
            url_xici = 'http://www.xicidaili.com/nn/' + str(i+20)
            results = self.get_content(url_xici, headers, url_xpath_xici, port_xpath_xici)
            print('current url is {} total num is {}'.format(url_xici,len(results)))
            self.all_ip.update(results)
            current_all_ip.update(results)
            time.sleep(0.5)

        ##################################
        # kuaidaili (http://www.kuaidaili.com/)
        ###################################
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
        url_xpath_kuaidaili = '//table//td[1]/text()'
        port_xpath_kuaidaili = '//td[@data-title="PORT"]/text()'
        for i in range(self.page_num):
            url_kuaidaili = 'http://www.kuaidaili.com/free/inha/' + str(i+10) + '/'
            results = self.get_content(url_kuaidaili, headers, url_xpath_kuaidaili, port_xpath_kuaidaili)
            print('current url is {} total num is {}'.format(url_kuaidaili,len(results)))
            self.all_ip.update(results)
            current_all_ip.update(results)
            time.sleep(0.5)

        print(">>>>>>>>>>>>>> All proxies has been crawled <<<<<<<<<<<")
        return current_all_ip

    def get_valid_ip(self, ip_set, manager_list, timeout):
        """
        test if ip is valid.
        """
        # request url.
        # url = 'http://httpbin.org/get?show_env=1'
        # url = 'http://github.com'
        url = 'https://buff.163.com/market/?game=dota2#tab=buying&page_num=1'

        # check proxy one by one
        for p in ip_set:
            proxy = {'http': 'http://'+p}
            try:
                start = time.time()
                r = requests.get(url, proxies=proxy, timeout=timeout)
                end = time.time()

                # judge if proxy valid
                if r.status_code == 200:
                    print ('succeed: ' + p + '\t' + " succeed in " + format(end-start, '0.4f') + 's!',end='\r')
                    # add to result
                    manager_list.append(p)
            except Exception:
                print (p + "\t timeout.")

    def multi_thread_validation(self, ip_set, manager_list, timeout, thread=50):
        """
        use multiple process to accelerate the judgement of valid proxies.
        """
        if len(ip_set) < thread:
            thread = len(ip_set)

        # divide ip_set to blocks for later multiprocess.
        slice_len = len(ip_set) / thread

        jobs = []
        for i in range(thread-1):
            part = set(random.sample(ip_set, slice_len))
            ip_set -= part
            p = Process(target=self.get_valid_ip, args=(part, manager_list, timeout))
            jobs.append(p)
            p.start()

        # the last slice of ip_set.
        p = Process(target=self.get_valid_ip, args=(ip_set, manager_list, timeout))
        p.start()
        jobs.append(p)

        # join threads
        for job in jobs:
            if job.is_alive():
                job.join()

    def save_to_db(self, valid_ips):
        """
        save all valid proxies into db
        """
        if len(valid_ips) == 0:
            print ("not proxy available for this time.")
            return

        # store valid proxies into db.
        print ("\n>>>>>>>>>>>>>>>>>>>> Insert to database Start  <<<<<<<<<<<<<<<<<<<<<<")
        # conn = mdb.connect(cfg.host, cfg.user, cfg.passwd, cfg.DB_NAME)
        conn = psycopg2.connect(host=cfg.host, port=cfg.port, user=cfg.user, password=cfg.passwd,database=cfg.DB_NAME)
        cursor = conn.cursor()
        try:
            for item in valid_ips:
                # check if current ip exists.
                sql = "SELECT * FROM {}.{} WHERE content='{}'".format(cfg.SCHEMA_NAME,cfg.TABLE_NAME, item)
                cursor.execute(sql)

                # it's new ip
                if len(cursor.fetchall())==0:
                  sql = '''INSERT INTO {}.{}(content,test_times,failure_times,success_rate,avg_response_time,score)
                          VALUES('{}', 1, 0, 0, 1.0, 2.5)'''.format(cfg.SCHEMA_NAME,cfg.TABLE_NAME, item)
                  cursor.execute(sql)
                  conn.commit()
                  print (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" "+item+" insert successfully.",end='\r')
                else:
                  print (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" "+ item + " exists.")
        except Exception as e:
            print ("store to db failed：" + str(e))
        finally:
            cursor.close()
            conn.close()
        print( ">>>>>>>>>>>>>>>>>>>> Insert to database Ended  <<<<<<<<<<<<<<<<<<<<<<")
        print ("Finished.")

    def get_proxies(self, manager_list):
        ip_list = []

        # db connection
        conn = mdb.connect(cfg.host, cfg.user, cfg.passwd, cfg.DB_NAME)
        cursor = conn.cursor()

        try:
            ip_exist = cursor.execute('SELECT * FROM %s ' % cfg.TABLE_NAME)
            result = cursor.fetchall()

            # if exists proxies in db, fetch and return.
            if len(result):
                for item in result:
                    ip_list.append(item[0])
            else:
                # crawl more proxies.
                current_ips = self.get_all_ip()
                self.multi_thread_validation(current_ips, manager_list, cfg.timeout)
                valid_ips = manager_list
                self.save_to_db(valid_ips)
                ip_list.extend(valid_ips)
        except Exception as e:
            print ("get ip from database failed." + str(e))
        finally:
            cursor.close()
            conn.close()

        return ip_list

def main():
    ip_pool = IPFactory()
    while True:
      manager = Manager()
      manager_list = manager.list()
      current_ips = ip_pool.get_all_ip()
      ip_pool.multi_thread_validation(current_ips, manager_list, cfg.timeout)
      # print ("\n>>>>>>>>>>>>> Valid proxies <<<<<<<<<<")
      ip_pool.save_to_db(manager_list)
      time.sleep(cfg.CHECK_TIME_INTERVAL)


if __name__ == '__main__':
  # main()
  ip_pool = IPFactory()
  while True:
    # manager = Manager()
    # manager_list = manager.list()
    manager_list = []
    current_ips = ip_pool.get_all_ip()
    ip_pool.get_valid_ip(current_ips, manager_list, cfg.timeout)
    print ("\n>>>>>>>>>>>>> Valid proxies <<<<<<<<<<")
    ip_pool.save_to_db(manager_list)
    time.sleep(cfg.CHECK_TIME_INTERVAL)
