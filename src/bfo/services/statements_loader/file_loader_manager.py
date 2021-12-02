import logging

from bfo.models import (
    FinancialStatementFile,
)
from bfo.services.statements_loader.file_loader import (
    StatementFileLoaderTKS,
    StatementFileLoaderBN,
    StatementFileLoaderCBSTR,
    StatementFileLoaderCBNSTR,
)

load_statement_file_logger = logging.getLogger('load_statement_file')


class StatementFileManager:
    def __init__(self, file_token):
        self.file_token = file_token
        self.file = FinancialStatementFile.objects.get(
            token=self.file_token,
        )

    def load(self):
        report_type_map = {
            'BFO_TKS': StatementFileLoaderTKS,
            'BFO_BN': StatementFileLoaderBN,
            'BFO_CB_STR': StatementFileLoaderCBSTR,
            'BFO_CB_NSTR': StatementFileLoaderCBNSTR,
        }
        processor = report_type_map.get(self.file.report_type)
        if processor is None:
            load_statement_file_logger.debug(
                'Неизвестный тип отчетности!',
                self.file_token,
            )
            return
        processor(file_token=self.file_token, file=self.file).process()
