# encoding: utf-8
'''
Created on 2017年2月9日

@author: winston
'''

#!/usr/bin/env python
#coding=utf-8

def get_cn_first_letter(ch,codec="unicode"):
    if codec!="GBK":
        if codec!="unicode":
            ch=ch.decode(codec)
        ch=ch.encode("GBK")
    
    if ch<"\xb0\xa1" or ch>"\xd7\xf9":
        return ch
#     print [ch]
    if ch<"\xb0\xc4":
        return "a"
    if ch<"\xb2\xc0":
        return "b"
    if ch<"\xb4\xed":
        return "c"
    if ch<"\xb6\xe9":
        return "d"
    if ch<"\xb7\xa1":
        return "e"
    if ch<"\xb8\xc0":
        return "f"
    if ch<"\xb9\xfd":
        return "g"
    if ch<"\xbb\xf6":
        return "h"
    if ch<"\xbf\xa5":
        return "j"
    if ch<"\xc0\xab":
        return "k"
    if ch<"\xc2\xe7":
        return "l"
    if ch<"\xc4\xc2":
        return "m"
    if ch<"\xc5\xb5":
        return "n"
    if ch<"\xc5\xbd":
        return "o"
    if ch<"\xc6\xd9":
        return "p"
    if ch<"\xc8\xba":
        return "q"
    if ch<"\xc8\xf5":
        return "r"
    if ch<"\xcb\xf9":
        return "s"
    if ch<"\xcd\xd9":
        return "t"
    if ch<"\xce\xf3":
        return "w"
    if ch<="\xd1\xaa":
        return "x"
    if ch<"\xd4\xd0":
        return "y"
    if ch<="\xd7\xf9":
        return "z"
    return ch

def get_first_chars(uchars):
    return ''.join(map(lambda x:get_cn_first_letter(x), uchars))

if __name__ == '__main__':
    print [get_first_chars(u"血")]
#     print ["血"]