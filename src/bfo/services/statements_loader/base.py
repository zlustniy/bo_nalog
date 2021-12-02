import datetime
import json
import logging

import xmltodict
from django.forms.models import model_to_dict
from jsondiff import diff as json_diff

from bfo.models import (
    PreviousOrgStatement,
    DifferenceStatement,
    FinancialStatementFile,
)
from bfo.services.clients import GirboClient

load_statement_file_logger = logging.getLogger('load_statement_file')


class StatementFileBase:
    log_prefix = 'StatementFileLoader'

    def __init__(self, file_token, file):
        self.girbo_client = GirboClient()
        self.file_token = file_token
        self.file = file

    def process(self):
        raise NotImplementedError()

    def save_to_db(self, response_dict_xml):
        raise NotImplementedError()

    @staticmethod
    def process_response(response):
        response_dict_xml = xmltodict.parse(response.content)
        return response_dict_xml

    @staticmethod
    def prepare_data_from_src(response_dict_xml):
        return response_dict_xml

    @staticmethod
    def get_saved_data_from_src(org_statement):
        return org_statement.data_from_src

    @staticmethod
    def get_date_by_year_str(report_date_year):
        return datetime.date(int(report_date_year), 12, 31)

    @staticmethod
    def get_diff(saved_data_from_src, current_data_from_src):
        return json.loads(json_diff(saved_data_from_src, current_data_from_src, syntax='explicit', dump=True))

    def process_difference(self, org_statement, response_dict_xml):
        diff = self.get_diff(
            saved_data_from_src=self.get_saved_data_from_src(org_statement),
            current_data_from_src=response_dict_xml,
        )
        if not diff:
            org_statement.save()  # update changed_at
            load_statement_file_logger.debug(
                f'%s: (Token: `%s`) Statement has not changed. `changed_at` updated.',
                self.log_prefix,
                self.file_token,
            )
            return

        dict_org_statement_object = model_to_dict(org_statement)
        dict_org_statement_object.pop('id')
        dict_org_statement_object['statement_file'] = FinancialStatementFile.objects.get(
            id=dict_org_statement_object['statement_file'],
        )

        previous_org_statement = PreviousOrgStatement.objects.create(**dict_org_statement_object)

        org_statement.data_from_src = self.prepare_data_from_src(response_dict_xml)
        org_statement.save()

        difference_statement = DifferenceStatement.objects.create(
            org_statement=org_statement,
            previous_org_statement=previous_org_statement,
            diff=self.prepare_data_from_src(diff),
        )
        load_statement_file_logger.debug(
            f'%s: (Token: `%s`) Statement has changed. '
            'OrgStatement.id=`%s`, PreviousOrgStatement.id=`%s`, DifferenceStatement.id=`%s`',
            self.log_prefix,
            self.file_token,
            org_statement.id,
            previous_org_statement.id,
            difference_statement.id,
        )
