# encoding: utf-8
'''
Created on Mar 27, 2016

@author: root
'''
import sys
import time
import urllib2
import random

class UrlOpenError(Exception):
    pass

def retry(attempt):
    def decorator(func):
        def retryit(att, e):
            print "timeout, retrying ...", att
            att += 1
            if att >= attempt:
                raise e, None, sys.exc_info()[2]
            time.sleep(random.randint(1,3)+att)
            return att
        def wrapper(*args, **kw):
            att = 0
            while att < attempt:
                try:
                    return func(*args, **kw)
                except Exception as e:
                    att = retryit(att, e)
                    
        return wrapper
    return decorator

@retry(5)
def urlopen(*args, **params):
    try:
        r = urllib2.urlopen(*args, **params)
        return r.read()
    finally:
        try:
            r.close()
        except NameError:
            pass

def urlopen_report(*args, **params):
    try:
        return urlopen(*args, **params)
    except Exception as e:
        raise UrlOpenError

def urlopen_silently(*args, **params):
    try:
        return urlopen(*args, **params)
    except Exception as e:
        print e
    

if __name__ == '__main__':
#     print urlopen("http://thenextweb.com/", timeout=20)
    urlopen("http://www.baidu.com/", timeout=20)