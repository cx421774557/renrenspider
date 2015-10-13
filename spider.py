#!/usr/bin/python -tt
# encoding=utf-8
#待优化 1, 减少文件写入操作
#可以通过给函数传递一个ID的LIST,20个一组,完成后再保存,待以后改进
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
        self.finished_ids = set()
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
        #reference: http://stackoverflow.com/questions/3515087/detecting-timeout-erros-in-pythons-urllib2-urlopen
        #reference: http://stackoverflow.com/questions/8072597/skip-url-if-timeout
        while True:
            try:
                subdata = urllib2.urlopen(url_getcount,timeout=10)
            #增加urllib2.socket.timeout异常处理
            except (urllib2.HTTPError,urllib2.URLError,urllib2.socket.timeout) as err:
                time.sleep(3)
                print 'something is wrong with your networking'
                #不加continue依然会异常退出
                continue
            else:
                subdata_str = subdata.read()
                break
        #待修复:这里偶尔会报ValueError: No JSON object could be decoded
        #ValueError: Unterminated string starting at: line 1 column 50098 (char 50097)
        try:
            subdict = json.loads(subdata_str)
        except ValueError:
            return
        if subdict['code'] != 0:
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
            while True:
                try:
                    subdata = urllib2.urlopen(url_getsub,timeout=10)
                except (urllib2.HTTPError,urllib2.URLError,urllib2.socket.timeout) as err:
                    time.sleep(3)
                    print 'something is wrong with your networking'
                    continue
                else:
                    subdata_str = subdata.read()
                    break

            #待修复ValueError: Invalid control character at: line 1 column 16842 (char 16841)异常
            #subdict = json.loads(subdata_str.replace('\r\n', ''),encoding='utf-8') 这个方法无效,也许是要把'\n'换成'',没有试验
            #暂时用下面的方法 json.loads(restrict=False)貌似也不对,应该就是下载的数据不完整造成的
            try:
                subdict = json.loads(subdata_str,encoding='utf-8')
            except ValueError:
                return
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
                while True:
                    try:
                        subdata = urllib2.urlopen(url_getsub,timeout=10)
                    except (urllib2.HTTPError,urllib2.URLError,urllib2.socket.timeout) as err:
                        time.sleep(3)
                        print 'something is wrong with your networking'
                        continue
                    else:
                        subdata_str = subdata.read()
                        break
                try:
                    subdict = json.loads(subdata_str,encoding='utf-8')
                except ValueError:
                    print 'load json data error...something is bad with the server or maybe your network is bad'
                    return
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
        功能跟getSub类似,只是URL及保存的字典key略有不同
        '''

        url_base = 'http://follow.renren.com/list/'
        print 'now crawling pub id--> ' + str(cid)
        url_getcount = url_base + str(cid) + '/pubmore?offset=0&limit=1'
        while True:
            try:
                pubdata = urllib2.urlopen(url_getcount,timeout=10)
            except (urllib2.HTTPError,urllib2.URLError,urllib2.socket.timeout) as err:
                time.sleep(3)
                print 'something is wrong with your networking'
                continue
            else:
                pubdata_str = pubdata.read()
                break

        try:
            pubdict = json.loads(pubdata_str)
        except ValueError:
            print 'load json data error...something is bad with the server or maybe your network is bad'
            return
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
            while True:
                try:
                    pubdata = urllib2.urlopen(url_getpub,timeout=10)
                except (urllib2.HTTPError,urllib2.URLError,urllib2.socket.timeout) as err:
                    time.sleep(3)
                    print 'something is wrong with your networking'
                    continue
                else:
                    pubdata_str = pubdata.read()
                    break

            try:
                pubdict = json.loads(pubdata_str,encoding='utf-8')
            except ValueError:
                print 'load json data error...something is bad with the server or maybe your network is bad'
                return
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
                while True:
                    try:
                        pubdata = urllib2.urlopen(url_getpub,timeout=10)
                    except (urllib2.HTTPError,urllib2.URLError,urllib2.socket.timeout) as err:
                        time.sleep(3)
                        print 'something is wrong with your networking'
                        continue
                    else:
                        pubdata_str = pubdata.read()
                        break
                try:
                    pubdict = json.loads(pubdata_str,encoding='utf-8',strict=False)
                except:
                    print 'load json data error...something is bad with the server or maybe your network is bad'
                    return
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
    #start_id = 440818854
    #start_id = 319383233
    start_id = 271038494
    subfile = str(start_id)+'_sub.txt'
    renrenlogin.getSub(start_id, subfile)
    pubfile = str(start_id)+'_pub.txt'
    renrenlogin.getPub(start_id, pubfile)
    #获取已经完成扫描的用户ID,放到集合中
    renrenlogin.finished_ids.add(start_id)
    print renrenlogin.finished_ids
    print renrenlogin.newids

    while True:
        needtocrawlids = renrenlogin.newids - renrenlogin.finished_ids
        for cid in needtocrawlids:
            renrenlogin.getSub(cid, str(start_id)+'_sub_1.txt')
            renrenlogin.getPub(cid, str(start_id)+'_pub_1.txt')
            #更新已完成的ID集合
            renrenlogin.finished_ids.add(cid)
            #print str(renrenlogin.finished_ids)
            #打印已经完成的ID总数
            print str(len(renrenlogin.finished_ids))+' FINISHED'
            #抓取完成一组ID之后,把已经抓取成功的ID记录下文件中,其实最好做成抓完一个ID立即保存,但是为了防止文件IO过多,暂时这样处理.
            #每完成20个ID, 保存一次
            if len(renrenlogin.finished_ids) % 20 == 0:
                #这里应该用w方式清空文件,因为finished_ids没有清空,不能用a方式
                with open('finished_ids.txt', 'w') as f:
                    #这里用'\n'代替',' 防止先后两次写入的项没有以','分隔开
                    f.write('\n'.join(str(x) for x in renrenlogin.finished_ids))
