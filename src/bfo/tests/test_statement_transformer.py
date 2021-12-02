import datetime
from collections import OrderedDict

from asgiref.sync import async_to_sync
from django.test import TestCase

from bfo.models import OrgStatement
from bfo.services.statements_loader import StatementFileBase
from bfo.services_async.statements.statements_transformer import StatementsTransformer
from bfo.tests.statement_data import (
    girbo_no_buhotch_json,
    girbo_no_boupr_json,
    girbo_no_buhotch_special_json,
    girbo_no_boupr_5_02v_json,
    transformed_no_buhotch,
    transformed_no_boupr,
    transformed_no_buhotch_special,
    transformed_no_boupr_5_02v,
)


class TestStatementTransformer(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.inn = '7724508296'
        cls.kpp = '772401001'
        cls.buhotch_org = OrgStatement.objects.create(
            report_date=datetime.date(2020, 12, 31),
            inn=cls.inn,
            kpp=cls.kpp,
            data_from_src=StatementFileBase.prepare_data_from_src(girbo_no_buhotch_json),
        )
        cls.boupr_org = OrgStatement.objects.create(
            report_date=datetime.date(2020, 12, 31),
            inn=cls.inn,
            kpp=cls.kpp,
            data_from_src=StatementFileBase.prepare_data_from_src(girbo_no_boupr_json),
        )
        cls.buhotch_org_special = OrgStatement.objects.create(
            report_date=datetime.date(2020, 12, 31),
            inn=cls.inn,
            kpp=cls.kpp,
            data_from_src=StatementFileBase.prepare_data_from_src(girbo_no_buhotch_special_json),
        )
        cls.boupr_org_5_02v = OrgStatement.objects.create(
            report_date=datetime.date(2020, 12, 31),
            inn=cls.inn,
            kpp=cls.kpp,
            data_from_src=StatementFileBase.prepare_data_from_src(girbo_no_boupr_5_02v_json),
        )

    def test_statement_transform_buhotch_org(self):
        statements_transformer = async_to_sync(StatementsTransformer.create)()
        buhotch_org = async_to_sync(statements_transformer.transform)(self.buhotch_org)
        excepted_buhotch_org = OrderedDict([
            ('year', 2020),
            ('knd', '0710099'),
        ])
        excepted_buhotch_org.update(transformed_no_buhotch)
        self.assertDictEqual(
            buhotch_org,
            excepted_buhotch_org
        )

    def test_statement_transform_boupr_org(self):
        statements_transformer = async_to_sync(StatementsTransformer.create)()
        boupr_org = async_to_sync(statements_transformer.transform)(self.boupr_org)
        excepted_transformed_no_boupr = OrderedDict([
            ('year', 2020),
            ('knd', '0710096'),
        ])
        excepted_transformed_no_boupr.update(transformed_no_boupr)
        self.assertDictEqual(
            boupr_org,
            excepted_transformed_no_boupr
        )

    def test_statement_transform_buhotch_org_special(self):
        statements_transformer = async_to_sync(StatementsTransformer.create)()
        buhotch_org_special = async_to_sync(statements_transformer.transform)(self.buhotch_org_special)
        excepted_buhotch_org_special = OrderedDict([
            ('year', 2020),
            ('knd', '0710099'),
        ])
        excepted_buhotch_org_special.update(transformed_no_buhotch_special)
        self.assertDictEqual(
            buhotch_org_special,
            excepted_buhotch_org_special,
        )

    def test_statement_transform_boupr_org_5_02v(self):
        statements_transformer = async_to_sync(StatementsTransformer.create)()
        boupr_org_5_02v = async_to_sync(statements_transformer.transform)(self.boupr_org_5_02v)
        excepted_boupr_org_5_02v = OrderedDict([
            ('year', 2020),
            ('knd', '0710096'),
        ])
        excepted_boupr_org_5_02v.update(transformed_no_boupr_5_02v)
        self.assertDictEqual(
            boupr_org_5_02v,
            excepted_boupr_org_5_02v,
        )
