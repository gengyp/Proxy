#!/user/bin/env python
# -*- coding:utf-8 -*-
#
# @author   Ringo
# @email    myfancoo@qq.com
# @date     2016/10/12

import requests
import time
import json
import datetime
import logging
import psycopg2
# import pymysql as mdb
import config as cfg

"""
Assess an score the proxies
"""

log_file = 'assess_logger.log'
logging.basicConfig(filename=log_file, level=logging.WARNING)

TEST_ROUND_COUNT = 0


def modify_score(ip, success, response_time):
    # type = 0 means ip hasn't pass the test

    # database connection
    # conn = mdb.connect(cfg.host, cfg.user, cfg.passwd, cfg.DB_NAME)
    conn = psycopg2.connect(host=cfg.host, port=cfg.port, user=cfg.user, password=cfg.passwd,database=cfg.DB_NAME)
    cursor = conn.cursor()

    # timeout
    if success == 0:
        logging.warning(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+": " + ip + " out of time")
        try:
            cursor.execute("SELECT * FROM {}.{} WHERE content='{}'".format(cfg.SCHEMA_NAME,cfg.TABLE_NAME,ip))
            r = cursor.fetchall()[0]

            test_times = r[2] + 1
            failure_times = r[3]
            success_rate = r[4]
            avg_response_time = r[5]

            # when an IP (timeout up to 4 times) && (SUCCESS_RATE lower than a threshold), discard it.
            if failure_times > 4 and success_rate < cfg.SUCCESS_RATE:
                # cursor.execute('DELETE FROM %s WHERE content= "%s"' % (cfg.TABLE_NAME, ip))
                cursor.execute("DELETE FROM {}.{} WHERE content='{}'".format(cfg.SCHEMA_NAME,cfg.TABLE_NAME,ip))
                conn.commit()
                logging.warning(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+": " + ip + " was deleted.")
            else:
                # not fatal
                failure_times += 1
                success_rate = 1 - float(failure_times) / test_times
                avg_response_time = (avg_response_time * (test_times - 1) + cfg.TIME_OUT_PENALTY) / test_times
                score = (success_rate + float(test_times) / 500) / avg_response_time
                update_sql = "UPDATE {}.{} SET test_times={},failure_times={},success_rate={:.2f},avg_response_time={:.2f},score={:.2f} WHERE content='{}'".format(
                    cfg.SCHEMA_NAME,cfg.TABLE_NAME,test_times, failure_times, success_rate, avg_response_time, score, ip)
                cursor.execute(update_sql)
                # n = cursor.execute('UPDATE %s SET test_times = %d, failure_times = %d, success_rate = %.2f, avg_response_time = %.2f, score = %.2f WHERE content = "%s"' % (cfg.TABLE_NAME, test_times, failure_times, success_rate, avg_response_time, score, ip))
                conn.commit()
                # if n:
                logging.error(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+": " + ip + ' has been modify successfully!')
        except Exception as e:
            logging.error(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+": " + 'Error when try to delete ' + ip + str(e))
        finally:
            cursor.close()
            conn.close()
    elif success == 1:
        # pass the test
        try:
            cursor.execute("SELECT * FROM {}.{} WHERE content='{}'".format(cfg.SCHEMA_NAME,cfg.TABLE_NAME,ip))
            r = cursor.fetchall()[0]

            test_times = r[2] + 1
            failure_times = r[3]
            avg_response_time = r[5]

            success_rate = 1 - float(failure_times) / test_times
            avg_response_time = (avg_response_time * (test_times - 1) + response_time) / test_times
            score = (success_rate + float(test_times) / 500) / avg_response_time
            # n = cursor.execute('UPDATE %s SET test_times = %d, success_rate = %.2f, avg_response_time = %.2f, score = %.2f WHERE content = "%s"' %(cfg.TABLE_NAME, test_times, success_rate, avg_response_time, score, ip))
            update_sql = "UPDATE {}.{} SET test_times={},failure_times={},success_rate={:.2f},avg_response_time={:.2f},score={:.2f} WHERE content='{}'".format(cfg.SCHEMA_NAME,cfg.TABLE_NAME,test_times, failure_times, success_rate, avg_response_time, score, ip)
            cursor.execute(update_sql)
            conn.commit()
            # if n:
            logging.error(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+": " + ip + 'has been modify successfully!')
        except Exception as e:
            logging.error(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+": " + 'Error when try to modify ' + ip + str(e))
        finally:
            cursor.close()
            conn.close()


def ip_test(proxies, timeout):
    url = 'https://www.baidu.com'
    # url = 'https://httpbin.org/get?show_env=1'
    url = 'https://buff.163.com/market/?game=dota2#tab=selling&page_num=1'
    for p in proxies:
        proxy = {'http': 'http://'+p}
        try:
            start = time.time()
            r = requests.get(url, proxies=proxy, timeout=timeout)
            end = time.time()
            if r.text is not None:
                logging.warning(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+": " + p + " out of time")
                resp_time = end - start
                modify_score(p, 1, resp_time)
                # request_ip = json.loads(r.text)['headers']['X-Real-Ip']
                # print('ip test succeed,proxy is:{}\trequest ip is:{}\ttest time is:{}'.format(p,request_ip,resp_time))
                print('ip test succeed,proxy is:{}\ttest time is:{}'.format(p,resp_time))
        except OSError:
            modify_score(p, 0, 0)


def assess():
    global TEST_ROUND_COUNT
    TEST_ROUND_COUNT += 1
    logging.warning(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+": " + ">>>>\t" + str(TEST_ROUND_COUNT) + " round!\t<<<<")

    # db connection
    # conn = mdb.connect(cfg.host, cfg.user, cfg.passwd, cfg.DB_NAME)
    conn = psycopg2.connect(host=cfg.host, port=cfg.port, user=cfg.user, password=cfg.passwd,database=cfg.DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT content FROM {}.{}".format(cfg.SCHEMA_NAME,cfg.TABLE_NAME))
        result = cursor.fetchall()
        ip_list = []
        for i in result:
            ip_list.append(i[0])
        if len(ip_list) == 0:
            return
        ip_test(ip_list, cfg.timeout)
        print(">>>>> Waiting for the next assessment <<<<<")
        print(">>>>> You can terminate me now if you like <<<<<")
    except Exception as e:
        logging.warning(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+": " + str(e))
    finally:
        cursor.close()
        conn.close()


def main():
    while True:
        assess()
        # schedule
        time.sleep(cfg.CHECK_TIME_INTERVAL)

if __name__ == '__main__':
    # main()
    # 一般一天运行一次即可
    assess()