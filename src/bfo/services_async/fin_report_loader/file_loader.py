import logging

from asgiref.sync import sync_to_async, async_to_sync
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError

from bfo.models import (
    FinancialReportFile,
)
from ..clients import BoNalogClient

load_report_file_logger = logging.getLogger('load_report_file')


class ReportFileLoader:
    def __init__(self, ogrn, year):
        self.bo_nalog_client = BoNalogClient()
        self.ogrn = ogrn
        self.year = year

    @sync_to_async
    def create_financial_report_file(self, name, content, content_type, inn) -> FinancialReportFile:
        try:
            financial_report_file = FinancialReportFile.objects.create(
                file=SimpleUploadedFile(
                    name=name,
                    content=content,
                    content_type=content_type,
                ),
                ogrn=self.ogrn,
                year=self.year,
                is_active=True,
                inn=inn,
            )
        except IntegrityError as e:
            load_report_file_logger.error('FinancialReportFile duplicate error: %s', e)
            from .report_interface import ReportInterface
            financial_report_file = async_to_sync(ReportInterface.get_last_financial_report_file)(
                ogrn=self.ogrn,
                year=self.year,
            )
        return financial_report_file

    async def load(self) -> FinancialReportFile | None:
        load_report_file_logger.debug(
            'ReportFileLoader: (OGRN: `%s`) Start load statement document',
            self.ogrn,
        )
        response = await self.bo_nalog_client.get_nbo_organizations_search(ogrn=self.ogrn)
        load_report_file_logger.debug(
            'ReportFileLoader: (OGRN: `%s`) nbo_organizations_search Success loaded',
            self.ogrn,
        )
        if response and response['content']:
            content = response['content'][0]
            periods_bfo = self.get_periods_bfo(content['bfo'])
            if str(self.year) not in periods_bfo:
                return

            response, temporary_content = await self.bo_nalog_client.download_file_bfo(
                file_id=content['id'],
                period=self.year,
            )
            response.raise_for_status()
            report_file = await self.create_financial_report_file(
                name=response.headers['Content-Disposition'].replace("inline; filename*=UTF-8''", ""),
                content=temporary_content,
                content_type=response.headers['Content-Type'],
                inn=content['inn'],
            )

            load_report_file_logger.debug(
                'ReportFileLoader: (OGRN: `%s`) download_file_bfo Success loaded',
                self.ogrn,
            )
            return report_file

    @staticmethod
    def get_periods_bfo(bfo):
        return [i['period'] for i in bfo]
