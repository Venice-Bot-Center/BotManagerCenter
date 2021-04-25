from django.core.management.base import BaseCommand

from marea.cron import run


class Command(BaseCommand):
    help = "Run bot for pollini"

    def handle(self, *args, **kwargs):
        run()
