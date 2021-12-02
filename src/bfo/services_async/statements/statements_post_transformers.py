from abc import ABC, abstractmethod
from dataclasses import dataclass
from operator import itemgetter
from typing import List

from asgiref.sync import sync_to_async

from bfo.models import StatementDictionary


@dataclass
class StatementValue:
    code: str
    start_value: int
    end_value: int


def index_by_code(code, compatible_values, form):
    try:
        return list(map(itemgetter('code'), compatible_values[form])).index(code)
    except (KeyError, ValueError):
        return None


class CompatibleValuesManager:
    def __init__(self, compatible_values, form='form2'):
        self.compatible_values = compatible_values
        self.form = form

    async def get_value(self, code, key):
        index = index_by_code(code=code, compatible_values=self.compatible_values, form=self.form)
        if index is None:
            return 0
        return self.compatible_values[self.form][index][key]

    async def get_start_end_values(self, code):
        return StatementValue(
            code=code,
            start_value=await self.get_value(code=code, key='startValue'),
            end_value=await self.get_value(code=code, key='endValue'),
        )

    @staticmethod
    @sync_to_async
    def get_statement_dictionary(code):
        return StatementDictionary.objects.filter(code=code).first()

    async def calculate_missing_codes(self):
        existing_2410 = await self.get_start_end_values(code='2410')
        existing_2430 = await self.get_start_end_values(code='2430')
        existing_2450 = await self.get_start_end_values(code='2450')

        recalculated_value_2410 = StatementValue(
            code='2410',
            start_value=(existing_2410.start_value * -1) + existing_2430.start_value + existing_2450.start_value,
            end_value=(existing_2410.end_value * -1) + existing_2430.end_value + existing_2450.end_value,
        )
        recalculated_value_2411 = StatementValue(
            code='2411',
            start_value=(existing_2410.start_value * -1),
            end_value=(existing_2410.end_value * -1),
        )
        recalculated_value_2412 = StatementValue(
            code='2412',
            start_value=existing_2430.start_value + existing_2450.start_value,
            end_value=existing_2430.end_value + existing_2450.end_value,
        )
        await self.update_values(
            recalculated_values=[recalculated_value_2410, recalculated_value_2411, recalculated_value_2412],
        )
        return self.compatible_values

    async def update_values(self, recalculated_values: List[StatementValue]):
        for recalculated_value in recalculated_values:
            index = index_by_code(
                code=recalculated_value.code,
                compatible_values=self.compatible_values,
                form=self.form,
            )
            if index is None:
                await self.create_value(statement_value=recalculated_value)
            else:
                await self.update_value(statement_value=recalculated_value, index=index)

    async def create_value(self, statement_value: StatementValue):
        statement_dictionary = await self.get_statement_dictionary(code=statement_value.code)
        self.compatible_values[self.form].append({
            'code': statement_dictionary.code,
            'name': statement_dictionary.title,
            'startValue': statement_value.start_value,
            'endValue': statement_value.end_value,
        })

    async def update_value(self, statement_value: StatementValue, index: int):
        self.compatible_values[self.form][index].update({
            'startValue': statement_value.start_value,
            'endValue': statement_value.end_value,
        })


class PostTransform:
    @staticmethod
    async def get_post_transform_strategy(knd_code):
        strategy_map = {
            '0710099': PostTransformCommon,
            '0710096': PostTransformSimplified,
        }
        return strategy_map[knd_code]

    @staticmethod
    async def calculate_missing_codes(compatible_values):
        compatible_values_manager = CompatibleValuesManager(
            compatible_values=compatible_values,
        )
        calculated_missing_codes = await compatible_values_manager.calculate_missing_codes()
        return calculated_missing_codes

    @staticmethod
    async def is_special_financial_statements(compatible_values):
        form2_values = compatible_values.get('form2', [])
        if not form2_values:
            return False

        any_code_exists = ['2421', '2430', '2450']
        codes_do_not_exist = ['2411', '2412']
        return all([
            bool([value for value in form2_values if value['code'] in any_code_exists]),
            not bool([value for value in form2_values if value['code'] in codes_do_not_exist]),
        ])

    async def post_transform(self, compatible_values):
        if await self.is_special_financial_statements(compatible_values=compatible_values):
            compatible_values = await self.calculate_missing_codes(compatible_values=compatible_values)
        post_transform_strategy = await self.get_post_transform_strategy(knd_code=compatible_values['knd'])
        return await post_transform_strategy().post_transform(
            compatible_values=compatible_values,
        )


class PostTransformBase(ABC):
    @abstractmethod
    async def post_transform(self, compatible_values):
        pass

    @staticmethod
    async def change_sign(compatible_values, codes):
        for form_name, codes in codes.items():
            for code in codes:
                index = index_by_code(
                    code=code,
                    compatible_values=compatible_values,
                    form=form_name,
                )
                if index is None:
                    continue

                compatible_values[form_name][index]['startValue'] *= -1
                compatible_values[form_name][index]['endValue'] *= -1
        return compatible_values


class PostTransformCommon(PostTransformBase):
    async def post_transform(self, compatible_values):
        compatible_values = await self.change_sign(
            compatible_values=compatible_values,
            codes={
                'form1': ['1320'],
                'form2': ['2120', '2210', '2220', '2330', '2350', '2411'],
            }
        )
        return compatible_values


class PostTransformSimplified(PostTransformBase):
    async def post_transform(self, compatible_values):
        compatible_values = await self.change_sign(
            compatible_values=compatible_values,
            codes={
                'form2': ['2120', '2330', '2350', '2410'],
            }
        )
        return compatible_values
