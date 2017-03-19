# encoding: utf-8
import datetime

from django.core.management.base import BaseCommand
from django.db.models.query_utils import Q
import numpy
import pandas

from collection.models import PersonRecord, CommonEnglishNames
from collection.tool_net import get_name_info, JBQMNameParseError, \
    get_common_english_names, get_missing_birthday, get_real_name, \
    get_missing_gender
import matplotlib.pyplot as plt
from utils.tool_env import force_unicode, force_utf8, reformat_date_str, \
    get_first_english_name


class Command(BaseCommand):
    def add_arguments(self, parser):
        """定义参数"""
        # Positional arguments
#         parser.add_argument('args', nargs='*', type=str)
        
        # Named (optional) arguments
        parser.add_argument('--add', nargs = "?",default=None, help='add a name')
        
        parser.add_argument('--run', nargs = "?",default=0, help='add a name', type=int)
        parser.add_argument('--patch', action='store_true', default=False, help='patch data with out name info')
        parser.add_argument('--import_english', action='store_true', default=False, help='import english names.')
        parser.add_argument('--find_missing_birth', action='store_true', default=False, help='find missing birthdays.')
        parser.add_argument('--find_missing_gender', action='store_true', default=False, help='find missing genders.')
        
        parser.add_argument('--export', nargs = "?",default=0, help='export head n records order by bd inex from database to to excel')
        parser.add_argument('--fx1', action='store_true', default=False, help=u'分析明星取英文名字和年代的关系')
        parser.add_argument('--fx2', action='store_true', default=False, help=u'画出具体的案例，使用渐变散点图方式')
        
        parser.add_argument('--update', nargs = "?",default=None, help='update a single name')
        
        
        
        


    def handle(self, *args, **options):
        """参数指向"""

        if options.get('update'):
            name = force_unicode(options.get('update'))
            PersonRecord.add(name)
            PersonRecord.update(name)
            return


        if options.get('add'):
            name = force_unicode(options.get('add'))
            PersonRecord.add(name)
            return
        
        if options.get('run'):
            for i in xrange(options.get('run')):
                print i,
                r = PersonRecord.step()
                if not r:
                    break
            return 
        
        if options.get('patch'):
            q = PersonRecord.objects.filter(~Q(ywm=None), updated=1, english_info=None).order_by('-bd_index')
            total = q.count()
            for i, pr in enumerate(q.iterator()):
                print "Patching:%d/%d" % (i, total), pr.zwm
                try:
                    pr.english_info = pr.get_english_info(pr.ywm)
                    pr.save()
                except Exception as e:
                    raise e
#                     pr.updated = e.code
#                     pr.save()
            return

        if options.get('find_missing_birth'):
            q = PersonRecord.objects.filter(updated=1, csny=None).order_by('-bd_index')
            total = q.count()
            for i, pr in enumerate(q.iterator()):
                print "Find_missing_birth:%d/%d" % (i, total), pr.zwm,
                birth = get_missing_birthday(get_real_name(pr.zwm))
                print birth
                if birth:
                    pr.csny = reformat_date_str(birth)
                    pr.save()
            return

        if options.get('find_missing_gender'):
            q = PersonRecord.objects.filter(updated=1, xb=None).order_by('-bd_index')
            total = q.count()
            for i, pr in enumerate(q.iterator()):
                print "Find_missing_gender:%d/%d" % (i, total), pr.zwm,
                gender = get_missing_gender(get_real_name(pr.zwm))
                print gender
                if gender:
                    pr.xb = gender
                    pr.save()
            return

        
        if options.get('import_english'):
            to_import = [
                {'url':"https://www.douban.com/note/138477313/", 'q':'div#link-report', 'sex':0},
                {'url':"http://blog.renren.com/share/243317589/1192669473", 'q':'div#shareBody', 'sex':1},
                
                {'url':"http://blog.sina.com.cn/s/blog_49b5f65f0100o5mh.html", 'q':'div#sina_keyword_ad_area2', 'sex':None},
                
                         ]
            for d in to_import:
                for x in get_common_english_names(**d):
                    print x
                    name, sex = x
                    cen, _ = CommonEnglishNames.objects.get_or_create(name=name.lower())
                    cen.sex = sex
                    cen.save()
            return


        if options.get('fx1'):
            q = PersonRecord.objects.filter(Q(zy__contains='演员') |Q( zy__contains='导演') | Q(zy__contains='歌手') | Q(zy__contains='模特'), updated=1).order_by('-bd_index')
            df = pandas.DataFrame(list(q.values('zwm','ywm','csny', 'xb')))
            df['gen'] = df.csny.astype(datetime.date).apply(lambda x:(x.year -1900)/10 * 10 if x else None)
            df['enc'] = map(lambda x: CommonEnglishNames.get_english_name_gender_count(x), df.ywm)
#             df.xb = df.xb.apply(lambda x: {u'男':'M', u"女":'F'}.get(x))
            
            def ratio_count(x, xb=None):
                if xb is None:
                    return len(x[~x.enc.isnull()]) * 1.0 / len(x)
                return len(x[(~x.enc.isnull()) & (x.xb==xb)]) * 1.0 / len(x) 
            
#             print df.groupby('gen').enc.apply(ratio_count)
            
            df = df[(~df.ywm.isnull()) & (~df.gen.isnull())]
            
            df = df.iloc[:500]
            
#             g = df.groupby(['gen']).enc.apply(ratio_count)
            g = df.groupby(['gen'])
            
            rtn = pandas.DataFrame()
            
            rtn[u'男'] = g.apply(ratio_count, u'男')
            rtn[u'女'] = g.apply(ratio_count, u'女')
            rtn[u'总'] = g.apply(ratio_count)
            
            rtn.index.names = [u'年代'] 
            
            rtn.plot(kind='bar', rot=0, title=u'明星取传统英文名字和年代的关系')
            

            plt.show()
            print rtn
#             df.to_excel('/home/winston/fx1.xls', 'fx1')
            
            return

        if options.get('export'):
            count = options.get('export')
            q = PersonRecord.objects.filter(Q(zy__contains='演员') |Q( zy__contains='导演') | Q(zy__contains='歌手') | Q(zy__contains='模特'), updated=1).order_by('-bd_index')[:count]
            df = pandas.DataFrame(list(q.values('zwm','ywm','csny', 'xb', 'bd_index')))
            df.to_excel('/home/winston/data.xls', 'stars')
            return 
            
            
        if options.get('fx2'):
            q = PersonRecord.objects.filter(Q(zy__contains='演员') |Q( zy__contains='导演') | Q(zy__contains='歌手') | Q(zy__contains='模特'), updated=1).order_by('-bd_index')
            df = pandas.DataFrame(list(q.values('zwm','ywm','csny', 'xb', 'bd_index')))
            df.csny = df.csny.astype(datetime.date)
            df['gen'] = df.csny.apply(lambda x:(x.year -1900)/10 * 10 if x else None)
            df['enc'] = map(lambda x: CommonEnglishNames.get_english_name_gender_count(x), df.ywm)
            df['fontsize'] = df.bd_index * 30.0 / df.bd_index.max()
#             df.xb = df.xb.apply(lambda x: {u'男':'M', u"女":'F'}.get(x))
            
#             def ratio_count(x, xb=None):
#                 if xb is None:
#                     return len(x[~x.enc.isnull()]) * 1.0 / len(x)
#                 return len(x[(~x.enc.isnull()) & (x.xb==xb)]) * 1.0 / len(x) 
#             
# #             print df.groupby('gen').enc.apply(ratio_count)
            
            df = df[(~df.ywm.isnull()) & (~df.gen.isnull())]
            
            df = df.iloc[:500]
            print df

#             circle1 = plt.Circle((0, 0), 0.2, color='r')
#             circle2 = plt.Circle((0.5, 0.5), 0.2, color='blue')
#             circle3 = plt.Circle((1, 1), 0.2, color='g', clip_on=False)
            
#             plt.text
            fig, ax = plt.subplots() # note we must use plt.subplots, not plt.subplot
            # (or if you have an existing figure)
            # fig = plt.gcf()
            # ax = fig.gca()
#             ax.add_artist(circle1)
#             ax.add_artist(circle2)
#             ax.add_artist(circle3)
            def get_name_text(x):
                return '%s\n%s' % (x.zwm, get_first_english_name(x.ywm))
            
            def get_face_color(x):
                if numpy.isnan(x.enc):
                    return 'green'
                return 'red'
            
            def plot_name(x):
                fc = get_face_color(x)
                item = ax.text(x.csny.year, x.bd_index, get_name_text(x), color='black', alpha=0.5, bbox=dict(facecolor=fc, edgecolor='red', boxstyle='round,pad=1', alpha=0.5))
#                 item = ax.text(x.csny.year, x.bd_index, get_name_text(x), color='black', alpha=0.5 )#,bbox=dict(facecolor='green', edgecolor='red', boxstyle='round,pad=1'))
                item.set_fontsize(x.fontsize)
                item.set_ha('center')
                item.set_va('center')
                
                
#             plot_name(df.iloc[0])
#             plot_name(df.iloc[1])
            for i in range(len(df)):
                plot_name(df.iloc[i])
            
            plt.ylim((df.bd_index.min(),df.bd_index.max() * 1.2))
            plt.xlim((df.csny.min().year, df.csny.max().year))
#             t = '%s\n%s' % (df.iloc[0].zwm, df.iloc[0].ywm)
#             item = ax.text(0.5, 0.2, get_name_text(df.iloc[0]), color='black', 
#                     bbox=dict(facecolor='green', edgecolor='red', boxstyle='round,pad=1'))
#             item.set_fontsize(30)
# 
# 
# #             t = '%s\n%s' % (df.iloc[1].zwm, df.iloc[1].ywm)
#             item = ax.text(0.2, 0.5, get_name_text(df.iloc[1]), color='black', 
#                     bbox=dict(facecolor='green', edgecolor='red', boxstyle='round,pad=1'))
#             item.set_fontsize(3)
# 
#             item = ax.text(0.1, 0.6, get_name_text(df.iloc[2]), color='black', 
#                     bbox=dict(facecolor='green', edgecolor='red', boxstyle='round,pad=1'))
#             item.set_fontsize(0.1)
            
            plt.show()
            
#             g = df.groupby(['gen']).enc.apply(ratio_count)
#             g = df.groupby(['gen'])
#             
#             rtn = pandas.DataFrame()
#             
#             rtn[u'男'] = g.apply(ratio_count, u'男')
#             rtn[u'女'] = g.apply(ratio_count, u'女')
#             rtn[u'总'] = g.apply(ratio_count)
#             
#             rtn.index.names = [u'年代'] 
#             
#             rtn.plot(kind='bar', rot=0, title=u'明星取传统英文名字和年代的关系')
#             
# 
#             plt.show()
#             print rtn
#             df.to_excel('/home/winston/fx1.xls', 'fx1')
            
            return


