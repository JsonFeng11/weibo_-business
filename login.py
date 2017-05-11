# !/usr/bin/env python
# coding=utf8

import urllib
import base64
import re
import json
import rsa
import binascii
import requests
from lxml import etree
import xpath
import time
import random

# from setting import getAgent

# 预登陆url
prelogin_url = "https://login.sina.com.cn/sso/prelogin.php?"
# 登录url
login_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'

categoryUrl = 'http://weibo.com/aj/v6/user/newcard?'

# 预登陆参数
parameters = {
    'entry': 'weibo',
    'callback': 'sinaSSOController.preloginCallBack',
    'su': '',
    'rsakt': 'mod',
    'client': 'ssologin.js(v1.4.18)',
    '_': '1494208589026'
}
# 登录参数
postdata = {
    'entry': 'weibo',
    'gateway': '1',
    'from': '',
    'savestate': '7',
    'useticket': '1',
    'pagerefer': '',
    'vsnf': '1',
    'su': '',
    'service': 'miniblog',
    'servertime': '',
    'nonce': '',
    'pwencode': 'rsa2',
    'rsakv': '',
    'sp': '',
    'encoding': 'UTF-8',
    'prelt': '27',
    'url': 'http://www.weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
    'returntype': 'META'
}

headers = {
    'User-Agent' : "Mozilla/5.0 (Linux; U; Android 1.6; en-us; SonyEricssonX10i Build/R1AA056) AppleWebKit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1",
    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }



# 这里用requests库来处理cookie
s = requests.session()

# 从预登录中获取需要的参数
def get_servertime():
    r = s.get(url=prelogin_url,params=parameters)
    p = r.text[35:len(r.text)-1]
    data = json.loads(p)
    servertime = data['servertime']
    nonce = data['nonce']
    pubkey = data['pubkey']
    rsakv = data['rsakv']
    # print servertime, nonce, pubkey, rsakv
    return servertime, nonce, pubkey, rsakv

# 过去加密的密码
def get_pwd(pwd, servertime, nonce, pubkey):
    rsaPublickey = int(pubkey, 16)
    key = rsa.PublicKey(rsaPublickey, 65537)  # 创建公钥
    message = str(servertime) + '\t' + str(nonce) + '\n' + str(pwd)  # 拼接明文 js加密文件中得到
    passwd = rsa.encrypt(message.encode(encoding="utf-8"), key)  # 加密
    passwd = binascii.b2a_hex(passwd)  # 将加密信息转换为16进制
    return passwd

# 获取加密的用户名
def get_user(username):
    username_ = urllib.quote(username)
    username = base64.encodestring(username_)[:-1]
    return username

# 登录
def login(username, pwd):
    servertime, nonce, pubkey, rsakv = get_servertime()
    global postdata
    postdata['servertime'] = servertime
    postdata['nonce'] = nonce
    postdata['rsakv'] = rsakv
    postdata['su'] = get_user(username)
    postdata['sp'] = get_pwd(pwd, servertime, nonce, pubkey)
    # print postdata

    r = s.post(url=login_url, data=postdata, headers=headers)
    # print r.text,r.status_code

    p = re.compile('location\.replace\(\'(.*?)\'\)')
    p2 = re.compile(r'"userdomain":"(.*?)"')
    url = p.search(r.text).group(1)
    page = s.get(url=url)
    # print page.text
    lurl = 'http://weibo.com/' + p2.search(page.text).group(1)
    rq = s.get(lurl)
    # print rq.text

