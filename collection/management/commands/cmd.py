from django.core.management.base import BaseCommand
from collection.models import PersonRecord

class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('args', nargs='*', type=str)
        
        # Named (optional) arguments
        parser.add_argument('--name', nargs = "?",default=None, help='add a name')


    def handle(self, *args, **options):
        if options.get('name'):
            name = options.get('name').decode('cp936')#.decode('utf8')
            return PersonRecord.add(name)
