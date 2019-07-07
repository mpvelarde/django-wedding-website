from optparse import make_option
from django.core.management import BaseCommand
from guests import csv_import
from guests.save_the_date import send_save_the_dates_by_type, clear_all_save_the_dates


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--send',
            action='store_true',
            dest='send',
            default=False,
            help="Actually send emails"
        )
        parser.add_argument(
            '--mark-sent',
            action='store_true',
            dest='mark_sent',
            default=False,
            help="Mark as sent"
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            dest='reset',
            default=False,
            help="Reset sent flags"
        )

        parser.add_argument(
            '--type',
            type=str,
            dest='type',
            default='scotland',
            help="Send to only this type"
        )

    def handle(self, *args, **options):
        if options['reset']:
            clear_all_save_the_dates()
        send_save_the_dates_by_type(test_only=not options['send'], mark_as_sent=options['mark_sent'], ptype=options['type'])
