# encoding: utf-8

from datetime import date as thedate
from datetime import datetime

from time import mktime, strptime

import chardet


def is_string(s):
    return isinstance(s, str)

def is_unicode(s):
    return isinstance(s, unicode)

def force_utf8(txt):
    return force_unicode(txt).encode('utf8')

def force_unicode(txt):
    if isinstance(txt,unicode) or not txt:
        return txt or ''
    ecd = chardet.detect(txt)['encoding']
    if ecd == 'utf-8' or ecd == 'utf8':
        return txt.decode(ecd)
    else:
        return txt.decode('cp936')


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
    

if __name__ == '__main__':
    import doctest
    print doctest.testmod(verbose=False, report=False)
