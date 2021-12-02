import logging

from aiohttp import ClientResponseError
from django.http import JsonResponse
from rest_framework import status

from bfo.services_async.fin_report_loader.exceptions import ReportFileNotFoundException
from bfo.services_async.fin_report_loader.report_interface import ReportInterface
from bfo.services_async.statements.statements_interface import StatementInterface
from ..serializers import ParamFinReportSerializer, ParamFinStatementsSerializer

bo_nalog_logger = logging.getLogger('bo_nalog_client')


async def fin_report_api_view(request):
    param_serializer = ParamFinReportSerializer(data=request.GET)
    if not param_serializer.is_valid(raise_exception=False):
        return JsonResponse(
            data=param_serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
    ogrn = param_serializer.validated_data['ogrn']
    year = param_serializer.validated_data['year']

    report_interface = ReportInterface()
    try:
        report_file = await report_interface.get_fin_report(
            ogrn=ogrn,
            year=year,
        )
    except ClientResponseError as e:
        bo_nalog_logger.exception('Ошибка при запросе файл для ogrn=%s year=%s: `%s`', ogrn, year, e)
        return JsonResponse(
            data={
                'detail': f'Файл для ogrn={ogrn} year={year} не удалось получить.',
            },
            status=status.HTTP_404_NOT_FOUND,
        )
    except ReportFileNotFoundException:
        return JsonResponse(
            data={
                'detail': f'Файл для ogrn={ogrn} year={year} отсутствует.',
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    response = await report_interface.wrap_as_http_response(
        report_file=report_file,
    )
    return response


async def fin_statements_api_view(request):
    param_serializer = ParamFinStatementsSerializer(data=request.GET)
    if not param_serializer.is_valid(raise_exception=False):
        return JsonResponse(
            data=param_serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
    inn = param_serializer.validated_data['inn']
    years = param_serializer.validated_data['years']
    compatibility = param_serializer.validated_data['compatibility']
    post_transform = param_serializer.validated_data['post_transform']

    data = await StatementInterface.get_fin_statement(
        inn=inn,
        years=years,
        compatibility=compatibility,
        post_transform=post_transform,
    )
    return JsonResponse(
        status=200,
        data=data,
    )
