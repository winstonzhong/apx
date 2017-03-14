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
    force_unicode, force_utf8
from utils.urlopen import urlopen
from utils.tool_html import remove_garbages

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



def get_missing_birthday(name, url='https://www.bing.com/search?q=%s'):
    html = urlopen(url % urllib.quote_plus('%s 出生日期' % force_utf8(name)), timeout=15)

    html = force_unicode(html)
#      
    html = remove_garbages(html)

    content = PyQuery(html)('body').text()

    ptn = re.compile(u'[\d\s]+年[\d\s]+月[\d\s]+日')

    rtn = map(lambda x:x.strip(), ptn.findall(content))
    
    return max(set(rtn), key=lambda x:rtn.count(x)) if rtn else None

def get_missing_gender(name, url='https://www.bing.com/search?q=%s'):
    url = url % urllib.quote_plus('%s 性别' % force_utf8(name))

    html = urlopen(url, timeout=15)

    html = force_unicode(html)
#      
    html = remove_garbages(html)

    content = PyQuery(html)('body').text()

    ptn = re.compile(u'男|女')

    rtn = map(lambda x:x.strip(), ptn.findall(content))
    
    return rtn[0] if rtn else None


if __name__ == '__main__':
    print get_missing_gender('周星驰')
    print get_missing_gender('景甜')
    print get_missing_gender('毛泽东')
