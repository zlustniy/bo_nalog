import os

from asgiref.sync import sync_to_async
from django.http import HttpResponse
from django.utils.http import urlquote

from bfo.models import FinancialReportFile
from project.services.file_response import FileResponse
from .exceptions import ReportFileNotFoundException
from .file_loader import ReportFileLoader


class ReportInterface:
    @staticmethod
    @sync_to_async
    def get_last_financial_report_file(ogrn, year):
        return FinancialReportFile.objects.filter(
            ogrn=ogrn,
            year=year,
            is_active=True,
        ).last()

    async def get_fin_report(self, ogrn, year):
        report_file = await self.get_last_financial_report_file(
            ogrn=ogrn,
            year=year
        )

        if report_file is not None:
            return report_file
        report_file = await ReportFileLoader(ogrn=ogrn, year=year).load()
        if not report_file:
            raise ReportFileNotFoundException()

        return report_file

    @staticmethod
    async def wrap_as_http_response(report_file: FinancialReportFile) -> HttpResponse:
        filename = os.path.basename(report_file.file.name)
        response = await FileResponse.get_response(file_obj=report_file.file)
        response['Content-Disposition'] = f'attachment; filename="{urlquote(filename)}"; filename*=UTF-8\'\'{filename}'
        response['Content-Type'] = 'application/pdf'
        return response
