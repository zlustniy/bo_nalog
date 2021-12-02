import datetime
import logging

from bfo.models import (
    Setting,
    OrgStatement,
    TemporaryINN,
)
from bfo.services.statements_loader import StatementFileBase

load_statement_file_logger = logging.getLogger('load_statement_file')


class StatementFileLoaderTKS(StatementFileBase):
    log_prefix = 'StatementFileLoaderTKS'

    def process(self):
        if not self.file.file_name.startswith(('NO_BUHOTCH', 'NO_BOUPR')):
            load_statement_file_logger.debug(
                f'%s: (Token: `%s`) file_name does not start with (NO_BUHOTCH, NO_BOUPR)',
                self.log_prefix,
                self.file_token,
            )
            return
        load_statement_file_logger.debug(
            f'%s: (Token: `%s`) Start load statement document',
            self.log_prefix,
            self.file_token,
        )
        response = self.girbo_client.get_statement_file(file_token=self.file_token)
        load_statement_file_logger.debug(
            f'%s: (Token: `%s`) Success loaded',
            self.log_prefix,
            self.file_token,
        )
        response_dict_xml = self.process_response(response)
        load_statement_file_logger.debug(
            f'%s: (Token: `%s`) Success convert xml to dict',
            self.log_prefix,
            self.file_token,
        )
        self.save_to_db(response_dict_xml)

    def save_to_db(self, response_dict_xml):
        report_date_year = response_dict_xml['Файл']['Документ']['@ОтчетГод']
        report_date = self.get_date_by_year_str(report_date_year)
        inn = response_dict_xml['Файл']['Документ']['СвНП']['НПЮЛ']['@ИННЮЛ']
        kpp = response_dict_xml['Файл']['Документ']['СвНП']['НПЮЛ']['@КПП']

        load_statement_file_logger.debug(
            f'%s: (Token: `%s`) Statement document inn=`%s`, kpp=`%s`, report_date=`%s`',
            self.log_prefix,
            self.file_token,
            inn,
            kpp,
            report_date,
        )

        org_statement, created = OrgStatement.objects.get_or_create(
            report_date=report_date,
            inn=inn,
            kpp=kpp,
            defaults={
                'data_from_src': self.prepare_data_from_src(response_dict_xml),
                'statement_file': self.file,
            }
        )
        load_statement_file_logger.debug(
            f'%s: (Token: `%s`) Created status: `%s`. Statement id: `%s`',
            self.log_prefix,
            self.file_token,
            created,
            org_statement.id,
        )
        if not created:
            self.process_difference(org_statement, response_dict_xml)

        self.file.is_downloaded = True
        self.file.save(
            update_fields=['is_downloaded'],
        )
        setting = Setting.objects.first()
        setting.last_at = datetime.datetime.now()
        setting.save(update_fields=['last_at'])


class StatementFileLoaderBN(StatementFileBase):
    log_prefix = 'StatementFileLoaderBN'

    def process(self):
        load_statement_file_logger.debug(
            f'%s: (Token: `%s`) Start load statement document',
            self.log_prefix,
            self.file_token,
        )
        response_tiff = None
        # Пока не качаем и не обрабатываем tiff

        self.save_to_db(response_tiff)

    def save_to_db(self, response_tiff):
        org_statement, created = TemporaryINN.objects.get_or_create(
            statement_file=self.file,
            inn=self.file.inn,
        )
        if not created:
            load_statement_file_logger.debug(
                f'%s: (Token: `%s`) already uploaded',
                self.log_prefix,
                self.file_token,
            )
            return
        self.file.is_downloaded = True
        self.file.save(
            update_fields=['is_downloaded'],
        )
        setting = Setting.objects.first()
        setting.last_at = datetime.datetime.now()
        setting.save(update_fields=['last_at'])


class StatementFileLoaderCBSTR(StatementFileBase):
    log_prefix = 'StatementFileLoaderCBSTR'

    def process(self):
        pass

    def save_to_db(self, response):
        pass


class StatementFileLoaderCBNSTR(StatementFileBase):
    log_prefix = 'StatementFileLoaderCBNSTR'

    def process(self):
        pass

    def save_to_db(self, response):
        pass
