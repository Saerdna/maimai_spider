import os
import sys
import requests
import urllib
import random
import json
import pprint

def luhn_residue(digits):
    return sum(sum(divmod(int(d)*(1 + i%2), 10)) for i, d in enumerate(digits[::-1])) % 10
def getImei(N):
    part = ''.join(str(random.randrange(0,9)) for _ in range(N-1))
    res = luhn_residue('{}{}'.format(part, 0))
    return '{}{}'.format(part, -res%10)
class MMSpider:
    def __init__(self, username, passwd, mmid = None, token = None):
        self._login_useragent = "MaiMai_Android"
        self._imei = "285787567615164"
        self._useragent = "Dalvik/1.6.0 (Linux; U; Android 4.4.4; MI 3 MIUI/5.1.7)"
        self._username = username
        self._passwd = passwd
        self._token = token
        self._mmid = mmid
        self._headers = {"Content-Type": "application/x-www-form-urlencoded", "Connection": "Keep-Alive"}
        self._login_url = "https://open.taou.com/maimai/user/v3/login"
        self._degree_one_url = "https://open.taou.com/maimai/contact/v3/rece_d1"
        self._feed_url = "https://open.taou.com/maimai/contact/v3/feed"

    def _login(self):
        if self._token != None and self._mmid != None:
            return
        query = {'u':'', 'access_token':'', 'version':"3.10.8", 'ver_code':'android_955', 'channel':'XiaoMi'}
        url = "%(url)s?%(query)s" % ({'url': self._login_url, 'query': urllib.urlencode(query)})
        body = {'info_type':2, 'account': self._username, 'password': self._passwd, 'dev_type': 3, 'imei': self._imei}
        headers = self._headers
        headers['User-Agent'] = self._login_useragent
        req = requests.post(url, urllib.urlencode(body), headers = headers, verify = False)
        resp = json.loads(req.text)
        self._token = resp['token']
        self._mmid = resp['user']['mmid']
    def get_degree_one(self):
        self._login()
        query = {'u': self._mmid, 'access_token': self._token, 'rece': 1, 'version':"3.10.8", 'ver_code':'android_955', 'channel':'XiaoMi'}
        url = "%(url)s?%(query)s" % ({'url': self._degree_one_url, 'query': urllib.urlencode(query)})
        headers = self._headers
        headers["User-Agent"] = self._useragent
        headers["Charset"] = "UTF-8"
        req = requests.get(url, headers = headers, verify = False)
        resp = json.loads(req.text)
    def get_degree_two(self):
        self._login()
        query = {'u': self._mmid, 'access_token': self._token, 'version':"3.10.8", 'ver_code':'android_955', 'channel':'XiaoMi', 'gl': 1, 'count':20, 'page':23, 'gtype':'a', 'dist':2}
        url = "%(url)s?%(query)s" % ({'url': self._feed_url, 'query': urllib.urlencode(query)})
        headers = self._headers
        headers["User-Agent"] = self._useragent
        headers["Charset"] = "UTF-8"
        req = requests.get(url, headers = headers, verify = False)
        resp = json.loads(req.text)
        for one in resp['contacts']:
            for k,v in one.items():
                print k,v
