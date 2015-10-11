#!/usr/bin/python -tt
# encoding=utf-8

import sys
import urllib
import urllib2
import cookielib
import json
import time
import re
import os

from bs4 import BeautifulSoup

class renrenSpider:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.domain = 'renren.com'
        self.id = ''
        self.sid = ''
        try:
            self.cookie = cookielib.CookieJar()
            self.cookieProc = urllib2.HTTPCookieProcessor(self.cookie)
        except:
            raise
        else:
            opener = urllib2.build_opener(self.cookieProc)
            opener.addheaders = [('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')]
            urllib2.install_opener(opener)

    def login(self):
        url = 'http://www.renren.com/PLogin.do'
        postdata = {
            'email':email,
            'password':password,
        }

        req = urllib2.Request(url, urllib.urlencode(postdata))
        index = urllib2.urlopen(req).read()
        indexSoup = BeautifulSoup(index,'lxml')

        indexFile = open('index.html','w')
        indexFile.write(indexSoup.prettify())
        indexFile.close()

    def getSub(self, start_id, end_id, filename):
        url_base = 'http://follow.renren.com/list/'
        subf = open(filename, 'a')
        for cid in range(start_id, end_id + 1):
            print 'now crawling sub list id --> ' + str(cid)
            url_getcount = url_base + str(cid) + '/submore?offset=0&limit=1'
            subdata_str = urllib2.urlopen(url_getcount).read()
            subdict = json.loads(subdata_str)
            if json.loads(subdata_str)['code'] != 0:
                subcount = 0
                continue
            else:
                subcount = subdict['data']['subscriberCount']
                print 'subcount = ' + str(subcount)

            if subcount < 500:
                url_getsub = url_base + str(cid) + '/submore?offset=0&limit=' + str(subcount)
                print url_getsub
                subdata_str = urllib2.urlopen(url_getsub).read()
                subdict = json.loads(subdata_str,encoding='utf-8')
                #获取当前查询结果中的用户数量
                cnt = len(subdict['data']['userList'])
                subdata_list = []
                for num in range(cnt):
                    subdata_summary = {}
                    subdata_summary['id'] = subdict['data']['userList'][num]['id']
                    subdata_summary['name'] = subdict['data']['userList'][num]['name']
                    subdata_summary['info'] = subdict['data']['userList'][num]['profileInfo']
                    subdata_summary['subcnt'] = subdict['data']['userList'][num]['subscriberCount']
                    subdata_summary['subto'] = cid
                    subdata_list.append(subdata_summary)
                subf.write(json.dumps(subdata_list))
            else:
                offset_num = 0
                limit_num = 500
                subdata_list = []
                while offset_num < subcount:
                    url_getsub = url_base + str(cid) + '/submore?offset=' + str(offset_num) + '&limit=' + str(limit_num)
                    print url_getsub
                    subdata_str = urllib2.urlopen(url_getsub).read()
                    subdict = json.loads(subdata_str,encoding='utf-8')
                    #获取当前查询结果中的用户数量
                    cnt = len(subdict['data']['userList'])
                    for num in range(cnt):
                        subdata_summary = {}
                        subdata_summary['id'] = subdict['data']['userList'][num]['id']
                        subdata_summary['name'] = subdict['data']['userList'][num]['name']
                        subdata_summary['info'] = subdict['data']['userList'][num]['profileInfo']
                        subdata_summary['subcnt'] = subdict['data']['userList'][num]['subscriberCount']
                        subdata_summary['subto'] = cid
                        subdata_list.append(subdata_summary)
                    offset_num += 500
                    print 'id = ' + str(cid) + ', subcount = ' + str(subcount) + ', offset = ' + str(offset_num)
                subf.write(json.dumps(subdata_list))
            #抓取完一个用户的关注者列表后,换行处理
            subf.write('\n')
        subf.close()

    def getPub(self, start_id, end_id, filename):
        pubf = open(filename, 'a')
        url_base = 'http://follow.renren.com/list/'
        for cid in range(start_id, end_id + 1):
            print 'now crawling pub id--> ' + str(cid)
            url_getcount = url_base + str(cid) + '/pubmore?offset=0&limit=1'
            pubdata_str = urllib2.urlopen(url_getcount).read()
            pubdict = json.loads(pubdata_str)
            if pubdict['code'] != 0:
                pubcount = 0
                continue
            else:
                pubcount = pubdict['data']['publisherCount']
                print str(cid) + ' pubcount = ' + str(pubcount)
            print 'pubcount = ' + str(pubcount)
            pubdata_list = []
            if pubcount < 500:
                url_getpub = url_base + str(cid) + '/pubmore?offset=0&limit=' + str(pubcount)
                print url_getpub
                pubdata_str = urllib2.urlopen(url_getpub).read()
                pubdict = json.loads(pubdata_str,encoding='utf-8')
                #获取当前查询结果中的用户数量
                cnt = len(pubdict['data']['userList'])
                for num in range(cnt):
                    pubdata_summary = {}
                    pubdata_summary['id'] = pubdict['data']['userList'][num]['id']
                    pubdata_summary['name'] = pubdict['data']['userList'][num]['name']
                    pubdata_summary['info'] = pubdict['data']['userList'][num]['profileInfo']
                    pubdata_summary['subcnt'] = pubdict['data']['userList'][num]['subscriberCount']
                    pubdata_summary['authinfo'] = pubdict['data']['userList'][num]['authInfo']
                    pubdata_summary['subby'] = cid
                    pubdata_list.append(pubdata_summary)
                pubf.write(json.dumps(pubdata_list))
            else:
                offset_num = 0
                limit_num = 500
                while offset_num < pubcount:
                    url_getpub = url_base + str(cid) + '/pubmore?offset=' + str(offset_num) + '&limit=' + str(limit_num)
                    pubdata_str = urllib2.urlopen(url_getpub).read()
                    pubdict = json.loads(pubdata_str,encoding='utf-8')
                    #获取当前查询结果中的用户数量
                    cnt = len(pubdict['data']['userList'])
                    for num in range(cnt):
                        pubdata_summary = {}
                        pubdata_summary['id'] = pubdict['data']['userList'][num]['id']
                        pubdata_summary['name'] = pubdict['data']['userList'][num]['name']
                        pubdata_summary['info'] = pubdict['data']['userList'][num]['profileInfo']
                        pubdata_summary['subcnt'] = pubdict['data']['userList'][num]['subscriberCount']
                        pubdata_summary['authinfo'] = pubdict['data']['userList'][num]['authInfo']
                        pubdata_summary['subby'] = cid
                        pubdata_list.append(pubdata_summary)
                    pubf.write(json.dumps(pubdata_list))
                    offset_num += 500
                    print 'id = ' + str(cid) + ', pubcount = ' + str(pubcount) + ', offset = ' + str(offset_num)
            pubf.write('\n')
        pubf.close()

if __name__ == '__main__':
    email = raw_input('email: ')
    password = raw_input('password: ')
    reload(sys)
    sys.setdefaultencoding('utf-8')
    renrenlogin = renrenSpider(email,password)
    renrenlogin.login()
    start_id = 725807834
    end_id = 725807834
    subfile = str(start_id)+'_'+str(end_id)+'_sub.txt'
    renrenlogin.getSub(start_id, end_id, subfile)
    pubfile = str(start_id)+'_'+str(end_id)+'_pub.txt'
    renrenlogin.getPub(start_id, end_id, pubfile)


    needtocrawlids = []
    f = open(pubfile, 'r')
    for linetext in f.readlines():
        linelist = json.loads(linetext, encoding='utf-8')
        cnt = len(linelist)
        for i in range(cnt):
            needtocrawlids.append(linelist[i]['id'])

    f = open(subfile, 'r')
    for linetext in f.readlines():
        linelist = json.loads(linetext, encoding='utf-8')
        cnt = len(linelist)
        for i in range(cnt):
            needtocrawlids.append(linelist[i]['id'])
    f.close()
    for cid in needtocrawlids:
        renrenlogin.getSub(cid, cid, str(start_id)+'_sub.txt')
        renrenlogin.getPub(cid, cid, str(start_id)+'_pub.txt')
    print done
