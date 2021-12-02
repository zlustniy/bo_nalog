import os

import mock
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from bfo.models import (
    Setting,
    OrgStatement,
    PreviousOrgStatement,
    DifferenceStatement,
    FinancialStatementPage,
    FinancialStatementFile,
    TemporaryINN,
)
from bfo.services.statements_loader import StatementsLoader


class MockXmlResponse:
    def __init__(self, content, inn=None, kpp=None):
        if inn:
            content = content.replace('ИННЮЛ="stringstri"', f'ИННЮЛ="{inn}"')
        if kpp:
            content = content.replace('КПП="stringstr"', f'КПП="{kpp}"')
        self.content = content.encode('utf-8')


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPOGATES=True,
)
class TestStatementsLoader(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root = User.objects.filter(is_superuser=True)
        cls.settings = Setting.objects.first()

    @mock.patch('bfo.services.clients.GirboClient.get')
    @mock.patch('bfo.services.clients.GirboClient.get_access_token_with_cache')
    def test_load_bfo_tks(self, mock_get_access_token_with_cache, mock_get):
        mock_get_access_token_with_cache.return_value = 'f9ea18de-5cc7-42f3-a091-071ee3b1fa80'
        mock_get.return_value = {
            "access_token": "f9ea18de-5cc7-42f3-a091-071ee3b1fa80",
            "token_type": "bearer",
            "scope": "api"
        }
        no_boupr_path = os.path.join(settings.BASE_DIR, 'bfo', 'tests', 'xml', 'NO_BOUPR_1_159_00_05_03_01.xsd.xml')
        no_buhoth_path = os.path.join(settings.BASE_DIR, 'bfo', 'tests', 'xml', 'NO_BUHOTCH_1_105_00_05_08_02.xsd.xml')

        no_boupr_content = open(no_boupr_path).read()
        no_buhoth_content = open(no_buhoth_path).read()
        mock_get.side_effect = [
            {
                "content": [
                    {
                        "id": 181,
                        "inn": 1111111111,
                        "fileName": "NO_BUHOTCH",
                        "fileType": "AZ",
                        "reportType": 'BFO_TKS',
                        "period": "2019",
                        "uploadDate": "2020-05-22",
                        "token": " 5df1ee2d46e0fb0001ac5111"
                    },
                    {
                        "id": 182,
                        "inn": 1111111112,
                        "fileName": "NO_BOUPR",
                        "fileType": "AZ",
                        "reportType": 'BFO_TKS',
                        "period": "2019",
                        "uploadDate": "2020-05-22",
                        "token": " 5df1ee2d46e0fb0001ac5122"
                    },
                    {
                        "id": 11,
                        "inn": 1234567877,
                        "fileName": "test10",  # Не подходящее название файла
                        "fileType": "AZ",
                        "reportType": 'BFO_TKS',
                        "period": "2019",
                        "uploadDate": "2020-05-22",
                        "token": " 5df1ee2d46e0fb0001ac5123"
                    }
                ],
                "totalPages": 1,
                "totalElements": 3,
                "sort": "inn: DESC,uploadDate: DESC",
                "page": 0,
                "size": 3
            },
            MockXmlResponse(no_buhoth_content, inn=1111111111, kpp=111111111),
            MockXmlResponse(no_boupr_content, inn=1111111112, kpp=111111112),

            {
                "content": [
                    {
                        "id": 191,
                        "inn": 1111111113,
                        "fileName": "NO_BUHOTCH",
                        "fileType": "AZ",
                        "reportType": 'BFO_TKS',
                        "period": "2020",
                        "uploadDate": "2020-05-22",
                        "token": " 5df1ee2d46e0fb0001ac5114"
                    },
                    {
                        "id": 192,
                        "inn": 1111111114,
                        "fileName": "NO_BOUPR",
                        "fileType": "AZ",
                        "reportType": 'BFO_TKS',
                        "period": "2020",
                        "uploadDate": "2020-05-22",
                        "token": " 5df1ee2d46e0fb0001ac5125"
                    },
                    {
                        "id": 12,
                        "inn": 1234567878,
                        "fileName": "test10",  # Не подходящее название файла
                        "fileType": "AZ",
                        "reportType": 'BFO_TKS',
                        "period": "2020",
                        "uploadDate": "2020-05-22",
                        "token": " 5df1ee2d46e0fb0001ac5126"
                    }
                ],
                "totalPages": 1,
                "totalElements": 3,
                "sort": "inn: DESC,uploadDate: DESC",
                "page": 0,
                "size": 3
            },
            MockXmlResponse(no_buhoth_content, inn=1111111113, kpp=111111113),
            MockXmlResponse(no_boupr_content, inn=1111111114, kpp=111111114),
        ]

        StatementsLoader().load()
        self.assertEqual(OrgStatement.objects.count(), 4)
        self.assertIsNotNone(OrgStatement.objects.first().statement_file)
        self.assertEqual(PreviousOrgStatement.objects.count(), 0)
        self.assertEqual(DifferenceStatement.objects.count(), 0)
        self.assertEqual(FinancialStatementPage.objects.count(), 2)
        self.assertEqual(FinancialStatementFile.objects.count(), 6)
        self.assertEqual(FinancialStatementFile.objects.filter(is_downloaded=True).count(), 4)

    @mock.patch('bfo.services.clients.GirboClient.get')
    @mock.patch('bfo.services.clients.GirboClient.get_access_token_with_cache')
    def test_load_with_diff(self, mock_get_access_token_with_cache, mock_get):
        mock_get_access_token_with_cache.return_value = 'f9ea18de-5cc7-42f3-a091-071ee3b1fa80'
        mock_get.return_value = {
            "access_token": "f9ea18de-5cc7-42f3-a091-071ee3b1fa80",
            "token_type": "bearer",
            "scope": "api"
        }
        no_boupr_path = os.path.join(settings.BASE_DIR, 'bfo', 'tests', 'xml', 'NO_BOUPR_1_159_00_05_03_01.xsd.xml')
        no_buhoth_path = os.path.join(settings.BASE_DIR, 'bfo', 'tests', 'xml', 'NO_BUHOTCH_1_105_00_05_08_02.xsd.xml')

        no_boupr_content = open(no_boupr_path).read()
        no_buhoth_content = open(no_buhoth_path).read()
        mock_get.side_effect = [
            {
                "content": [
                    {
                        "id": 181,
                        "inn": 1111111111,
                        "fileName": "NO_BUHOTCH",
                        "fileType": "AZ",
                        "reportType": 'BFO_TKS',
                        "period": "2019",
                        "uploadDate": "2020-05-22",
                        "token": " 5df1ee2d46e0fb0001ac5111"
                    },
                    {
                        "id": 182,
                        "inn": 1111111111,
                        "fileName": "NO_BOUPR",
                        "fileType": "AZ",
                        "reportType": 'BFO_TKS',
                        "period": "2019",
                        "uploadDate": "2020-05-22",
                        "token": " 5df1ee2d46e0fb0001ac5122"
                    },
                    {
                        "id": 11,
                        "inn": 1234567877,
                        "fileName": "test10",  # Не подходящее название файла
                        "fileType": "AZ",
                        "reportType": 'BFO_TKS',
                        "period": "2019",
                        "uploadDate": "2020-05-22",
                        "token": " 5df1ee2d46e0fb0001ac5123"
                    }
                ],
                "totalPages": 1,
                "totalElements": 3,
                "sort": "inn: DESC,uploadDate: DESC",
                "page": 0,
                "size": 3
            },
            MockXmlResponse(no_buhoth_content, inn=1111111111, kpp=111111111),
            MockXmlResponse(no_buhoth_content, inn=1111111111, kpp=111111111),

            {
                "content": [
                    {
                        "id": 191,
                        "inn": 1111111111,
                        "fileName": "NO_BUHOTCH",
                        "fileType": "AZ",
                        "reportType": 'BFO_TKS',
                        "period": "2020",
                        "uploadDate": "2020-05-22",
                        "token": " 5df1ee2d46e0fb0001ac5114"
                    },
                    {
                        "id": 192,
                        "inn": 1111111111,
                        "fileName": "NO_BOUPR",
                        "fileType": "AZ",
                        "reportType": 'BFO_TKS',
                        "period": "2020",
                        "uploadDate": "2020-05-22",
                        "token": " 5df1ee2d46e0fb0001ac5125"
                    },
                    {
                        "id": 12,
                        "inn": 1234567878,
                        "fileName": "test10",  # Не подходящее название файла
                        "fileType": "AZ",
                        "reportType": 'BFO_TKS',
                        "period": "2020",
                        "uploadDate": "2020-05-22",
                        "token": " 5df1ee2d46e0fb0001ac5126"
                    }
                ],
                "totalPages": 1,
                "totalElements": 3,
                "sort": "inn: DESC,uploadDate: DESC",
                "page": 0,
                "size": 3
            },
            MockXmlResponse(no_boupr_content, inn=1111111111, kpp=111111111),
            MockXmlResponse(no_buhoth_content, inn=1111111111, kpp=111111111),
        ]

        StatementsLoader().load()
        self.assertEqual(OrgStatement.objects.count(), 1)
        self.assertIsNotNone(OrgStatement.objects.first().statement_file)
        self.assertEqual(PreviousOrgStatement.objects.count(), 2)
        self.assertIsNotNone(PreviousOrgStatement.objects.first().statement_file)
        self.assertIsNotNone(PreviousOrgStatement.objects.last().statement_file)
        self.assertEqual(DifferenceStatement.objects.count(), 2)
        self.assertEqual(FinancialStatementPage.objects.count(), 2)
        self.assertEqual(FinancialStatementFile.objects.count(), 6)
        self.assertEqual(FinancialStatementFile.objects.filter(is_downloaded=True).count(), 4)

    @mock.patch('bfo.services.clients.GirboClient.get')
    @mock.patch('bfo.services.clients.GirboClient.get_access_token_with_cache')
    def test_load_bfo_bn(self, mock_get_access_token_with_cache, mock_get):
        mock_get_access_token_with_cache.return_value = 'f9ea18de-5cc7-42f3-a091-071ee3b1fa80'
        mock_get.return_value = {
            "access_token": "f9ea18de-5cc7-42f3-a091-071ee3b1fa80",
            "token_type": "bearer",
            "scope": "api"
        }

        mock_get.side_effect = [
            {
                "content": [
                    {
                        "id": 2723140,
                        "inn": "1111111111",
                        "fileName": "00002b8731e547c88ee90b3ad102de90-0001.tiff",
                        "fileType": "UNKNOWN",
                        "reportType": "BFO_BN",
                        "period": "2019",
                        "uploadDate": "2020-03-12",
                        "token": "5e6a1ff846e0fb0001ddb520"
                    },
                    {
                        "id": 2723141,
                        "inn": "1111111112",
                        "fileName": "00002b8731e547c88ee90b3ad102de90-0002.tiff",
                        "fileType": "UNKNOWN",
                        "reportType": "BFO_BN",
                        "period": "2019",
                        "uploadDate": "2020-03-12",
                        "token": "5e6a1ff846e0fb0001ddb51e"
                    },
                    {
                        "id": 2723142,
                        "inn": "1111111113",
                        "fileName": "00002b8731e547c88ee90b3ad102de90-0003.tiff",
                        "fileType": "UNKNOWN",
                        "reportType": "BFO_BN",
                        "period": "2019",
                        "uploadDate": "2020-03-12",
                        "token": "5e6a1ff846e0fb0001ddb51c"
                    },
                ],
                "totalPages": 1,
                "totalElements": 3,
                "sort": "fileName: ASC",
                "page": 0,
                "size": 3
            },
            {
                "content": [
                    {
                        "id": 2723140,
                        "inn": "1111111111",
                        "fileName": "00002b8731e547c88ee90b3ad102de90-0001.tiff",
                        "fileType": "UNKNOWN",
                        "reportType": "BFO_BN",
                        "period": "2020",
                        "uploadDate": "2020-03-12",
                        "token": "5e6a1ff846e0fb0001ddb520"
                    },
                    {
                        "id": 2723141,
                        "inn": "1111111112",
                        "fileName": "00002b8731e547c88ee90b3ad102de90-0002.tiff",
                        "fileType": "UNKNOWN",
                        "reportType": "BFO_BN",
                        "period": "2020",
                        "uploadDate": "2020-03-12",
                        "token": "5e6a1ff846e0fb0001ddb51e"
                    },
                    {
                        "id": 2723142,
                        "inn": "1111111113",
                        "fileName": "00002b8731e547c88ee90b3ad102de90-0003.tiff",
                        "fileType": "UNKNOWN",
                        "reportType": "BFO_BN",
                        "period": "2020",
                        "uploadDate": "2020-03-12",
                        "token": "5e6a1ff846e0fb0001ddb51c"
                    },
                ],
                "totalPages": 1,
                "totalElements": 3,
                "sort": "fileName: ASC",
                "page": 0,
                "size": 3
            },
        ]

        StatementsLoader().load()
        self.assertEqual(TemporaryINN.objects.count(), 3)
        self.assertIsNotNone(TemporaryINN.objects.first().statement_file)
        self.assertEqual(FinancialStatementPage.objects.count(), 2)
        self.assertEqual(FinancialStatementFile.objects.count(), 3)
        self.assertEqual(FinancialStatementFile.objects.filter(is_downloaded=True).count(), 3)

    @mock.patch('bfo.services.clients.GirboClient.get')
    @mock.patch('bfo.services.clients.GirboClient.get_access_token_with_cache')
    def test_load_bfo_cb_str(self, mock_get_access_token_with_cache, mock_get):
        mock_get_access_token_with_cache.return_value = 'f9ea18de-5cc7-42f3-a091-071ee3b1fa80'
        mock_get.return_value = {
            "access_token": "f9ea18de-5cc7-42f3-a091-071ee3b1fa80",
            "token_type": "bearer",
            "scope": "api"
        }

        mock_get.side_effect = [
            {
                "content": [
                    {
                        "id": 8572650,
                        "inn": "1111111111",
                        "fileName": "0409806_1_F806_20200101_20210120.CSV",
                        "fileType": "BFO",
                        "reportType": "BFO_CB_STR",
                        "period": "2019",
                        "uploadDate": "2021-01-22",
                        "token": "600a994846e0fb0001cb881e"
                    },
                    {
                        "id": 8570817,
                        "inn": "1111111112",
                        "fileName": "0409806_1000_F806_20200101_20210120.CSV",
                        "fileType": "BFO",
                        "reportType": "BFO_CB_STR",
                        "period": "2019",
                        "uploadDate": "2021-01-22",
                        "token": "600a8b1f46e0fb0001cb76d5"
                    },
                    {
                        "id": 8566783,
                        "inn": "1111111113",
                        "fileName": "0409806_101_F806_20200101_20210120.CSV",
                        "fileType": "BFO",
                        "reportType": "BFO_CB_STR",
                        "period": "2019",
                        "uploadDate": "2021-01-22",
                        "token": "600a6a7d46e0fb0001cb4f7c"
                    },
                ],
                "totalPages": 1,
                "totalElements": 3,
                "sort": "fileName: ASC",
                "page": 0,
                "size": 3
            },
            {
                "content": [
                    {
                        "id": 8572650,
                        "inn": "1111111111",
                        "fileName": "0409806_1_F806_20200101_20210120.CSV",
                        "fileType": "BFO",
                        "reportType": "BFO_CB_STR",
                        "period": "2020",
                        "uploadDate": "2021-01-22",
                        "token": "600a994846e0fb0001cb881e"
                    },
                    {
                        "id": 8570817,
                        "inn": "1111111112",
                        "fileName": "0409806_1000_F806_20200101_20210120.CSV",
                        "fileType": "BFO",
                        "reportType": "BFO_CB_STR",
                        "period": "2020",
                        "uploadDate": "2021-01-22",
                        "token": "600a8b1f46e0fb0001cb76d5"
                    },
                    {
                        "id": 8566783,
                        "inn": "1111111113",
                        "fileName": "0409806_101_F806_20200101_20210120.CSV",
                        "fileType": "BFO",
                        "reportType": "BFO_CB_STR",
                        "period": "2020",
                        "uploadDate": "2021-01-22",
                        "token": "600a6a7d46e0fb0001cb4f7c"
                    },
                ],
                "totalPages": 1,
                "totalElements": 3,
                "sort": "fileName: ASC",
                "page": 0,
                "size": 3
            },
        ]

        StatementsLoader().load()
        self.assertEqual(FinancialStatementPage.objects.count(), 2)
        self.assertEqual(FinancialStatementFile.objects.count(), 3)
        self.assertEqual(FinancialStatementFile.objects.filter(is_downloaded=True).count(), 0)

    @mock.patch('bfo.services.clients.GirboClient.get')
    @mock.patch('bfo.services.clients.GirboClient.get_access_token_with_cache')
    def test_load_bfo_cb_nstr(self, mock_get_access_token_with_cache, mock_get):
        mock_get_access_token_with_cache.return_value = 'f9ea18de-5cc7-42f3-a091-071ee3b1fa80'
        mock_get.return_value = {
            "access_token": "f9ea18de-5cc7-42f3-a091-071ee3b1fa80",
            "token_type": "bearer",
            "scope": "api"
        }

        mock_get.side_effect = [
            {
                "content": [
                    {
                        "id": 8148802,
                        "inn": "1111111111",
                        "fileName": " Бухгалтерская отчетность (Январь - Декабрь 2019 г.). "
                                    "Бухгал_7722719157_20191231_20200928_1.xls",
                        "fileType": "UNKNOWN",
                        "reportType": "BFO_CB_NSTR",
                        "period": "2019",
                        "uploadDate": "2020-11-18",
                        "token": "5fb5aa0946e0fb000121ffb8"
                    },
                    {
                        "id": 8148805,
                        "inn": "1111111112",
                        "fileName": " Бухгалтерская отчетность (Январь - Декабрь 2019 г.). "
                                    "Бухгал_7722719157_20191231_20200928_4.xls",
                        "fileType": "UNKNOWN",
                        "reportType": "BFO_CB_NSTR",
                        "period": "2019",
                        "uploadDate": "2020-11-18",
                        "token": "5fb5aa0946e0fb000121ff7f"
                    },
                    {
                        "id": 8148930,
                        "inn": "1111111113",
                        "fileName": " Бухгалтерская отчетность (Январь - Декабрь 2019 г.). "
                                    "Бухгал_7734725613_20191231_20200928_1.xls",
                        "fileType": "UNKNOWN",
                        "reportType": "BFO_CB_NSTR",
                        "period": "2019",
                        "uploadDate": "2020-11-18",
                        "token": "5fb5aa2846e0fb0001220208"
                    },
                ],
                "totalPages": 1,
                "totalElements": 3,
                "sort": "fileName: ASC",
                "page": 0,
                "size": 3
            },
            {
                "content": [
                    {
                        "id": 8148802,
                        "inn": "1111111111",
                        "fileName": " Бухгалтерская отчетность (Январь - Декабрь 2019 г.). "
                                    "Бухгал_7722719157_20191231_20200928_1.xls",
                        "fileType": "UNKNOWN",
                        "reportType": "BFO_CB_NSTR",
                        "period": "2019",
                        "uploadDate": "2020-11-18",
                        "token": "5fb5aa0946e0fb000121ffb8"
                    },
                    {
                        "id": 8148805,
                        "inn": "1111111112",
                        "fileName": " Бухгалтерская отчетность (Январь - Декабрь 2019 г.). "
                                    "Бухгал_7722719157_20191231_20200928_4.xls",
                        "fileType": "UNKNOWN",
                        "reportType": "BFO_CB_NSTR",
                        "period": "2019",
                        "uploadDate": "2020-11-18",
                        "token": "5fb5aa0946e0fb000121ff7f"
                    },
                    {
                        "id": 8148930,
                        "inn": "1111111113",
                        "fileName": " Бухгалтерская отчетность (Январь - Декабрь 2019 г.). "
                                    "Бухгал_7734725613_20191231_20200928_1.xls",
                        "fileType": "UNKNOWN",
                        "reportType": "BFO_CB_NSTR",
                        "period": "2019",
                        "uploadDate": "2020-11-18",
                        "token": "5fb5aa2846e0fb0001220208"
                    },
                ],
                "totalPages": 1,
                "totalElements": 3,
                "sort": "fileName: ASC",
                "page": 0,
                "size": 3
            },
        ]

        StatementsLoader().load()
        self.assertEqual(FinancialStatementPage.objects.count(), 2)
        self.assertEqual(FinancialStatementFile.objects.count(), 3)
        self.assertEqual(FinancialStatementFile.objects.filter(is_downloaded=True).count(), 0)
