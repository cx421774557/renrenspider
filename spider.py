#!/usr/bin/python -tt
# encoding=utf-8
#75行有BUG

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
        self.newids = set()
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

    def getSub(self, cid, filename):
        url_base = 'http://follow.renren.com/list/'

        print 'now crawling sub list id --> ' + str(cid)
        #配置获取关注者列表URL, 第一步先查看是否存在关注者
        url_getcount = url_base + str(cid) + '/submore?offset=0&limit=1'
        subdata_str = urllib2.urlopen(url_getcount).read()
        subdict = json.loads(subdata_str)
        if json.loads(subdata_str)['code'] != 0:
            #该ID没有关注者 退出函数
            subcount = 0
            return
        else:
            subcount = subdict['data']['subscriberCount']
            print 'subcount = ' + str(subcount)
            if subcount > 100000:
                with open('sub_too_large.txt', 'a') as f:
                    f.write(str(cid)+' '+str(subcount)+'\n')
                return

        subf = open(filename, 'a')
        subdata_list = []
        if subcount < 500:
            url_getsub = url_base + str(cid) + '/submore?offset=0&limit=' + str(subcount)
            print url_getsub
            subdata_str = urllib2.urlopen(url_getsub).read()
            print subda
            #修复ValueError: Invalid control character at: line 1 column 16842 (char 16841)异常
            subdict = json.loads(subdata_str.replace('\r\n', ''),encoding='utf-8')
            #获取当前查询结果中的用户数量
            cnt = len(subdict['data']['userList'])
            for num in range(cnt):
                #该字典用于存储第个每个用户的精简信息
                subdata_summary = {}
                subdata_summary['id'] = subdict['data']['userList'][num]['id']
                subdata_summary['name'] = subdict['data']['userList'][num]['name']
                subdata_summary['info'] = subdict['data']['userList'][num]['profileInfo']
                subdata_summary['subcnt'] = subdict['data']['userList'][num]['subscriberCount']
                subdata_summary['img'] = subdict['data']['userList'][num]['headUrl']
                #增加一项指向该用户所关注的ID,方便统计用户间关注关系
                subdata_summary['subto'] = cid
                subdata_list.append(subdata_summary)
                self.newids.add(subdata_summary['id'])
            #所有关注者信息抓取完成,写入文件
            subf.write(json.dumps(subdata_list))
        else:
            #当关注者总数超过500个时, 以500为单位分次抓取
            offset_num = 0
            limit_num = 500
            subdata_list = []
            while offset_num < subcount:
                url_getsub = url_base + str(cid) + '/submore?offset=' + str(offset_num) + '&limit=' + str(limit_num)
                print url_getsub
                subdata_str = urllib2.urlopen(url_getsub).read()
                subdict = json.loads(subdata_str.replace('\r\n', ''),encoding='utf-8')
                #获取当前查询结果中的用户数量
                cnt = len(subdict['data']['userList'])
                for num in range(cnt):
                    subdata_summary = {}
                    subdata_summary['id'] = subdict['data']['userList'][num]['id']
                    subdata_summary['name'] = subdict['data']['userList'][num]['name']
                    subdata_summary['info'] = subdict['data']['userList'][num]['profileInfo']
                    subdata_summary['subcnt'] = subdict['data']['userList'][num]['subscriberCount']
                    subdata_summary['img'] = subdict['data']['userList'][num]['headUrl']
                    subdata_summary['subto'] = cid
                    subdata_list.append(subdata_summary)
                    self.newids.add(subdata_summary['id'])
                offset_num += 500
                print 'id = ' + str(cid) + ', subcount = ' + str(subcount) + ', offset = ' + str(offset_num)
            subf.write(json.dumps(subdata_list))
        #抓取完一个用户的关注者列表后,换行处理
        subf.write('\n')
        subf.close()

    def getPub(self, cid, filename):
        '''
        功能跟getSub类似,只是URL及或者的字典key略有不同
        '''

        url_base = 'http://follow.renren.com/list/'
        print 'now crawling pub id--> ' + str(cid)
        url_getcount = url_base + str(cid) + '/pubmore?offset=0&limit=1'
        pubdata_str = urllib2.urlopen(url_getcount).read()
        pubdict = json.loads(pubdata_str)
        if pubdict['code'] != 0:
            pubcount = 0
            return
        else:
            pubcount = pubdict['data']['publisherCount']
            print str(cid) + ' pubcount = ' + str(pubcount)
            if pubcount > 100000:
                with open('pub_too_large.txt', 'a') as f:
                    f.write(str(cid)+' '+str(pubcount)+'\n')
                return

        pubf = open(filename, 'a')
        pubdata_list = []
        if pubcount < 500:
            url_getpub = url_base + str(cid) + '/pubmore?offset=0&limit=' + str(pubcount)
            print url_getpub
            pubdata_str = urllib2.urlopen(url_getpub).read()
            pubdict = json.loads(pubdata_str.replace('\r\n', ''),encoding='utf-8')
            #获取当前查询结果中的用户数量
            cnt = len(pubdict['data']['userList'])
            for num in range(cnt):
                pubdata_summary = {}
                pubdata_summary['id'] = pubdict['data']['userList'][num]['id']
                pubdata_summary['name'] = pubdict['data']['userList'][num]['name']
                pubdata_summary['info'] = pubdict['data']['userList'][num]['profileInfo']
                pubdata_summary['subcnt'] = pubdict['data']['userList'][num]['subscriberCount']
                pubdata_summary['authinfo'] = pubdict['data']['userList'][num]['authInfo']
                pubdata_summary['img'] = pubdict['data']['userList'][num]['headUrl']
                pubdata_summary['subby'] = cid
                pubdata_list.append(pubdata_summary)
                self.newids.add(pubdata_summary['id'])
            pubf.write(json.dumps(pubdata_list))
        else:
            offset_num = 0
            limit_num = 500
            while offset_num < pubcount:
                url_getpub = url_base + str(cid) + '/pubmore?offset=' + str(offset_num) + '&limit=' + str(limit_num)
                pubdata_str = urllib2.urlopen(url_getpub).read()
                pubdict = json.loads(pubdata_str.replace('\r\n', ''),encoding='utf-8')
                #获取当前查询结果中的用户数量
                cnt = len(pubdict['data']['userList'])
                for num in range(cnt):
                    pubdata_summary = {}
                    pubdata_summary['id'] = pubdict['data']['userList'][num]['id']
                    pubdata_summary['name'] = pubdict['data']['userList'][num]['name']
                    pubdata_summary['info'] = pubdict['data']['userList'][num]['profileInfo']
                    pubdata_summary['subcnt'] = pubdict['data']['userList'][num]['subscriberCount']
                    pubdata_summary['authinfo'] = pubdict['data']['userList'][num]['authInfo']
                    pubdata_summary['img'] = pubdict['data']['userList'][num]['headUrl']
                    #增加subby字段 代表该用户被cid关注
                    pubdata_summary['subby'] = cid
                    pubdata_list.append(pubdata_summary)
                    self.newids.add(pubdata_summary['id'])
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
    #抓取该ID的所有关注者和被关注者,必须两者均有至少一个人
    #start_id = 725807834
    #start_id = 326198288
    #start_id = 853016989
    start_id = 440818854
    subfile = str(start_id)+'_sub.txt'
    renrenlogin.getSub(start_id, subfile)
    pubfile = str(start_id)+'_pub.txt'
    renrenlogin.getPub(start_id, pubfile)
    #获取已经完成扫描的用户ID,放到集合中
    finished_ids = set()
    finished_ids.add(start_id)
    print finished_ids
    print renrenlogin.newids

    try:
        while True:
            needtocrawlids = renrenlogin.newids - finished_ids
            for cid in needtocrawlids:
                renrenlogin.getSub(cid, str(start_id)+'_sub_1.txt')
                renrenlogin.getPub(cid, str(start_id)+'_pub_1.txt')
                finished_ids.add(start_id)
            with open('finished_ids.txt', 'a') as f:
                f.write(','.join(str(x) for x in finished_ids))
    except:
        raise
    finally:
        print 'Done'
