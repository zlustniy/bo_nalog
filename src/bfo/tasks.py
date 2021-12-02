import datetime
import logging

from celery.exceptions import SoftTimeLimitExceeded
from django.db.models import Q
from django.db.utils import IntegrityError

from bfo.models import (
    FinancialStatementFile,
)
from project.celery import app

load_logger = logging.getLogger('load_statements')
load_statement_file_logger = logging.getLogger('load_statement_file')
load_statement_page_logger = logging.getLogger('load_statement_page')


@app.task
def load_statements_previous_day_task(params=None, periods=None):
    from bfo.services.statements_loader import StatementsLoader
    params_to_request = {
        'dateFrom': (datetime.datetime.today() - datetime.timedelta(days=1)).date().strftime('%Y-%m-%d'),
    }
    if isinstance(params, dict):
        params_to_request.update(**params)
    load_logger.debug(
        'Run task `load_statements_previous_day_task` with params_to_request `%s`, periods `%s`',
        params_to_request,
        periods,
    )
    statements_loader = StatementsLoader()
    statements_loader.load(
        params=params_to_request,
        periods=periods,
    )


@app.task
def load_statements_task(params=None, periods=None):
    from bfo.services.statements_loader import StatementsLoader
    load_logger.debug(
        'Run task `load_statements_task` with params `%s`, periods `%s`',
        params,
        periods,
    )
    statements_loader = StatementsLoader()
    statements_loader.load(
        params=params,
        periods=periods,
    )


@app.task(
    queue='load_pages',
    bind=True,
    acks_late=True,
    acks_on_failure_or_timeout=False,
    max_retries=3,
    default_retry_delay=5,
    soft_time_limit=60 * 3,
)
def load_statement_page_task(self, params):
    from bfo.services.statements_loader import StatementPageLoader
    try:
        StatementPageLoader(params=params).load()
    except SoftTimeLimitExceeded:
        load_statement_page_logger.error(
            'Task `load_statement_page_task` killed by timeout (Attempt: `%s`)',
            self.request.retries,
        )
        self.retry()
    except IntegrityError as e:
        load_statement_page_logger.error(
            'Task `load_statement_page_task` an IntegrityError: `%s`',
            e,
        )
    except Exception as e:
        load_statement_page_logger.error(
            'Task `load_statement_page_task` an exception (Attempt: `%s`): `%s`',
            self.request.retries,
            e,
        )
        self.retry(exc=e)


@app.task(
    queue='load_files',
    bind=True,
    acks_late=True,
    acks_on_failure_or_timeout=False,
    max_retries=3,
    default_retry_delay=5,
    soft_time_limit=60 * 1,
)
def load_statement_file_task(self, file_token):
    from bfo.services.statements_loader import StatementFileManager
    try:
        StatementFileManager(file_token=file_token).load()
    except SoftTimeLimitExceeded:
        load_statement_page_logger.error(
            'Task `load_statement_file_task` killed by timeout (Attempt: `%s`)',
            self.request.retries,
        )
        self.retry()

    except Exception as e:
        load_statement_file_logger.error(
            'Task `load_statement_page_task` an exception (Attempt: `%s`): `%s`',
            self.request.retries,
            e,
        )
        self.retry(exc=e)


@app.task
def download_files_task():
    files = FinancialStatementFile.objects.filter(
        Q(is_downloaded=False),
        Q(file_name__startswith='NO_BUHOTCH') | Q(file_name__startswith='NO_BOUPR'),
    )
    for file in files:
        load_statement_file_task.delay(
            file_token=file.token,
        )
