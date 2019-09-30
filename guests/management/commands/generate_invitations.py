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
            '--type',
            type=str,
            dest='type',
            default=None,
            help="Generate to only this type"
        )

    def handle(self, *args, **options):
        generate_invitations_for_event(test_only=not options['save'], party_type=options['type'])
