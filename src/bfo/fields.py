from rest_framework import serializers


class YearField(serializers.IntegerField):
    def __init__(self, **kwargs):
        kwargs['min_value'] = kwargs.get('min_value', 2000)
        kwargs['max_value'] = kwargs.get('max_value', 3000)
        super().__init__(**kwargs)
