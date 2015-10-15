#!/usr/bin/python -tt
# encoding=utf-8
#http://www.renren.com/newnamecard?uid=882835050

import sys
import urllib
import urllib2
import cookielib
import json
import time
import re

from bs4 import BeautifulSoup

class nameCard:
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
        while True:
            try:
                index = urllib2.urlopen(req,timeout=10).read()
            except (urllib2.HTTPError, urllib2.URLError, urllib2.socket.timeout) as err:
                time.sleep(3)
                print 'something is wrong with your networking maybe...'
                continue
            else:
                break
        indexSoup = BeautifulSoup(index,'lxml')

        indexFile = open('namecard.html','w')
        indexFile.write(indexSoup.prettify())
        indexFile.close()

    def card(self, idlist, filename):
        url_base = 'http://www.renren.com/newnamecard?uid='
        with open(filename, 'a') as cfd:
            for cid in idlist:
                name_summary = {}
                url_card = url_base + str(cid)
                print url_card
                while True:
                    try:
                        cardtext = urllib2.urlopen(url_card, timeout=10).read()
                    except (urllib2.HTTPError, urllib2.URLError, urllib2.socket.timeout) as err:
                        time.sleep(3)
                        print 'something is wrong with your networking maybe...'
                        continue
                    else:
                        break
                #print cardtext
                name_dict = json.loads(cardtext)
                #print name_dict
                name_summary['name'] = name_dict['name']
                name_summary['id'] = name_dict['ownerId']
                name_summary['region'] = name_dict['region']
                name_summary['authInfo'] = name_dict['authInfo']

                #print name_summary
                cfd.write(str(name_summary))
                cfd.write('\n')

if __name__ == '__main__':
    email = raw_input('email :')
    password = raw_input('password :)
    reload(sys)
    sys.setdefaultencoding('utf-8')
    renrenlogin = nameCard(email, password)
    renrenlogin.login()

    id_list = []
    with open('card_ids.txt', 'r') as f:
        ids_text = f.readlines()

    for line in ids_text:
        id_list.append(int(line.replace('\n', '')))
    #print id_list
    renrenlogin.card(id_list, 'namecard.txt')
