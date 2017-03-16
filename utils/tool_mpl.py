# encoding: utf-8
'''
Created on 2017年3月16日

@author: winston
'''
import subprocess

from matplotlib.font_manager import FontManager



def get_available_fonts():
    fm = FontManager()
    mat_fonts = set(f.name for f in fm.ttflist)
    
    output = subprocess.check_output(
        'fc-list :lang=zh -f "%{family}\n"', shell=True)
    # print '*' * 10, '系统可用的中文字体', '*' * 10
    # print output
    zh_fonts = set(f.split(',', 1)[0] for f in output.split('\n'))
   
    print '*' * 10, 'Sys字体', '*' * 10
    
    for x in zh_fonts:
        print x


    print '*' * 10, 'Mat 字体', '*' * 10
    
    for x in mat_fonts:
        print x
    
    available = mat_fonts & zh_fonts
    
    print '*' * 10, '可用的字体', '*' * 10
    for f in available:
        print f

    
if __name__ == '__main__':
    get_available_fonts()
