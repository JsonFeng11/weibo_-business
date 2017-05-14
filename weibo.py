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
myUserId = ''
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
    'User-Agent' : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:50.0) Gecko/20100101 Firefox/50.0",
    'Accept' : '*/*',
    }


# model
class Person:
    def __init__(self, userID, name, fans):
        self.name = name
        self.fans = fans
        self.userID = userID
# class userModel:
#     def __init__(self, uid, name):
#         self.uid = uid
#         self.name = name


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
    text = rq.text
    num1 = text.find("$CONFIG['uid']=")
    num2 = text.find("$CONFIG['onick']=")
    str2 = text[num2 + 1 : 40]
    num3 =  str2.rfind("';")
    # user['userID'] = text[num1+1 : num1 + 11]
    # user['name'] = str2[1:num3]
    user = Person(text[num1+1 : num1 + 11], str2[1:num3], '')
    myUserId = text[num1 + 16: num1 + 26]
    print '000000' , myUserId

    print 'log success'


user = Person("", "", "")
login('phone', 'psd')





#-------------------------------------------------------
# 获取全部列表  我的id:2529091407 ,在这里关注的时候必须在headers里加Referer,踩了好多坑
param = '0002_2975_1002_0'
all_url = 'http://d.weibo.com/108703' + param + '?' + 'page='#体育 ?ajaxpagelet=1&__ref=/1087030002_2975_1002_0
curpage = 1
nextData = {
    'pids' : 'Pl_Core_F4RightUserList__4',
    'ajaxpagelet' : '1',
    '__ref' : '/1087030002_2975_1002_0',
}





def followCurpagePer(page):
    print "+++++++++++第%d页++++++++++++" % page
    allurltemp = all_url
    allurltemp = allurltemp + str(page)
    print allurltemp
    r = s.get(url=allurltemp)
    text = r.text.encode('utf-8')
    a = text.count("follow_item S_line2")
    num = text.find('follow_item S_line2')
    text = text[num : len(text)]
    print a
    ids = []
    for x in range(a):
        num1 = text.find('usercard=')
        num2 = text.find('title=')
        num3 = text.find('粉丝')
        userid = text[num1 + 14 : num1 + 24]
        str2 = text[num2 + 8: num2 + 52]
        s2 = str2.rfind('\" ')
        title = str2[0:(s2-1)]
        str3 = text[num3 + 26 : num3 + 36]
        s3 = str3.rfind('<')
        fans = str3[0:s3]
        # print userid, title, fans
        per = Person(userid, title, fans)
        ids.append(per)
        text = text[num3 + 50 : len(text)]

    countPer = 0
    # 关注粉丝大于1000万的人
    for a in range(len(ids)):
        p = ids[a]
        if "万" in p.fans:
            count = str(p.fans)[0 : (len(p.fans) - 3)]
            if int(count) >= 100:
                countPer = int(countPer) + 1
                followData['uid'] = p.userID
                print p.name
                r = s.post(url=follow_url, data=followData, headers=headers)
                # print r.text, r.status_code
    print '在本页关注了%s个人' % str(countPer)
    # print ids
    print '----------'
    #操作完成以后
    # headers.pop('Referer')


# 关注参数,需要子啊header里加refer
follow_url = 'http://d.weibo.com/aj/f/followed?ajwvr=6&__rnd=' + str(time.time()).replace('.', '') + '6' # __rnd=1494415341464
followData = {
    'uid' : '',
    'objectid' : '',
    'f' : '1',
    'extra' : '',
    'refer_sort' : '',
    'refer_flag' : '1087030701_2975_1002_0',
    'location' : 'page_1087030002_2975_1002_0_home',
    'oid' : param,
    'wforce' : '1',
    'nogroup' : 'false',
    'template' : '1',
    '_t' : '0',
    # 'fnick' : ''
}
headers['Referer'] = 'http://d.weibo.com/108703' + param

# 取消关注参数
allfollow_url = 'http://weibo.com/p/1005056243373121/myfollow?t=1&cfs=&Pl_Official_RelationMyfollow__93_page='
unallfollow_url = 'http://weibo.com/aj/f/unfollow?ajwvr=6'
allPage = 1

unFollowData = {
    'uid' : '',
    'objectid' : '',
    'f' : '1',
    'extra' : '',
    'refer_sort' : '',
    # 'refer_flag' : 'followed&refer_flag=0000020001_',
    'refer_flag' : '0000020001_&refer_flag=followed',
    # 'refer_flag' : 'followed',
    # 'refer_flag' : '0000020001_',
    'location' : 'page_100505_myfollow',
    'oid' : '',
    'wforce' : '1',
    'nogroup' : 'false',
    'fnick' : '',
    'template' : '1',
    'refer_lflag' : '',
}

# 循环页数
# while curpage <= 2:
#     followCurpagePer(curpage)
#     curpage = curpage + 1

#-------------------------------------------------------

# 判断字符串是否只有中文(暂时没有判断id含有数字的)

def check_contain_chinese(check_str):
    count = len(check_str)
    num = 0
    for ch in check_str.decode('utf-8'):
        if (u'\u4e00' <= ch <= u'\u9fff'):
            num = num + 1
    if num == count/3:
        return True
    else:
        return False

#  获取所有关注
def getCurPageFollwed(page):
    # if headers.has_key('Referer'):
    #     del headers['Referer']
    url = allfollow_url + str(page)
    headers['Referer'] = url
    headers['Host'] = 'weibo.com'
    # Content-Type:

    # headers['Origin'] = 'http://weibo.com'
    # headers['X-Requested-With'] = 'XMLHttpRequest'
    # headers['Accept'] = '*/*'
    # Origin:http://weibo.com

    allr = s.get(allfollow_url)
    # print allr.text
    text = allr.text.encode('utf-8')
    a = text.count('member_li S_bg1')
    num = text.find('member_li S_bg1')
    text = text[num : len(text)]
    print a
    ids = []
    userids = []
    for x in range(a):
        num1 = text.find('usercard=')
        num2 = text.find('title=')
        # num3 = text.find('粉丝')
        userid = text[num1 + 14: num1 + 24]
        str2 = text[num2 + 8: num2 + 40]
        s2 = str2.rfind('\" ')
        title = str2[0:(s2 - 1)]
        # str3 = text[num3 + 26: num3 + 36]
        # s3 = str3.rfind('<')
        # fans = str3[0:s3]
        print userid, title
        userids.append(userid)
        per = Person(userid, title, '')
        isR = check_contain_chinese(per.name)
        if isR:
            # print per, ids
            if per not in ids:
                ids.append(per)
                print '++++' + per.name
        text = text[num1 + 350 : len(text)]
    print len(ids)

    # unfollow(ids)
    return ids
    # 取消本页所有关注,需要在header里加host
    # for a in range(len(ids)):
    #     if a != 1:
    #         continue
    #     per = ids[a]
    #     global unFollowData
    #     unFollowData['uid'] = per.userID
    #     unFollowData['oid'] = '6243373121'
    #     unFollowData['fnick'] = per.name
    #     print unallfollow_url, per.name, per.userID, unFollowData, headers
    #     tt = s.post(url=unallfollow_url, data=json.dumps(unFollowData), headers=headers)
    #     print tt.text, tt.status_code

def unfollow(ids):
    # 取消本页所有关注,需要在header里加host
    for a in range(len(ids)):
        if a != 1:
            continue
        per = ids[a]
        global unFollowData
        unFollowData['uid'] = per.userID
        unFollowData['oid'] = '6243373121'
        unFollowData['fnick'] = per.name
        print unallfollow_url, per.name, per.userID, unFollowData, headers
        tt = s.post(url=unallfollow_url, data=json.dumps(unFollowData), headers=headers)
        print tt.text, tt.status_code


# getCurPageFollwed(1)

#-------------------------------------------------------

# 获取动态并点赞
# 个人主页url
perUrl = 'http://weibo.com/u/%s?from=myfollow_all&is_all=1'

# 取消收藏,把add变为del
collectUrl = 'http://weibo.com/aj/fav/mblog/add?ajwvr=6'

# 该方法是点赞行为,如果已点赞,则为取消点赞.反之则为点赞.
admireUul = 'http://weibo.com/aj/v6/like/add?ajwvr=6&__rnd=' + str(time.time()).replace('.', '')

admireData = {
    'location' : 'page_100505_home',
    'version' : 'mini',
    'qid' : 'heart',
    'mid' : '',
    'loc' : 'profile',
    '_t' : '0'
}
collectData = {
    'mid' : '',
    'location' : 'page_100505_home'
}

allFollow = getCurPageFollwed(1)
# print allFollow
pp = Person('', '', '')
pp = allFollow[2]
print '-------------------'
print pp.userID, pp.name,perUrl % pp.userID
ar = s.get(perUrl % pp.userID)
# print ar.text
wantText = ar.text
wantNum = wantText.find('WB_cardwrap WB_feed_type S_bg2')
wantUid = wantText[wantNum - 40 + 10 + 2 : wantNum - 12]
print wantUid

# 收藏
def collectiong(wantUid):
    collectData['mid'] = str(wantUid)
    headers['Referer'] = perUrl
    print collectData, collectUrl, headers
    collectResponse = s.post(url=collectUrl, headers=headers, data=collectData)
    print collectResponse.text

# 点赞
def admire(wantUid):
    admireData['mid'] = str(wantUid)
    headers['Referer'] = perUrl
    print admireData, admireUul,
    admireResponse = s.post(url=admireUul, headers=headers, data=admireData)
    print admireResponse.text

admire(wantUid)