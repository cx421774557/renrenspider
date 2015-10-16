#!/usr/bin/python -tt
# encoding=utf-8

import json
import time
import yaml
#reference http://stackoverflow.com/questions/13675942/converting-string-to-dict

if __name__ == '__main__':

    sum_dict = {}
    id_set = set()
    with open('pub.txt', 'r') as f:
        pubtext = f.readlines()
    for line in pubtext:
        cid = json.loads(line)[0]['subby']
        cnt = len(json.loads(line))
        print cid, cnt
        sum_dict[str(cid)] = {}
        sum_dict[str(cid)]['pub_cnt'] = int(cnt)
        id_set.add(int(cid))

    with open('sub.txt', 'r') as f:
        subtext = f.readlines()
    for line in subtext:
        cid = json.loads(line)[0]['subto']
        cnt = len(json.loads(line))
        print cid, cnt
        if cid in id_set:
            sum_dict[str(cid)]['sub_cnt'] = int(cnt)
        else:
            sum_dict[str(cid)] = {}
            sum_dict[str(cid)]['pub_cnt'] = 0
            sum_dict[str(cid)]['sub_cnt'] = int(cnt)
        id_set.add(int(cid))

    with open('namecard.txt', 'r') as f:
        cardtext = f.readlines()
    for line in cardtext:
        try:
            cid = yaml.load(line)['id']
            region = yaml.load(line)['region']
        except:
            print 'data format error.'
            continue
        print cid, region
        if cid in id_set:
            sum_dict[str(cid)]['region'] = region

    #处理info.txt
    with open('info.txt') as f :
        infotext = f.readlines()
    for line in infotext:
        try:
            linedict = yaml.load(line)
            cid = linedict['id']
            name = linedict['name'].decode('utf-8')
            f_cnt = linedict['friends_cnt']
            views = linedict['views']
            is_star = linedict['isstar']
            f_list = linedict['friendslist']
        except:
            continue
        print cid, name
        if cid in id_set:
            sum_dict[str(cid)]['name'] = name
            sum_dict[str(cid)]['friends_cnt'] = f_cnt
            sum_dict[str(cid)]['views'] = views
            sum_dict[str(cid)]['is_star'] = is_star
            sum_dict[str(cid)]['friends_list'] = f_list

    with open('summary.txt', 'w') as f:
        f.write(json.dumps(sum_dict))
    print 'Done'
