# encoding: utf-8
'''
Created on Mar 27, 2016

@author: root
'''
import sys
import time
import urllib2
import random
# from tool_net import fetch

class UrlOpenError(Exception):
    pass

class HTTP403(Exception):
    eid = 403

class PageNotFound404(Exception):
    eid = 404
    
class HtmlMalFormed(Exception):
    eid = 1


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
            delay = 240
            while att < attempt:
                try:
                    return func(*args, **kw)
                except urllib2.URLError as e:
                    if hasattr(e, 'code') and e.code == 456:
                        print "http 456 occured, delaying %d seconds..." % delay
                        time.sleep(delay)
                        delay=10
                    elif hasattr(e, 'code') and e.code == 404:
                        raise PageNotFound404
                    elif hasattr(e, 'code') and e.code == 403:
                        raise HTTP403
                    else:
                        att = retryit(att, e)
#                     else:
#                         raise e, None, sys.exc_info()[2]
#                 except socket.timeout as e:
#                     att = retryit(att, e)
#                 except (urllib2.URLError, ssl.SSLError, socket.timeout) as e:
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

# @retry(5)
# def urlopen_handle_456(*args, **params):
#     try:
#         r = urllib2.urlopen(*args, **params)
#         return r.read()
# #         print r.getcode()
#     except urllib2.HTTPError as err:
#         if err.code == 456:
#            raise
#         delay = 5
#         while r.getcode() == 456:
#             print "http 456 occured, delaying %d seconds..." % delay
#             time.sleep(delay)
#             delay +=5
#             r = urllib2.urlopen(*args, **params)
#         
#     finally:
#         try:
#             r.close()
#         except NameError:
#             pass


def urlopen_report(*args, **params):
    try:
        return urlopen(*args, **params)
    except Exception as e:
        raise UrlOpenError

def urlopen_silently(*args, **params):
    try:
        return urlopen(*args, **params)
    except Exception as e:
#         print e
        print [e.message]
        
def urlopen_try_untill_ok(*args, **params):
    while 1:
        try:
            return urlopen(*args, **params)
        except Exception as e:
            print e
            time.sleep(1)

def urlopen_try_untill_ok_with_callback(*args, **params):
    while 1:
        try:
            callback = args[0]
            args = args[1:]
            return callback(urlopen(*args, **params))
        except Exception as e:
            print e
            time.sleep(1)

    
# @retry(10)
# def fetch_url(*args, **params):
#     return fetch(*args, **params)


if __name__ == '__main__':
#     print urlopen("http://thenextweb.com/", timeout=20)
    urlopen("http://qq.yy521.com/qq/feedback.asp", timeout=20)