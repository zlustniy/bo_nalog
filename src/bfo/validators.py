import re
from gettext import gettext

from django.forms import ValidationError


def is_valid_inn(inn):
    """функция проверяет корректность ИНН
    (длина, набор символов, контрольная сумма)
    :param inn: строка с ИНН (10 или 12 символов)
    :type inn: str or unicode
    :returns: True если ИНН корректный
    :rtype: bool

    https://www.creator.su/2015/07/is_valid_inn/
    """
    a = re.match(u"^0(.)\\1{8,}$", inn)
    if a is not None:
        return False
    multiplier = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
    try:
        inn = [int(i) for i in inn]
    except ValueError:
        return False

    def checksum(digit):
        _inn = [0] * (12 - digit) + inn
        s = sum([multiplier[i] * _inn[i] for i in range(11)])
        return _inn[11] == s % 11 % 10

    if len(inn) == 12:
        return checksum(11) and checksum(12)
    elif len(inn) == 10:
        return checksum(10)
    return False


def validate_inn(val):
    if not is_valid_inn(str(val)):
        raise ValidationError(gettext('Некорректное значение ИНН'))


def is_valid_ogrn(ogrn):
    len_ogrn = len(ogrn)
    if len_ogrn not in (13, 15):
        return False

    def ogrn_csum(ogrn):
        if len_ogrn == 13:
            delimeter = 11
        else:
            delimeter = 13
        return str(int(ogrn[:-1]) % delimeter % 10)

    return ogrn_csum(ogrn) == ogrn[-1]


def validate_ogrn(val):
    if not is_valid_ogrn(str(val)):
        raise ValidationError(gettext('Некорректное значение ogrn'))
