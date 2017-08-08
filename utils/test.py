# encoding: utf-8
'''
Created on 2017年7月14日

@author: winston
'''
import os

import pandas


base_dir = os.path.dirname(os.path.dirname(__file__))

data_dir = os.path.join(base_dir, 'data')

csv1 = os.path.join(data_dir, '2017071311151843.csv')
csv2 = os.path.join(data_dir, '2017071311133921.csv')

def get_df(csvx):
    df = pandas.read_csv(csvx, encoding='cp936')
    df.index = df[u'关键词']
    tmp = df[u'整体指数']
    tmp = tmp.drop_duplicates()
    return tmp

def get_jb_df():
    return get_df(csv1)

def get_ymw_df():
    return get_df(csv2)

def get_keywords_not_in_jb():
    jb = get_jb_df()
    ym = get_ymw_df()
    return ym[~ym.index.isin(jb.index)].sort_values(ascending=False)

if __name__ == '__main__':
    df = get_keywords_not_in_jb()
    df.to_csv('/home/winston/keywrods.csv', encoding='utf8')
    print df
    
