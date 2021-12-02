import logging
from copy import deepcopy

from bfo.services.clients import GirboClient
from bfo.services.statements_loader import StatementPageLoader
from bfo.tasks import load_statement_page_task

load_statements_logger = logging.getLogger('load_statements')


class StatementsLoader:
    DEFAULT_PERIODS = ['2019', '2020']
    DEFAULT_PARAMS = {
        'fileType': 'BFO',
        'sort': 'id,asc',
        'size': '2000',
    }

    def __init__(self):
        self.girbo_client = GirboClient()

    def prepare_args(self, params, periods):
        params_for_request = deepcopy(self.DEFAULT_PARAMS)
        if isinstance(params, dict):
            params_for_request.update(**params)

        periods_for_request = self.DEFAULT_PERIODS
        if isinstance(periods, list):
            periods_for_request = periods

        return params_for_request, periods_for_request

    def load(self, params=None, periods=None):
        params, periods = self.prepare_args(
            params=params,
            periods=periods,
        )
        page = params.get('page', 0)
        for period in periods:
            params.update({
                'period': period,
                'page': page,
            })
            response = StatementPageLoader(
                params=params,
            ).load()
            total_pages = response['totalPages']
            for request_page in range(page + 1, total_pages):
                params.update({
                    'page': request_page,
                })
                load_statement_page_task.delay(
                    params=params,
                )
