# encoding: utf-8
from collection.models import PersonRecord, CommonEnglishNames
from collection.tool_net import get_name_info, JBQMNameParseError, \
    get_common_english_names, get_missing_birthday, get_real_name, \
    get_missing_gender, get_name_img
from django.core.management.base import BaseCommand
from django.db.models.query_utils import Q
from matplotlib.ticker import IndexFormatter
from pylab import mpl
from utils.tool_env import force_unicode, force_utf8, reformat_date_str, \
    get_first_english_name, is_english_name
import datetime
import matplotlib.pyplot as plt
import numpy
import pandas
import time



mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

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
        parser.add_argument('--fx1', action='store_true', default=False, help=u'明星取英文名字和年代的关系')
        parser.add_argument('--fx2', action='store_true', default=False, help=u'明星取英文名字年代、热度、土鳖程度关系散点图')
        parser.add_argument('--fx3', action='store_true', default=False, help=u'明星名字分数、热度关系极坐标扇面图')
        parser.add_argument('--fx4', action='store_true', default=False, help=u'明星英文名重名图1')
        parser.add_argument('--fx5', action='store_true', default=False, help=u'明星英文名重名图2')
        
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



        if options.get('export'):
            count = options.get('export')
            q = PersonRecord.objects.filter(Q(zy__contains='演员') |Q( zy__contains='导演') | Q(zy__contains='歌手') | Q(zy__contains='模特'), updated=1).order_by('-bd_index')[:count]
            df = pandas.DataFrame(list(q.values('zwm','ywm','csny', 'xb', 'bd_index')))
            df.to_excel('/home/winston/data.xls', 'stars')
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
            
#             rtn.plot(kind='bar', rot=0, title=u'明星取传统英文名字和年代的关系')
            
            
            fig, ax = plt.subplots()
            width = 2
            rects1 = ax.bar(rtn.index, rtn[u'男'], width, color='r')
            rects2 = ax.bar(rtn.index + width, rtn[u'女'], width, color='g')
            rects3 = ax.bar(rtn.index+ width*2, rtn[u'总'], width, color='b')


            def autolabel(rects, color='b'):
                """
                Attach a text label above each bar displaying its height
                """
                for rect in rects:
                    height = rect.get_height()
                    ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                    '%s' % round(float(height), 2),
                    ha='center', va='bottom', color=color)
            print df
            print rtn
#             autolabel(rects1, color='r')
#             autolabel(rects2, color='g')
#             autolabel(rects3, color='b')
            plt.title(u'明星取传统英文名字和年代的关系')
            ax.legend((rects1[0], rects2[0], rects3[0]), (u'男', u'女', u'总'))
            plt.show()
            
#             df.to_excel('/home/winston/fx1.xls', 'fx1')
            
            return

            
        if options.get('fx2'):
            q = PersonRecord.objects.filter(Q(zy__contains='演员') |Q( zy__contains='导演') | Q(zy__contains='歌手') | Q(zy__contains='模特'), updated=1).order_by('-bd_index')
            df = pandas.DataFrame(list(q.values('zwm','ywm','csny', 'xb', 'bd_index')))
            df.csny = df.csny.astype(datetime.date)
            df['gen'] = df.csny.apply(lambda x:(x.year -1900)/10 * 10 if x else None)
            df['enc'] = map(lambda x: CommonEnglishNames.get_english_name_gender_count(x), df.ywm)
            df['fontsize'] = df.bd_index * 30.0 / df.bd_index.max()
            df['is_english_name'] = df.apply(lambda x: is_english_name(x['zwm'], x['ywm']), axis=1)
            
            df = df[(~df.ywm.isnull()) & (~df.gen.isnull()) & df.is_english_name==True]
#             df.to_csv('e:/test/test2.csv',encoding='utf8')
            df = df.iloc[:500]
            print df
            color_green = 'green'
            color_red = 'red'
            max_green = None
            max_red = None
            fig, ax = plt.subplots() # note we must use plt.subplots, not plt.subplot
            def get_name_text(x):
                return '%s\n%s' % (x.zwm, get_first_english_name(x.ywm))
            
            def get_face_color(x):
                if numpy.isnan(x.enc):
                    return color_green
                return color_red

            def get_max_green_and_red(x, max_green, max_red):
                color = get_face_color(x)
                if max_green is None and color == color_green:
                    max_green = x
                if max_red is None and color == color_red:
                    max_red = x
                return max_green, max_red

            def plot_name(x):
                fc = get_face_color(x)
                item = ax.text(x.csny.year, x.bd_index, get_name_text(x), color='black', alpha=0.5, bbox=dict(facecolor=fc, edgecolor='red', boxstyle='round,pad=1', alpha=0.5))
#                 item = ax.text(x.csny.year, x.bd_index, get_name_text(x), color='black', alpha=0.5 )#,bbox=dict(facecolor='green', edgecolor='red', boxstyle='round,pad=1'))
                item.set_fontsize(x.fontsize)
                item.set_ha('center')
                item.set_va('center')
                
            for i in xrange(len(df)):
                plot_name(df.iloc[i])
                max_green, max_red = get_max_green_and_red(df.iloc[i], max_green, max_red)
            
            def set_annotate(x, text_color='black'):
                if x is not None:
                    ax.annotate('%s/%s' % (x.zwm, x.ywm), 
                                xy=(x.csny.year, x.bd_index), 
                                xytext=(x.csny.year, x.bd_index.max() * 1.2),
                                arrowprops=dict(arrowstyle="->", facecolor='black'),
                                color=text_color,
                                fontsize=12,
                                       )
            
            set_annotate(max_green)
            set_annotate(max_red)
            plt.ylim((df.bd_index.min(),df.bd_index.max() * 1.2))
            plt.xlim((df.csny.min().year, df.csny.max().year))
            df.sort(columns='bd_index', ascending=True)
            plt.show()
            
            return
        
        if options.get('fx3'):
            q = PersonRecord.objects.filter(Q(zy__contains='演员') |Q( zy__contains='导演') | Q(zy__contains='歌手') | Q(zy__contains='模特'), updated=1).order_by('-bd_index')
            df = pandas.DataFrame(list(q.values('zwm', 'bd_index', 'name_shuli')))
            df.zwm = df.zwm.apply(lambda x:get_real_name(x))
            df = df.drop_duplicates()

#             df = df[(~df.gen.isnull())]
            score_map = {u'大凶':-90, u'半凶':-70,u'凶':-50, u'半吉':-30, u'吉':-10, }
            
            def get_name_score(s):
                return sum(map(lambda x:score_map.get(x, 0), s.split(','))) + 360
            
            df['score'] = df.name_shuli.apply(get_name_score)
            df['heat'] = df.bd_index * 10.0 / df.bd_index.max()
            
            df = df.iloc[:1000]
         
            print df
            N = len(df)
#             theta = numpy.linspace(0.0, 2 * numpy.pi, N, endpoint=False)
#             theta = [0] * N
            theta = 2 * numpy.pi * numpy.random.rand(N)
            radii = df.heat.tolist()
            
            width = map(lambda x:x * 2 * numpy.pi / 360.0, df.score)
            
            ax = plt.subplot(111, projection='polar')
            
            bars = ax.bar(theta, radii, width=width, bottom=0.0)

            def add_names(x):
                item = ax.text(x.csny.year, x.bd_index, get_name_text(x), color='black', alpha=0.5, bbox=dict(facecolor=fc, edgecolor='red', boxstyle='round,pad=1', alpha=0.5))
#                 item = ax.text(x.csny.year, x.bd_index, get_name_text(x), color='black', alpha=0.5 )#,bbox=dict(facecolor='green', edgecolor='red', boxstyle='round,pad=1'))
                item.set_fontsize(x.fontsize)
                item.set_ha('center')
                item.set_va('center')

            def autolabel(rect, idx, color='black', max_display_num=10):
                """
                Attach a text label above each bar displaying its height
                """
#                 for rect in rects:
#                     print dir(rect)
                if idx < max_display_num:
                    height = rect.get_height()
                    ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
#                     '%s(%s)' % (df.iloc[idx].zwm, df.iloc[idx].name_shuli),
                    df.iloc[idx].zwm,
                    ha='center', va='bottom', color=color)


#             autolabel(bars)
#             print 'bars', bars
            idx = 0
            for r, bar in zip(radii, bars):
                autolabel(bar, idx)
                bar.set_facecolor(plt.cm.hsv(r / 10.))
                bar.set_alpha(0.5)
                idx += 1
            plt.title(u'百度热搜明星中文名数理Top 10')
            plt.show()

        if options.get('fx4'):
            q = PersonRecord.objects.filter(Q(zy__contains='演员') |Q( zy__contains='导演') | Q(zy__contains='歌手') | Q(zy__contains='模特'), updated=1).order_by('-bd_index')
            df = pandas.DataFrame(list(q.values('zwm','ywm','csny', 'xb', 'bd_index')))
            df.csny = df.csny.astype(datetime.date)
            df.zwm = df.zwm.apply(lambda x:get_real_name(x))
            
            df = df.drop_duplicates()
            
            df['gen'] = df.csny.apply(lambda x:(x.year -1900)/10 * 10 if x else None)
            df['words'] = map(lambda x: CommonEnglishNames.get_unique_words(x), df.ywm)
            df['word'] = map(lambda x: x[0].capitalize() if x else None, df.words)
            
            df = df[(~df.word.isnull()) & (~df.gen.isnull())]
            
            df = df.iloc[:500]
            g = df.groupby(['word']).zwm.count().sort_values(ascending=False)[:10]
#             g = g[(g > 4)]
            print g.head(10)
            g.plot.pie()
            plt.title(u'明星常取英文名Top 10')
            plt.show()

        if options.get('fx5'):
            q = PersonRecord.objects.filter(Q(zy__contains='演员') |Q( zy__contains='导演') | Q(zy__contains='歌手') | Q(zy__contains='模特'), updated=1).order_by('-bd_index')
            df = pandas.DataFrame(list(q.values('zwm','ywm','csny', 'xb', 'bd_index')))
            df.csny = df.csny.astype(datetime.date)
            df.zwm = df.zwm.apply(lambda x:get_real_name(x))
            
            df = df.drop_duplicates()
            
            df['gen'] = df.csny.apply(lambda x:(x.year -1900)/10 * 10 if x else None)
            df['words'] = map(lambda x: CommonEnglishNames.get_unique_words(x), df.ywm)
            df['word'] = map(lambda x: x[0].capitalize() if x else None, df.words)
            
            df = df[(~df.word.isnull()) & (~df.gen.isnull())]
            
            df = df.iloc[:500]
            g = df.groupby(['word']).zwm.count().sort_values(ascending=False)
            
            print g.head(10)
            display_en = g.index[1]
            df1 =  df[df.word.str.contains(display_en)].copy()
            df1['year'] = map(lambda x:x.year, df1.csny)
            
            
            df1['x'] = (df1.year - df1.year.min()) * 1.0 / (df1.year.max() - df1.year.min())
            
#             df1.bd_index.to_list
#             df1['y'] = df1.bd_index * 1.0 /df1.bd_index.max()
            df1 = df1.drop_duplicates('zwm').drop_duplicates('ywm')
            print df1           
#             return
            
            def plot_name_img(ax, i):
                im = plt.imread(get_name_img(df1.iloc[i].zwm), 'jpeg')
                imh, imw, _ = im.shape
                [x0, y0], [x1, y1] = ax.bbox.get_points()
#                 limx = ax.get_xlim()
#                 limy = ax.get_ylim()
                limx = 0, len(df1)
                limy = 0, len(df1)
                
                datawidth = limx[1] - limx[0]
                dataheight = limy[1] - limy[0]
                pixelwidth = x1 - x0
                pixelheight = y1 - y0
                adaptedwidth = imw * (datawidth / pixelwidth)
                adaptedheight = imh * (dataheight / pixelheight)
                    
                x = df1.iloc[i].x * len(df1)
                y = len(df1) - i
                
#                 print ax.bbox.get_points()
#                 print adaptedwidth, adaptedheight
                ax.imshow(im, origin="upper",extent=(x, x + adaptedwidth, y, y + adaptedheight), alpha=0.5)
                
                def _add_label():
                    ax.text(x + adaptedwidth/2, y - 0.5 ,
                            df1.iloc[i].zwm,
                            ha='center', va='bottom')
                _add_label()

            ax = plt.subplot(111)
#             limx = ax.set_xlim((df1.year.min(), df1.year.max()))
            ax.set_xlim((-1, len(df1)+5))
            ax.set_ylim((-1, len(df1)+5))
            ax.set_autoscale_on(False)
            
            ixlabel =map(lambda x: int(df1.year.min() + x * (df1.year.max() - df1.year.min()) * 1.0 / len(df1)), range(-1, len(df1)+5))
            
            ax.xaxis.set_major_formatter(IndexFormatter(ixlabel))
            
            for i in range(len(df1)):
                plot_name_img(ax, i)
#                 get_zwm(item, i)
            ax.set_title(u'英文名为%s的明星' % display_en)
            plt.show()         

