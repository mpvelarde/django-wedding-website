from optparse import make_option
from django.core.management import BaseCommand
from guests.invitation import generate_invitations_for_event

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--save',
            action='store_true',
            dest='save',
            default=False,
            help="Actually save invitation"
        )
        parser.add_argument(
            '--event-type',
            type=str,
            dest='event-type',
            default='both',
            help="Generate invitations to only this event"
        )

    def handle(self, *args, **options):
        generate_invitations_for_event(test_only=not options['save'], party_type=options['event-type'])
