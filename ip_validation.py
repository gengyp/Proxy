# coding:utf8
import json
import requests

'''
验证是否使用代理 ip 请求
'''
url = "http://httpbin.org/get"
url = 'https://httpbin.org/get?show_env=1'

proxy = {'http':'http://183.148.135.203:9999'}

print('当前代理IP is {}'.format(proxy['http'].split('://')[1]))

querystring = {"show_env":"1"}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

response = requests.request("GET", url, headers=headers, params=querystring,proxies=proxy)
# response = requests.request("GET", url, headers=headers, proxies=proxy)

dts = json.loads(response.text)

print('当前请求IP is {}'.format(dts['headers']['X-Real-Ip']))