from rest_framework import serializers

from .fields import YearField
from .validators import (
    validate_inn,
    validate_ogrn,
)


class YearsListSerialiser(serializers.ListSerializer):
    def get_value(self, dictionary):
        years = dictionary.get('years', [])
        if years:
            years = years.split(',') if isinstance(years, str) else years
        else:
            years = dictionary.getlist('year', [])
        return years


class ParamFinStatementsSerializer(serializers.Serializer):
    inn = serializers.CharField(
        min_length=10,
        max_length=10,
        validators=[validate_inn],
    )
    years = YearsListSerialiser(
        child=YearField(),
        allow_empty=False,
    )
    compatibility = serializers.BooleanField(
        default=True,
    )
    post_transform = serializers.BooleanField(
        default=True,
    )


class ParamFinReportSerializer(serializers.Serializer):
    ogrn = serializers.CharField(
        min_length=13,
        max_length=15,
        validators=[validate_ogrn],
    )
    year = YearField()
