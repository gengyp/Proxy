Proxy
===============
A tiny tool for crawling, assessing, storing some useful proxies.[中文版](https://github.com/fancoo/Proxy/blob/master/README.zh-cn.md)

### Construct your ip pool
1. First make sure [postgres](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads) has been installed in your machine.
2. 打开连接数据库的客户端（或pgAdmin 4 网页版），将 `db.sql` 中sql 复制到query 中执行
3. modify db connection information in `config.py`.
4. 运行如下代码
```python
# crawl, assess and store proxies
# make sure psycopg2 pkg has been installed
python ip_pool.py

# assess proxies quality in db periodically.
python assess_quality.py
```



### Demo on how to use these proxies.
**Please first construct your ip pool.**

Crawl [github](https://www.github.com/) homepage data:
```python
# visit database to get all proxies
ip_list = []
try:
    cursor.execute('SELECT content FROM %s' % cfg.TABLE_NAME)
    result = cursor.fetchall()
    for i in result:
        ip_list.append(i[0])
except Exception as e:
    print e
finally:
    cursor.close()
    conn.close()

# use this proxies to crawl website
for i in ip_list:
    proxy = {'http': 'http://'+i}
    url = "https://www.github.com/"
    r = requests.get(url, proxies=proxy, timeout=4)
    print r.text
```
More detail in [crawl_demo.py](https://github.com/gengyp/Proxy/blob/master/crawl_demo.py)。

### Contact
gengyanpeng12@foxmail.com
