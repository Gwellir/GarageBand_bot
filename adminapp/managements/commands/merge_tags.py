from django.core.management import BaseCommand
from django.db.models import Q

from tgbot.models import WorkRequest


class Command(BaseCommand):
    help = "merge tags"

    def handle(self, *args, **options):
        WorkRequest.objects.filter(Q(tag=3)).update(tag=2)
        WorkRequest.objects.filter(Q(tag=4) | Q(tag=5)).update(tag=3)
        WorkRequest.objects.filter(Q(tag=6)).update(tag=4)
        WorkRequest.objects.filter(Q(tag=7) | Q(tag=8)).update(tag=5)
