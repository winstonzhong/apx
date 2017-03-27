# encoding: utf-8

from datetime import date as thedate, datetime
from time import mktime, strptime
from utils.constants import PROJECT_DIR
import chardet
import os
import re


pinyin_dict = {}
dat = os.path.join(PROJECT_DIR, "utils/Mandarin.dat")
with open(dat) as f:
    for line in f:
        k, v = line.strip().split('\t')
        pinyin_dict[k] = v.lower().split(" ")

def is_string(s):
    return isinstance(s, str)

def is_unicode(s):
    return isinstance(s, unicode)

def force_utf8(txt):
    return force_unicode(txt).encode('utf8')

def force_unicode(txt):
    if isinstance(txt, unicode) or not txt:
        return txt or ''
    ecd = chardet.detect(txt)['encoding']
    if ecd == 'utf-8' or ecd == 'utf8':
        return txt.decode(ecd)
    else:
        try:
            return txt.decode('cp936')
        except:
            pass
    return txt


def dash_date(date):
    '''
    >>> dash_date('20160308')
    '2016-03-08'
    >>> dash_date('20161231')
    '2016-12-31'
    >>> dash_date(datetime(year=2016,month=12,day=31))
    '2016-12-31'
    >>> dash_date(thedate(year=2016,month=12,day=31))
    '2016-12-31'
    >>> dash_date('2016-12-31')
    '2016-12-31'
    >>> dash_date(None)
    '''
    if date:
        if isinstance(date, datetime) or isinstance(date, thedate):
            date = date.strftime("%Y-%m-%d")
        elif '-' not in date:
            date = datetime.fromtimestamp(mktime(strptime(date, "%Y%m%d"))).strftime("%Y-%m-%d")
    return date
    
def reformat_date_str(txt, ptn=re.compile('[^0-9]*')):
    '''
    >>> reformat_date_str('2016年1月2日') == '2016-01-02'
    True
    >>> reformat_date_str('2016/1/2') == '2016-01-02'
    True
    >>> reformat_date_str('20160102') == '2016-01-02'
    True
    '''
    rtn = ptn.split(txt, maxsplit=3)
    if len(rtn) >=3:
        return "%04d-%02d-%02d" % tuple(map(lambda x:int(x), rtn[:3]))
    return dash_date(rtn[0])
        

def to_date(date):
    '''
    >>> to_date(datetime(year=2016, month=3, day=9))
    datetime.date(2016, 3, 9)
    >>> to_date('20160308')
    datetime.date(2016, 3, 8)
    >>> to_date('2016-12-31')
    datetime.date(2016, 12, 31)
    >>> to_date('a')
    >>> to_date(None)
    >>> to_date(0)
    >>> to_date(u'2016-04-22 10:46:00')
    datetime.date(2016, 4, 22)
    '''
    if isinstance(date, datetime):
        return date.date()
    if isinstance(date, thedate):
        return date
    try:
        return datetime.fromtimestamp(mktime(strptime(dash_date(date)[:10], "%Y-%m-%d"))).date()
    except:
        pass
    
def add_space_ahead_caps(name, ptn=re.compile('([A-Z])')):
    '''
    >>> add_space_ahead_caps('AngelaBaby')
    'Angela Baby'
    '''
    return ptn.sub(r' \1', name).strip()

def split_english_words(words, ptn=re.compile('[^a-z]+')):
    '''
    >>> split_english_words('aaa bbb') == ['aaa', 'bbb']
    True
    >>> split_english_words('Mark Chao/Mark Zhao') == ['zhao', 'chao', 'mark']
    True
    >>> split_english_words('  Jacqueline   LI Xiao-Lu') == ['i', 'jacqueline', 'lu', 'l', 'xiao']# == ['jacqueline', 'lu', 'xiao', 'li']
    True
    '''
    words = add_space_ahead_caps(words)
    return list(set(ptn.split(words.lower())))

def get_first_english_name(name,ptn = re.compile('[^\\s\w]')):
    return ptn.split(name)[0].strip()



def is_chinese(uchar,charset=None):
    
    '''
    >>> is_chinese('你',charset='utf8')
    True
    >>> is_chinese('a')
    False
    >>> is_chinese('.')
    False
    '''
    if charset:
        uchar = uchar.decode(charset)
#     print [uchar]
    if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
        return True
    else:
        return False    

def has_chinese(uchars):
    for u in uchars:
        if is_chinese(u):
            return True
    return False

def get_pinyin_list(txt):
    chars = force_unicode(txt)
    py_list = []
    for char in chars:
        char = '%X' % ord(char)
        char_py_list = pinyin_dict[char]
        py_list.sort()
        py_list.append(char_py_list)
    return py_list

def is_english_name(chinese_name, english_name):
    """判断英文名是否为中文拼音
    >>> is_english_name(u'\u5218\u5fb7\u534e', 'Liu De Hua')
    False
    >>> is_english_name(u'\u5218\u5fb7\u534e', 'dehualiu')
    False
    >>> is_english_name(u'\u5218\u5fb7\u534e', 'Andy Lau')
    True
    >>> is_english_name(u'\u5218\u5fb7\u534e', '')
    False
    >>> is_english_name('蒋劲夫', 'Jiang Jinfu')
    False
    """
    
    if not english_name or not english_name.strip():
        return False
    chinese_name = chinese_name.split('[')[0]
    py_list = get_pinyin_list(chinese_name)
    english_name = english_name.lower()
    for char_pys in py_list:
        for char_py in char_pys:
            char_py = char_py[:-1]
            if char_py in english_name:
                english_name = english_name.replace(char_py, '') 
                break
    if english_name.strip():
        return True
    return False
    

if __name__ == '__main__':
    import doctest
    print doctest.testmod(verbose=False, report=False)
#     print get_pinyin_str('蒋劲夫'.decode('utf8'), format='diacritical')
#     print is_english_name('蒋劲夫', 'Jiang Jinfu')
#     print "%X" % ord(u'甯')
    
