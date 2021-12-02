import logging

from django.core.management.base import BaseCommand

from bfo.services.statements_loader import StatementsLoader

load_logger = logging.getLogger('load_statements')


class Command(BaseCommand):
    def handle(self, *args, **options):
        statements_loader = StatementsLoader()
        statements_loader.load()
