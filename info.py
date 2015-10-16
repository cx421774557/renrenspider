#!/usr/bin/python -tt
# encoding=utf-8
#http://www.renren.com/newnamecard?uid=882835050
#待解决问题,查看100个同学的页面后,需要输入验证码
import sys
import urllib
import urllib2
import cookielib
import json
import time
import re

from bs4 import BeautifulSoup

class renrenInfo:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.domain = 'renren.com'
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
        #不明白为什么以下5行必须执行 才能登陆成功
        index = urllib2.urlopen(req,timeout=10).read()
        indexSoup = BeautifulSoup(index,'lxml')

        indexFile = open('index.html','w')
        indexFile.write(indexSoup.prettify())
        indexFile.close()

    def getInfo(self, idlist, filename):
        url_base = 'http://www.renren.com/'
        #pfd means profile_fd
        with open(filename, 'a') as pfd:
            for cid in idlist:
                url_info = url_base + str(cid) + '/profile'
                print url_info
                while True:
                    try:
                        indextext = urllib2.urlopen(url_info, timeout=10).read()
                    except (urllib2.HTTPError,urllib2.URLError,urllib2.socket.timeout) as err:
                        time.sleep(3)
                        print 'something is wrong with your network maybe...'
                        continue
                    else:
                        break
                soup = BeautifulSoup(indextext, 'lxml')
                #print soup.prettify()
                #判断是否为有效页面
                soup_userinfo = soup.find_all(name='h1',class_=re.compile('^avatar_title'))
                if not soup_userinfo:
                    is_invalid = soup.find_all(name='div', class_='text')
                    if is_invalid:
                        if is_invalid[0].text == '该用户已注销':
                            print '该用户已注销'
                            continue
                        elif is_invalid[0].text == '该用户已被封禁。':
                            print '该用户已被封禁'
                            continue
                        else:
                            print 'Unknow error\nQuitting...'
                            return
                    else:
                        #每抓取100个页面后,需要验证
                        s = raw_input('\n打开以下链接,输入完成验证码后,输入"Y"继续,"N"退出程序:\n{}\nY/N :'.format(url_info))
                        if s == 'N' or s == 'n':
                            print 'Quit...'
                            return
                        elif s == 'Y' or s == 'y' or s.replace(' ', '') == '':
                            print 'Continue...'
                            f = open('uncompleted.txt', 'a')
                            f.write('{}\n'.format(str(cid)))
                            f.close()
                            continue
                fullname = soup.find_all(name='title')[0]
                #print fullname
                p = re.compile(r'- (.*)<')
                name = re.findall(p, str(fullname))
                infolist = soup_userinfo[0].text.split('\n')
                while '' in infolist:
                    infolist.remove('')
                #print infolist
                infodict = {}
                #这样写会导致名字不全
                #infodict['name'] = infolist[0]
                infodict['name'] = name[0]
                #print infodict
                p = re.compile(r'\d+')
                infodict['views'] = int(re.findall(p, infolist[1])[0])
                if len(infolist) >= 3:
                    if infolist[2] == u'星级用户':
                        infodict['isstar'] = 1
                else:
                    infodict['isstar'] = 0
                #print infodict
                soup_friends = soup.find_all(name='div', class_='share-friend')
                if not soup_friends:
                    infodict['friends_cnt'] = 0
                else:
                    friendslist = soup_friends[0].text.split('\n')
                    while '' in friendslist:
                        friendslist.remove('')
                    infodict['friends_cnt'] = int(re.findall(p, friendslist[0])[0])
                #print cid, infodict
                friendslist = soup.find_all(name='a', namecard=True, target='_blank')
                #print friendslist
                seven_friends_ids = []
                for friend in friendslist[:7]:
                    #print type(friend)
                    fid = re.findall(p, str(friend))[0]
                    #print fid
                    seven_friends_ids.append(int(fid))
                infodict['friendslist'] = seven_friends_ids
                infodict['id'] = cid
                #print infodict
                pfd.write(str(infodict))
                pfd.write('\n')

if __name__ == '__main__':
    email = raw_input('email: ')
    password = raw_input('password: ')
    reload(sys)
    sys.setdefaultencoding('utf-8')
    renrenlogin = renrenInfo(email, password)
    renrenlogin.login()

    ids_fd = open('finished_ids.txt', 'r')
    ids_text = ids_fd.readlines()
    fidslist = []
    for line in ids_text:
        fidslist.append(int(line))
    #print fidslist
    ids_fd.close()
    renrenlogin.getInfo(fidslist, 'info.txt')
