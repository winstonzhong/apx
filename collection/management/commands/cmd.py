# encoding: utf-8
from django.core.management.base import BaseCommand
from django.db.models.query_utils import Q

from collection.models import PersonRecord, CommonEnglishNames
from collection.tool_net import get_name_info, JBQMNameParseError, \
    get_common_english_names
from utils.tool_env import force_unicode, force_utf8


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
        


    def handle(self, *args, **options):
        """参数指向"""
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
