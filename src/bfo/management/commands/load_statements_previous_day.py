import datetime
import logging

from django.core.management.base import BaseCommand

from bfo.services.statements_loader import StatementsLoader

load_logger = logging.getLogger('load_statements')


class Command(BaseCommand):
    def handle(self, *args, **options):
        params = {
            'dateFrom': str((datetime.datetime.today() - datetime.timedelta(days=1)).date()),
        }
        statements_loader = StatementsLoader()
        statements_loader.load(params)
