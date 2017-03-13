# encoding: utf-8
'''
Created on 2017年3月9日

@author: winston
'''
import re
import urllib

import pandas
from pyquery.pyquery import PyQuery

from collection.tool_chinese import get_first_chars
from utils.tool_env import is_string, is_unicode, to_date, dash_date,\
    force_unicode
from utils.urlopen import urlopen

CODE_OTHER_EXCEPTIONS = 100

class NoTableFoundError(Exception):
    code = 2

class NoPropertiesError(Exception):
    code = 3

class DumpPropertyError(Exception):
    code = 4

class JBQMNameParseError(Exception):
    code = 5

def get_real_name(name=None):
    return name.split('[', 1)[0].strip() 


def get_integer(s):
    try:
        return re.search("\d+", s).group()
    except:
        pass

def get_index(keyword, url='http://rank.chinaz.com/ajaxsync.aspx?at=index'):
    data = urllib.urlencode({'kw':get_real_name(keyword)})
    content = urlopen(url, data=data, timeout=15)
#     print content
    m = re.search("index:'(\d+)'", content)
    return m.groups()[0] if m is not None else 0


def get_name_relations(keyword=None, url='http://www.baike.com/wiki/%s', content=None):
    content = content or urlopen(url % keyword, timeout=15)
    d = PyQuery(content)
    
    x = d('#figurerelation')
    
    relation_links = filter(lambda x:x.attr('href') and x.attr('href').startswith('http://so.baike.com/doc'),x.items('a'))  

    for a in relation_links:
        yield a.text()


def get_name_properties(keyword, url='http://www.baike.com/wiki/%s'):
    url = url % keyword
    content = urlopen(url, timeout=15)
#     print content
    try:
        df = pandas.read_html(content)[0]
    except (ValueError,TypeError):
        raise NoTableFoundError
    
    rtn = {}
    for x in df.to_dict('records'):
        for v in x.values():
            
            if is_string(v) or is_unicode(v):
                p = v.split(u'：', 1)
                if len(p) != 2:
                    raise NoPropertiesError
                name, value = p
                name, value = purdge(name.strip(), value.strip())
                rtn.setdefault(name, value)
    return rtn, get_name_relations(content=content)
    
def purdge(key, value):
    if key == u'身高':
        value = get_integer(value)
    if key == u'体重':
        value = get_integer(value)
    if key in [u'出生年月', u'去世年月']:
        value = dash_date(to_date(value.replace(u'年', '-').replace(u'月', '-').replace(u'日', '')))
    return get_first_chars(key), value
        

def get_name_info(name, url='http://www.jinbangqm.com/names/%s.html'):
    content = urlopen(url % get_real_name(name), timeout=15)
#     print content
    try:
        dfs = pandas.read_html(content)
        rtn = dfs[14][1].dropna().tolist()
        rtn += dfs[15][1].dropna().tolist()
        rtn.remove(u'不论凶吉')
        return ','.join(rtn)
    except (ValueError,TypeError):
        raise JBQMNameParseError
    

def get_english_info(word, url='http://www.bing.com/dict/search?q=%s'):
    content = urlopen(url % word, timeout=15).decode('utf8')
    d = PyQuery(content)
    return ','.join(map(lambda x:x.text(), d("span.def").items()))

# def get_english_infos(name):
#     return ','.join(lambda x:get_english_info(x), re.split('\s+', name.strip()))
def get_common_english_names(url="https://www.douban.com/note/138477313/", q='div#link-report', sex=0):
    content = urlopen(url , timeout=15)
    d = PyQuery(force_unicode(content))
    if sex is None:
        sex = 1
    for x in filter(lambda x:len(x) > 1, re.findall('[a-zA-Z]+', d(q).text())):
        if x == 'Abigail':
            sex = 0
        yield x, sex


if __name__ == '__main__':
    to_import = [
        {'url':"https://www.douban.com/note/138477313/", 'q':'div#link-report', 'sex':0},
        {'url':"http://blog.renren.com/share/243317589/1192669473", 'q':'div#shareBody', 'sex':1},
        
        {'url':"http://blog.sina.com.cn/s/blog_49b5f65f0100o5mh.html", 'q':'div#sina_keyword_ad_area2', 'sex':None},
        
                 ]
    for x in get_common_english_names(**to_import[2]):
        print x 
