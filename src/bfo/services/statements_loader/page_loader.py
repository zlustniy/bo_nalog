import datetime
import logging
from dataclasses import dataclass

from django.db import transaction

from bfo.models import (
    FinancialStatementFile,
    FinancialStatementPage,
    FinancialReportFile,
)
from bfo.services.clients import GirboClient
from bfo.tasks import load_statement_file_task

load_statement_page_logger = logging.getLogger('load_statement_page')


@dataclass
class ResponseContentItem:
    id: int
    inn: int
    fileName: str
    fileType: str
    reportType: str
    period: str
    uploadDate: datetime.date
    token: str


class StatementPageLoader:
    def __init__(self, params):
        self.girbo_client = GirboClient()
        self.params = params
        self.page_number = params['page']

    def load(self):
        load_statement_page_logger.debug(
            'StatementPageLoader: (page=`%s` params=`%s`) Start load page',
            self.page_number,
            self.params,
        )
        response = self.girbo_client.get_statement_page(params=self.params)
        load_statement_page_logger.debug(
            'StatementPageLoader: (page=`%s` params=`%s`) Success loaded',
            self.page_number,
            self.params,
        )
        self.process_response(
            response=response,
        )
        load_statement_page_logger.debug(
            'StatementPageLoader: (page=`%s` params=`%s`) Success saved to db',
            self.page_number,
            self.params,
        )
        return response

    def process_response(self, response):
        response_content_items = []
        inn_for_invalidation = []
        with transaction.atomic():
            downloaded_page = FinancialStatementPage.objects.create(
                year=int(self.params['period']),
                page=response['page'],
                total_pages=response['totalPages'],
                size=response['size'],
                actual_size=len(response['content']),
                sort=response['sort'],
                params=self.params,
            )
            for response_content_item in response['content']:
                item = ResponseContentItem(**response_content_item)
                financial_statement_file, created = FinancialStatementFile.objects.get_or_create(
                    token=item.token,
                    defaults={
                        'downloaded_page': downloaded_page,
                        'external_id': item.id,
                        'inn': item.inn,
                        'file_name': item.fileName,
                        'report_type': item.reportType,
                        'period': item.period,
                        'upload_date': item.uploadDate,
                        'is_downloaded': False,
                    },
                )
                if created:
                    response_content_items.append(item)
                    inn_for_invalidation.append(item.inn)

            FinancialReportFile.objects.filter(inn__in=inn_for_invalidation).update(is_active=False)
        for response_content_item in response_content_items:
            load_statement_file_task.delay(
                file_token=response_content_item.token,
            )
