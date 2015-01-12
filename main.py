import os
import sys
import requests
import urllib
import random
import json
import pprint
import sqlite3
import time

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
        self._feed_url = "https://open.taou.com/maimai/contact/v3/feed"
        self._detail_url = "https://open.taou.com/maimai/contact/v3/detail2"
    def show_info(self):
        self._login()
        print >> sys.stderr, "mmid:%s\ttoken:%s" % (self._mmid, self._token)
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
    def get_degree(self, dist, pageno):
        self._login()
        query = {'u': self._mmid, 'access_token': self._token, 'version':"3.10.8", 'ver_code':'android_955', 'channel':'XiaoMi', 'gl': 1, 'count':20, 'page': pageno, 'gtype':'a', 'dist':dist}
        url = "%(url)s?%(query)s" % ({'url': self._feed_url, 'query': urllib.urlencode(query)})
        headers = self._headers
        headers["User-Agent"] = self._useragent
        headers["Charset"] = "UTF-8"
        req = requests.get(url, headers = headers, verify = False)
        resp = json.loads(req.text)
        return resp
    def get_detail(self, uid):
        self._login()
        query = {'u': self._mmid, 'access_token': self._token, 'version':"3.10.8", 'ver_code':'android_955', 'channel':'XiaoMi', 'u2': uid}
        headers = self._headers
        headers["User-Agent"] = self._useragent
        headers["Charset"] = "UTF-8"
        url = "%(url)s?%(query)s" % ({'url': self._detail_url, 'query': urllib.urlencode(query)})
        req = requests.get(url, headers = headers, verify = False)
        resp = json.loads(req.text)
        return resp
if __name__ == '__main__':
    print >> sys.stderr, "please input your mobile phone"
    uid = sys.stdin.readline().strip()
    print >> sys.stderr, "please input your password"
    password = sys.stdin.readline().strip()
    spider = MMSpider(uid, password)
    relation_one = spider.get_degree(1, 0)
    conn = sqlite3.Connection("maimai.db")
    cur = conn.cursor()
    try:
        cur.execute('''create table user_info(record_id integer PRIMARY KEY autoincrement, mmid text unique, json text)''')
    except Exception as Exc:
        pass
    page_no = 1
    while relation_one.get('remain', 0) > 0:
        for one in relation_one['contacts']:
            if one['mmid'].isdigit() == False:
                continue
            print >> sys.stderr, one['name'], relation_one.get('remain', 0)
            detail = spider.get_detail(one['mmid'])
            time.sleep(random.randint(5, 10))
            try:
                cur.execute("insert into user_info(mmid, json) values('%s', '%s')" % (one['mmid'], json.dumps(detail)))
                conn.commit()
            except Exception as Exc:
                print >> sys.stderr, Exc
        relation_one = spider.get_degree(1, page_no)
        page_no += 1

    relation_two = spider.get_degree(2, 0)
    page_no = 1
    while relation_two.get('remain', 0) > 0:
        for one in relation_two['contacts']:
            if one['mmid'].isdigit() == False:
                continue
            print >> sys.stderr, one['name'], relation_two.get('remain', 0)
            detail = spider.get_detail(one['mmid'])
            time.sleep(random.randint(5, 10))
            try:
                cur.execute("insert into user_info(mmid, json) values('%s', '%s')" % (one['mmid'], json.dumps(detail)))
                conn.commit()
            except Exception as Exc:
                print >> sys.stderr, Exc
        relation_two = spider.get_degree(2, page_no)
        page_no += 1

    conn.close()
