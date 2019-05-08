# coding:utf8
import json
import requests

'''
验证是否使用代理 ip 请求
'''
url = "http://httpbin.org/get"

proxy = {'http':'http://114.67.237.32:808'}

print('当前代理IP is {}'.format(proxy['http'].split('://')[1]))

querystring = {"show_env":"1"}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

response = requests.request("GET", url, headers=headers, params=querystring,proxies=proxy)

dts = json.loads(response.text)

print('当前请求IP is {}'.format(dts['headers']['X-Real-Ip']))