# encoding: utf-8
'''
Created on 2017年3月9日

@author: winston
'''
import re
import urllib
import urllib2

import pandas
from numpy.distutils.misc_util import is_string
from collection.tool_chinese import get_first_chars

def get_integer(s):
    try:
        return re.search("\d+", s).group()
    except:
        pass

def get_index(keyword, url='http://rank.chinaz.com/ajaxsync.aspx?at=index'):
    data = urllib.urlencode({'kw':keyword})
    content = urllib2.urlopen(url, data=data, timeout=15).read()
    return re.search("index:'(\d+)'", content).groups()[0]


def get_name_properties(keyword, url='http://www.baike.com/wiki/%s'):
    url = url % keyword
    content = urllib2.urlopen(url, timeout=15).read()
#     content
    df = pandas.read_html(content)[0]
    
    rtn = {}
    for x in df.to_dict('records'):
        for v in x.values():
            if is_string(v):
#                 print v
                name, value = v.split(u'：', 1)
                name, value = purdge(name.strip(), value.strip())
                rtn.setdefault(name, value)
    return rtn
    
def purdge(key, value):
    '''
    中文名 林志玲
英文名 Chiling Lin
别名 玲玲、冰欺凌、志玲姐姐
性别 女
出生年月 1974年11月29日
国籍 中国
籍贯 中国台湾
出生地 台湾省台北市
民族 汉族
毕业院校 加拿大多伦多大学,拥有美术史和经济学双学位。
身高 173cm
体重 54kg
职业 演员、主持人、模特
主要成就 华岗艺校表演艺术科教师  福布斯中国名人榜第11位  FHM “全球百大性感美女”第一名
代表作品 《赤壁》 《刺陵》《决战刹马镇》 《幸福额度》 《天机：富春山居图》 《101次求婚》 《甜心巧
出道地区 台湾
经纪公司 凯渥模特经纪公司
星座 射手座
血型 O
主要事件 2003年取代萧蔷当选台湾第一美女

    '''
    if key == u'身高':
        value = get_integer(value)
    if key == u'体重':
        value = get_integer(value)
    if key == u'出生年月':
        value = value.replace(u'年', '-').replace(u'月', '-').replace(u'日', '')
    return get_first_chars(key), value
        
    
if __name__ == '__main__':
#     print get_index(keyword='林志玲')
    d = get_name_properties(keyword='林志玲')
    d = {k:v for k,v in d.items() if k != 'zwm'}
#     d = filter(lambda x:x == 'zwm', d)
#     print d
    for k,v in d.items():
        print k, v
#     print get_name_height('林志玲')
    
#     print get_integer('1222cm')