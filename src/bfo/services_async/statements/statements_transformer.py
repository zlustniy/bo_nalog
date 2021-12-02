import json
import operator
from collections import OrderedDict, defaultdict
from dataclasses import dataclass
from functools import reduce

from asgiref.sync import sync_to_async
from django.core import serializers

from bfo.models import StatementDictionary
from bfo.services_async.statements.statements_post_transformers import PostTransform


@dataclass
class StatementDictionaryItem:
    pk: int
    code: str
    title: str
    ext_name: str
    form: str
    parent: 'StatementDictionaryItem'

    def __post_init__(self):
        self.form = f'form{self.form}'

    @property
    def parent_chain(self):
        chain = []
        parent = self.parent
        while True:
            if parent is None:
                break
            chain.append(parent.ext_name)
            parent = getattr(parent, 'parent', None)
        chain.reverse()
        return chain


class StatementsTransformer:
    def __init__(self):
        self.statement_dictionary = None

    @classmethod
    async def create(cls):
        self = StatementsTransformer()
        statement_dictionary = await sync_to_async(
            StatementDictionary.objects.all().order_by,
            thread_sensitive=True,
        )('id')
        statement_dictionary_serialized = await sync_to_async(serializers.serialize, thread_sensitive=True)(
            format='json',
            queryset=statement_dictionary,
        )
        self.statement_dictionary = json.loads(statement_dictionary_serialized)
        return self

    def get_statement_dictionary_by_pk(self, pk):
        return next(filter(lambda x: x['pk'] == pk, self.statement_dictionary), None)

    def get_statements_dictionary_filter_by_ext_name(self, ext_name):
        return filter(lambda x: x['fields']['ext_name'] == ext_name, self.statement_dictionary)

    def get_statement_dictionary_item_by_pk(self, pk):
        statement_dictionary = self.get_statement_dictionary_by_pk(pk)
        if statement_dictionary is None:
            return None
        return StatementDictionaryItem(
            pk=statement_dictionary['pk'],
            code=statement_dictionary['fields']['code'],
            form=statement_dictionary['fields']['form'],
            title=statement_dictionary['fields']['title'],
            ext_name=statement_dictionary['fields']['ext_name'],
            parent=self.get_statement_dictionary_item_by_pk(
                statement_dictionary['fields']['parent'],
            ),
        )

    def get_statement_dictionary(self, ext_name, chain_of_parents):
        parents = chain_of_parents[:-1]

        statement_dictionary_item = None
        statements_dictionary_filter = self.get_statements_dictionary_filter_by_ext_name(ext_name)
        for statement_dictionary in statements_dictionary_filter:
            statement_dictionary_item = self.get_statement_dictionary_item_by_pk(statement_dictionary['pk'])
            if statement_dictionary_item.parent_chain == parents:
                break
        return statement_dictionary_item

    async def recursive_dictionary_walk_find_finances_section(
            self,
            must_contain_element: tuple,
            dictionary: dict,
            chain_of_parents: list,
    ):
        must_contain_element_key, must_contain_element_value = must_contain_element
        for key, value in dictionary.items():
            if isinstance(value, dict):
                copy_chain_of_parents = list(chain_of_parents)
                copy_chain_of_parents.append(key)
                finances_section_path = await self.recursive_dictionary_walk_find_finances_section(
                    must_contain_element=must_contain_element,
                    dictionary=value,
                    chain_of_parents=copy_chain_of_parents,
                )
                if finances_section_path is not None:
                    return finances_section_path
            if all([
                key == must_contain_element_key,
                value == must_contain_element_value,
            ]):
                return chain_of_parents

    async def recursive_finances_section_walk(self, transformed_statement, dictionary, chain_of_parents):
        if chain_of_parents:
            parent_ext_name = chain_of_parents[-1]
            statement_dictionary = self.get_statement_dictionary(
                parent_ext_name,
                chain_of_parents,
            )
            if statement_dictionary:
                start_value = dictionary.get('@СумПрдщ') or dictionary.get('@СумПред') or 0
                end_value = dictionary.get('@СумОтч') or 0
                transformed_statement[statement_dictionary.form].append({
                    'code': statement_dictionary.code,
                    'name': statement_dictionary.title,
                    'startValue': int(start_value),
                    'endValue': int(end_value),
                })

        for key, value in dictionary.items():
            if isinstance(value, dict):
                copy_chain_of_parents = list(chain_of_parents)
                copy_chain_of_parents.append(key)
                await self.recursive_finances_section_walk(transformed_statement, value, copy_chain_of_parents)

    async def transform(self, statement, post_transform=True):
        data_from_src = statement.data_from_src
        year = statement.report_date.year
        compatible_values = OrderedDict([
            ('year', year),
            ('knd', data_from_src['Файл']['Документ']['@КНД']),
        ])

        # Ищем все вложенные словари, у которых есть значения, указанные в `must_contain_element`
        finances_section_paths = []
        for must_contain_element in [
            ('@ОКУД', '0710001'),
            ('@ОКУД', '0710002'),
        ]:
            section_path = await self.recursive_dictionary_walk_find_finances_section(
                must_contain_element=must_contain_element,
                dictionary=data_from_src,
                chain_of_parents=[],
            )
            if isinstance(section_path, list):
                finances_section_paths.append(section_path)

        # Ищем финансовые показатели в найденных вложенных словарях
        transformed_statement = defaultdict(list)
        for section_path in finances_section_paths:
            dictionary = reduce(operator.getitem, section_path, data_from_src)
            await self.recursive_finances_section_walk(transformed_statement, dictionary, chain_of_parents=[])

        compatible_values.update(transformed_statement)
        if post_transform:
            compatible_values = await self.post_transform(compatible_values=compatible_values)
        for form_name, form_values in compatible_values.items():
            if form_name not in ['form1', 'form2']:
                continue
            form_values = sorted(form_values, key=lambda k: (k['code'], k['name']))
            compatible_values[form_name] = form_values
        return compatible_values

    @staticmethod
    async def post_transform(compatible_values):
        post_transform = await PostTransform().post_transform(
            compatible_values=compatible_values,
        )
        return post_transform
