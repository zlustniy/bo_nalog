import datetime
from urllib.parse import urlencode

from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext

from bfo.models import OrgStatement
from bfo.services.statements_loader import StatementFileBase
from bfo.tests.statement_data import (
    girbo_no_buhotch_json,
    girbo_no_boupr_json,
    girbo_no_boupr_another_kpp_json,
    transformed_no_buhotch,
    transformed_no_boupr,
    transformed_no_boupr_another_kpp,
)


class TestFinStatementsAPIView(TestCase):
    url_name = 'fin_statements_async'
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.inn = '7724508296'
        cls.kpp = '772401001'
        cls.buhotch_org_statement_2018 = OrgStatement.objects.create(
            report_date=datetime.date(2018, 12, 31),
            inn=cls.inn,
            kpp=cls.kpp,
            data_from_src=StatementFileBase.prepare_data_from_src(girbo_no_buhotch_json),
        )
        cls.boupr_org_statement_2019 = OrgStatement.objects.create(
            report_date=datetime.date(2019, 12, 31),
            inn=cls.inn,
            kpp=cls.kpp,
            data_from_src=StatementFileBase.prepare_data_from_src(girbo_no_boupr_json),
        )
        cls.buhotch_org_statement_2020 = OrgStatement.objects.create(
            report_date=datetime.date(2020, 12, 31),
            inn=cls.inn,
            kpp=cls.kpp,
            data_from_src=StatementFileBase.prepare_data_from_src(girbo_no_buhotch_json),
        )

    def test_success_transformed_data(self):
        url = reverse(self.url_name)
        url += '?' + urlencode([
            ('inn', self.inn),
            ('years', '2019,2020'),
        ])

        response = self.client.get(url)
        response_json = response.json()
        self.assertEqual(len(response_json['buhForms']), 2)
        self.assertDictEqual(
            response_json['buhForms'][0],
            {
                'year': 2019,
                'knd': '0710096',
                **transformed_no_boupr,
            }
        )
        self.assertDictEqual(
            response_json['buhForms'][1],
            {
                'year': 2020,
                'knd': '0710099',
                **transformed_no_buhotch,
            }
        )

    def test_success_original_data(self):
        url = reverse(self.url_name)
        url += '?' + urlencode([
            ('inn', self.inn),
            ('years', '2019,2020'),
            ('compatibility', False),
        ])

        response = self.client.get(url)
        response_json = response.json()
        self.assertEqual(len(response_json['buhForms']), 2)
        self.assertDictEqual(
            response_json['buhForms'][0],
            self.boupr_org_statement_2019.data_from_src,
        )
        self.assertDictEqual(
            response_json['buhForms'][1],
            self.buhotch_org_statement_2020.data_from_src,
        )

    def test_unknown_year(self):
        url = reverse(self.url_name)
        url += '?' + urlencode([
            ('inn', self.inn),
            ('years', '2010'),
        ])

        response = self.client.get(url)
        response_json = response.json()
        self.assertEqual(len(response_json['buhForms']), 0)
        self.assertEqual(response_json['buhForms'], [])

    def test_success_transformed_data_two_kpp(self):
        kpp = '772401002'
        OrgStatement.objects.create(
            report_date=datetime.date(2019, 12, 31),
            inn=self.inn,
            kpp=kpp,
            data_from_src=StatementFileBase.prepare_data_from_src(girbo_no_boupr_another_kpp_json),
        )
        url = reverse(self.url_name)
        url += '?' + urlencode([
            ('inn', self.inn),
            ('years', '2019,2020'),
        ])

        response = self.client.get(url)
        response_json = response.json()
        self.assertEqual(len(response_json['buhForms']), 2)
        self.assertDictEqual(
            response_json['buhForms'][0],
            {
                'year': 2019,
                'knd': '0710096',
                **transformed_no_boupr_another_kpp,
            }
        )
        self.assertDictEqual(
            response_json['buhForms'][1],
            {
                'year': 2020,
                'knd': '0710099',
                **transformed_no_buhotch,
            }
        )

    def test_success_original_data_two_kpp(self):
        kpp = '772402002'
        boupr_org_statement_2019_another_kpp = OrgStatement.objects.create(
            report_date=datetime.date(2019, 12, 31),
            inn=self.inn,
            kpp=kpp,
            data_from_src=StatementFileBase.prepare_data_from_src(girbo_no_boupr_another_kpp_json),
        )
        url = reverse(self.url_name)
        url += '?' + urlencode([
            ('inn', self.inn),
            ('years', '2019,2020'),
            ('compatibility', False),
        ])

        response = self.client.get(url)
        response_json = response.json()
        self.assertEqual(len(response_json['buhForms']), 2)
        self.assertDictEqual(
            response_json['buhForms'][0],
            boupr_org_statement_2019_another_kpp.data_from_src,
        )
        self.assertDictEqual(
            response_json['buhForms'][1],
            self.buhotch_org_statement_2020.data_from_src,
        )

    def test_kpp_exists(self):
        url = reverse(self.url_name)
        url += '?' + urlencode([
            ('inn', self.inn),
            ('years', '2020'),
        ])

        response = self.client.get(url)
        response_json = response.json()
        self.assertEqual(response_json['inn'], self.inn)
        self.assertEqual(response_json['kpp'], self.kpp)

    def test_multiple_value_of_years(self):
        url = reverse(self.url_name)
        url += '?' + urlencode([
            ('inn', self.inn),
            ('year', '2018'),
            ('year', '2019'),
            ('year', '2020'),
        ])
        response = self.client.get(url)
        response_json = response.json()
        self.assertEqual(len(response_json['buhForms']), 3)
        self.assertEqual(response_json['buhForms'][0]['year'], 2018)
        self.assertEqual(response_json['buhForms'][1]['year'], 2019)
        self.assertEqual(response_json['buhForms'][2]['year'], 2020)

    def test_multiple_value_of_years_separate_by_comma(self):
        url = reverse(self.url_name)
        url += '?' + urlencode([
            ('inn', self.inn),
            ('years', '2018,2019,2020'),
        ])
        response = self.client.get(url)
        response_json = response.json()
        self.assertEqual(len(response_json['buhForms']), 3)
        self.assertEqual(response_json['buhForms'][0]['year'], 2018)
        self.assertEqual(response_json['buhForms'][1]['year'], 2019)
        self.assertEqual(response_json['buhForms'][2]['year'], 2020)

    def test_multiple_value_of_years_year_not_is_digits(self):
        url = reverse(self.url_name)
        url += '?' + urlencode([
            ('inn', self.inn),
            ('year', '2018'),
            ('year', '2o19'),
            ('year', '2020'),
            ('year', '1999'),
            ('year', '3001'),
        ])
        response = self.client.get(url)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response_json,
            {
                'years': [
                    {},
                    [
                        gettext('A valid integer is required.'),
                    ],
                    {},
                    [
                        gettext('Ensure this value is greater than or equal to 2000.'),
                    ],
                    [
                        gettext('Ensure this value is less than or equal to 3000.'),
                    ]
                ],
            }
        )

    def test_multiple_value_of_years_separate_by_comma_year_not_is_digits(self):
        url = reverse(self.url_name)
        url += '?' + urlencode([
            ('inn', self.inn),
            ('years', '2018,2o19,2020,1999,3001'),
        ])
        response = self.client.get(url)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response_json,
            {
                'years': [
                    {},
                    [
                        gettext('A valid integer is required.'),
                    ],
                    {},
                    [
                        gettext('Ensure this value is greater than or equal to 2000.'),
                    ],
                    [
                        gettext('Ensure this value is less than or equal to 3000.'),
                    ]
                ],
            }
        )
