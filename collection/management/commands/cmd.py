from django.core.management.base import BaseCommand

from collection.models import PersonRecord
from utils.tool_env import force_unicode


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
#         parser.add_argument('args', nargs='*', type=str)
        
        # Named (optional) arguments
        parser.add_argument('--add', nargs = "?",default=None, help='add a name')
        parser.add_argument('--run', nargs = "?",default=0, help='add a name', type=int)


    def handle(self, *args, **options):
        if options.get('add'):
            name = force_unicode(options.get('add'))
            PersonRecord.add(name)
        
        if options.get('run'):
            for i in xrange(options.get('run')):
                print i,
                r = PersonRecord.step()
                if not r:
                    break 
