import datetime
from collections import OrderedDict

from asgiref.sync import sync_to_async

from bfo.models import OrgStatement
from .statements_transformer import StatementsTransformer


class StatementInterface:
    @staticmethod
    async def get_fin_statement(inn, years, compatibility=True, post_transform=False):
        years = list(map(lambda x: datetime.date(int(x), 12, 31), years))
        statement_qs = OrgStatement.objects.filter(
            inn=inn,
            report_date__in=years,
        )
        fin_statement = OrderedDict([
            ('inn', inn),
            ('kpp', None),
            ('buhForms', []),
        ])

        if not await sync_to_async(statement_qs.exists, thread_sensitive=True)():
            return fin_statement
        for year in years:
            statement = await sync_to_async(statement_qs.filter(report_date=year).last, thread_sensitive=True)()
            if not statement:
                continue
            fin_statement['kpp'] = statement.kpp
            if not compatibility:
                fin_statement['buhForms'].append(statement.data_from_src)
                continue
            statements_transformer = await StatementsTransformer.create()
            compatible_values = await statements_transformer.transform(
                statement=statement,
                post_transform=post_transform,
            )

            fin_statement['buhForms'].append(compatible_values)
        return fin_statement
