# Generated by Django 2.2.19 on 2021-04-06 13:12

from django.db import migrations


def forward_insert_statement_form(apps, schema_editor):
    StatementForm = apps.get_model('bfo', 'StatementForm')
    StatementForm.objects.create(
        form_name='Форма № 1',
    )
    StatementForm.objects.create(
        form_name='Форма № 2',
    )


def backward_insert_statement_form(apps, schema_editor):
    StatementForm = apps.get_model('bfo', 'StatementForm')
    StatementForm.objects.filter(
        id__in=[1, 2],
    ).delete()


def forward_insert_statement_dictionary(apps, schema_editor):
    StatementDictionary = apps.get_model('bfo', 'StatementDictionary')
    StatementDictionary.objects.bulk_create([
        StatementDictionary(title='Нематериальные активы', form_id=1, code=1110, ext_name='НематАкт'),
        StatementDictionary(title='Результаты исследований и разработок', form_id=1, code=1120, ext_name='РезИсслед'),
        StatementDictionary(title='Нематериальные поисковые активы', form_id=1, code=1130, ext_name='НеМатПоискАкт'),
        StatementDictionary(title='Материальные поисковые активы', form_id=1, code=1140, ext_name='МатПоискАкт'),
        StatementDictionary(title='Основные средства', form_id=1, code=1150, ext_name='ОснСр'),
        StatementDictionary(
            title='Доходные вложения в материальные ценности',
            form_id=1,
            code=1160,
            ext_name='ВлМатЦен',
        ),
        StatementDictionary(title='Финансовые вложения', form_id=1, code=1170, ext_name='ФинВлож'),
        StatementDictionary(title='Отложенные налоговые активы', form_id=1, code=1180, ext_name='ОтлНалАкт'),
        StatementDictionary(title='Прочие внеоборотные активы', form_id=1, code=1190, ext_name='ПрочВнеОбА'),
        StatementDictionary(title='Итого по разделу I', form_id=1, code=1100, ext_name='ВнеОбА'),
        StatementDictionary(title='Запасы', form_id=1, code=1210, ext_name='Запасы'),
        StatementDictionary(
            title='Налог на добавленную стоимость по приобретенным ценностям',
            form_id=1,
            code=1220,
            ext_name='НДСПриобрЦен',
        ),
        StatementDictionary(title='Дебиторская задолженность', form_id=1, code=1230, ext_name='ДебЗад'),
        StatementDictionary(
            title='Финансовые вложения (за исключением денежных эквивалентов)',
            form_id=1,
            code=1240,
            ext_name='ФинВлож',
        ),
        StatementDictionary(
            title='Денежные средства и денежные эквиваленты',
            form_id=1,
            code=1250,
            ext_name='ДенежнСр',
        ),
        StatementDictionary(title='Прочие оборотные активы', form_id=1, code=1260, ext_name='ПрочОбА'),
        StatementDictionary(title='Итого по разделу II', form_id=1, code=1200, ext_name='ОбА'),
        StatementDictionary(title='БАЛАНС', form_id=1, code=1600, ext_name='Актив'),
        StatementDictionary(
            title='Уставный капитал (складочный капитал, уставный фонд, вклады товарищей)',
            form_id=1,
            code=1310,
            ext_name='УставКапитал',
        ),
        StatementDictionary(
            title='Собственные акции, выкупленные у акционеров',
            form_id=1,
            code=1320,
            ext_name='СобствАкции',
        ),
        StatementDictionary(title='Переоценка внеоборотных активов', form_id=1, code=1340, ext_name='ПереоцВнеОбА'),
        StatementDictionary(title='Добавочный капитал (без переоценки)', form_id=1, code=1350, ext_name='ДобКапитал'),
        StatementDictionary(title='Резервный капитал', form_id=1, code=1360, ext_name='РезКапитал'),
        StatementDictionary(
            title='Нераспределенная прибыль (непокрытый убыток)',
            form_id=1,
            code=1370,
            ext_name='НераспПриб',
        ),
        StatementDictionary(title='Итого по разделу III', form_id=1, code=1300, ext_name='КапРез'),

        StatementDictionary(title='Паевой фонд', form_id=1, code=1310, ext_name='ПайФонд'),
        StatementDictionary(title='Целевой капитал', form_id=1, code=1320, ext_name='ЦелевКапитал'),
        StatementDictionary(title='Целевые средства', form_id=1, code=1350, ext_name='ЦелевСредства'),
        StatementDictionary(
            title='Фонд недвижимого и особо ценного движимого имущества',
            form_id=1,
            code=1360,
            ext_name='ФондИмущ',
        ),
        StatementDictionary(title='Резервный и иные целевые фонды', form_id=1, code=1370, ext_name='РезервИнЦФ'),
        StatementDictionary(title='Итого по разделу III', form_id=1, code=1300, ext_name='ЦелевФин'),

        StatementDictionary(title='Заемные средства', form_id=1, code=1410, ext_name='ЗаемСредств'),
        StatementDictionary(title='Отложенные налоговые обязательства', form_id=1, code=1420, ext_name='ОтложНалОбяз'),
        StatementDictionary(title='Оценочные обязательства', form_id=1, code=1430, ext_name='ОценОбяз'),
        StatementDictionary(title='Прочие обязательства', form_id=1, code=1450, ext_name='ПрочОбяз'),
        StatementDictionary(title='Итого по разделу IV', form_id=1, code=1400, ext_name='ДолгосрОбяз'),
        StatementDictionary(title='Заемные средства', form_id=1, code=1510, ext_name='ЗаемСредств'),
        StatementDictionary(title='Кредиторская задолженность', form_id=1, code=1520, ext_name='КредитЗадолж'),
        StatementDictionary(title='Доходы будущих периодов', form_id=1, code=1530, ext_name='ДоходБудущ'),
        StatementDictionary(title='Оценочные обязательства', form_id=1, code=1540, ext_name='ОценОбяз'),
        StatementDictionary(title='Прочие обязательства', form_id=1, code=1550, ext_name='ПрочОбяз'),
        StatementDictionary(title='Итого по разделу V', form_id=1, code=1500, ext_name='КраткосрОбяз'),
        StatementDictionary(title='БАЛАНС', form_id=1, code=1700, ext_name='Пассив'),

        StatementDictionary(
            title='Выручка за минусом налога на добавленную стоимость, акцизов',
            form_id=2,
            code=2110,
            ext_name='Выруч',
        ),
        StatementDictionary(title='Себестоимость продаж', form_id=2, code=2120, ext_name='СебестПрод'),
        StatementDictionary(title='Валовая прибыль (убыток)', form_id=2, code=2100, ext_name='ВаловаяПрибыль'),
        StatementDictionary(title='Коммерческие расходы', form_id=2, code=2210, ext_name='КомРасход'),
        StatementDictionary(title='Управленческие расходы', form_id=2, code=2220, ext_name='УпрРасход'),
        StatementDictionary(title='Прибыль (убыток) от продаж', form_id=2, code=2200, ext_name='ПрибПрод'),
        StatementDictionary(
            title='Доходы от участия в других организациях',
            form_id=2,
            code=2310,
            ext_name='ДоходОтУчаст',
        ),
        StatementDictionary(title='Проценты к получению', form_id=2, code=2320, ext_name='ПроцПолуч'),
        StatementDictionary(title='Проценты к уплате', form_id=2, code=2330, ext_name='ПроцУпл'),
        StatementDictionary(title='Прочие доходы', form_id=2, code=2340, ext_name='ПрочДоход'),
        StatementDictionary(title='Прочие расходы', form_id=2, code=2350, ext_name='ПрочРасход'),
        StatementDictionary(title='Прибыль (убыток) до налогообложения', form_id=2, code=2300, ext_name='ПрибУбДоНал'),
        StatementDictionary(title='Налог на прибыль', form_id=2, code=2410, ext_name='НалПриб'),
        StatementDictionary(title='Текущий налог на прибыль', form_id=2, code=2411, ext_name='ТекНалПриб'),
        StatementDictionary(title='Отложенный налог на прибыль', form_id=2, code=2412, ext_name='ОтложНалПриб'),
        StatementDictionary(
            title='Налог на прибыль от операций, результат которых не включается в чистую прибыль (убыток) периода',
            form_id=2,
            code=2530,
            ext_name='НалПрибОпНеЧист',
        ),

        StatementDictionary(
            title='в т.ч. постоянные налоговые обязательства (активы)',
            form_id=2,
            code=2421,
            ext_name='ПостНалОбяз',
        ),
        StatementDictionary(
            title='Изменение отложенных налоговых обязательств',
            form_id=2,
            code=2430,
            ext_name='ИзмНалОбяз',
        ),
        StatementDictionary(
            title='Изменение отложенных налоговых активов',
            form_id=2,
            code=2450,
            ext_name='ИзмНалАктив',
        ),
        StatementDictionary(title='Прочее', form_id=2, code=2460, ext_name='Прочее'),
        StatementDictionary(title='Чистая прибыль (убыток)', form_id=2, code=2400, ext_name='ЧистПрибУб'),
        StatementDictionary(
            title='Результат от переоценки внеоборотных активов, не включаемый в чистую прибыль (убыток) периода',
            form_id=2,
            code=2510,
            ext_name='РезПрцВОАНеЧист',
        ),
        StatementDictionary(
            title='Результат от прочих операций, не включаемый в чистую прибыль (убыток) периода',
            form_id=2,
            code=2520,
            ext_name='РезПрОпНеЧист',
        ),
        StatementDictionary(
            title='Совокупный финансовый результат периода',
            form_id=2,
            code=2500,
            ext_name='СовФинРез',
        ),
        StatementDictionary(title='Базовая прибыль (убыток) на акцию', form_id=2, code=2900, ext_name='БазПрибылАкц'),
        StatementDictionary(
            title='Разводненная прибыль (убыток) на акцию',
            form_id=2,
            code=2910,
            ext_name='РазводПрибылАкц',
        ),
        StatementDictionary(title='Материальные внеоборотные активы ', form_id=1, code=1150, ext_name='МатВнеАкт'),
        StatementDictionary(
            title='Нематериальные, финансовые и другие внеоборотные активы',
            form_id=1,
            code=1170,
            ext_name='НеМатФинАкт',
        ),
        StatementDictionary(title='Запасы', form_id=1, code=1210, ext_name='Запасы'),
        StatementDictionary(
            title='Денежные средства и денежные эквиваленты',
            form_id=1,
            code=1250,
            ext_name='ДенежнСр',
        ),
        StatementDictionary(title='Финансовые и другие оборотные активы', form_id=1, code=1230, ext_name='ФинВлож'),
        StatementDictionary(title='Капитал и резервы', form_id=1, code=1300, ext_name='КапРез'),
        StatementDictionary(title='Целевые средства', form_id=1, code=1300, ext_name='ЦелевСредства'),
        StatementDictionary(
            title='Фонд недвижимого и особо ценного движимого имущества и иные целевые фонды',
            form_id=1,
            code=1300,
            ext_name='ФондИмущИнЦФ',
        ),
        StatementDictionary(title='Долгосрочные заемные средства', form_id=1, code=1410, ext_name='ДлгЗаемСредств'),
        StatementDictionary(title='Другие долгосрочные обязательства', form_id=1, code=1450, ext_name='ДрДолгосрОбяз'),
        StatementDictionary(title='Краткосрочные заемные средства', form_id=1, code=1510, ext_name='КртЗаемСредств'),
        StatementDictionary(title='Кредиторская задолженность', form_id=1, code=1520, ext_name='КредитЗадолж'),
        StatementDictionary(
            title='Другие краткосрочные обязательства',
            form_id=1,
            code=1550,
            ext_name='ДрКраткосрОбяз',
        ),
        StatementDictionary(title='Расходы по обычной деятельности', form_id=2, code=2120, ext_name='РасхОбДеят'),
        StatementDictionary(title='Налоги на прибыль (доходы)', form_id=2, code=2410, ext_name='НалПрибДох'),
    ])


def backward_insert_statement_dictionary(apps, schema_editor):
    StatementDictionary = apps.get_model('bfo', 'StatementDictionary')
    StatementDictionary.objects.filter(
        code__in=[
            1110,
            1120,
            1130,
            1140,
            1150,
            1160,
            1170,
            1180,
            1190,
            1100,
            1210,
            1220,
            1230,
            1240,
            1250,
            1260,
            1200,
            1600,
            1310,
            1320,
            1340,
            1350,
            1360,
            1370,
            1300,
            1410,
            1420,
            1430,
            1450,
            1400,
            1510,
            1520,
            1530,
            1540,
            1550,
            1500,
            1700,
            2110,
            2120,
            2100,
            2210,
            2220,
            2200,
            2310,
            2320,
            2330,
            2340,
            2350,
            2300,
            2410,
            2421,
            2430,
            2450,
            2460,
            2400,
            2510,
            2520,
            2500,
            2900,
            2910,
            2410,
            2411,
            2412,
            2530,
        ]
    ).delete()


def forward_set_parent_statement_dictionary(apps, schema_editor):
    StatementDictionary = apps.get_model('bfo', 'StatementDictionary')
    StatementDictionary.objects.filter(id=1).update(parent_id=10)
    StatementDictionary.objects.filter(id=2).update(parent_id=10)
    StatementDictionary.objects.filter(id=3).update(parent_id=10)
    StatementDictionary.objects.filter(id=4).update(parent_id=10)
    StatementDictionary.objects.filter(id=5).update(parent_id=10)
    StatementDictionary.objects.filter(id=6).update(parent_id=10)
    StatementDictionary.objects.filter(id=7).update(parent_id=10)
    StatementDictionary.objects.filter(id=8).update(parent_id=10)
    StatementDictionary.objects.filter(id=9).update(parent_id=10)
    StatementDictionary.objects.filter(id=10).update(parent_id=18)
    StatementDictionary.objects.filter(id=11).update(parent_id=17)
    StatementDictionary.objects.filter(id=12).update(parent_id=17)
    StatementDictionary.objects.filter(id=13).update(parent_id=17)
    StatementDictionary.objects.filter(id=14).update(parent_id=17)
    StatementDictionary.objects.filter(id=15).update(parent_id=17)
    StatementDictionary.objects.filter(id=16).update(parent_id=17)
    StatementDictionary.objects.filter(id=17).update(parent_id=18)
    StatementDictionary.objects.filter(id=19).update(parent_id=25)
    StatementDictionary.objects.filter(id=20).update(parent_id=25)
    StatementDictionary.objects.filter(id=21).update(parent_id=25)
    StatementDictionary.objects.filter(id=22).update(parent_id=25)
    StatementDictionary.objects.filter(id=23).update(parent_id=25)
    StatementDictionary.objects.filter(id=24).update(parent_id=25)
    StatementDictionary.objects.filter(id=25).update(parent_id=43)
    StatementDictionary.objects.filter(id=26).update(parent_id=31)
    StatementDictionary.objects.filter(id=27).update(parent_id=31)
    StatementDictionary.objects.filter(id=28).update(parent_id=31)
    StatementDictionary.objects.filter(id=29).update(parent_id=31)
    StatementDictionary.objects.filter(id=30).update(parent_id=31)
    StatementDictionary.objects.filter(id=31).update(parent_id=43)
    StatementDictionary.objects.filter(id=32).update(parent_id=36)
    StatementDictionary.objects.filter(id=33).update(parent_id=36)
    StatementDictionary.objects.filter(id=34).update(parent_id=36)
    StatementDictionary.objects.filter(id=35).update(parent_id=36)
    StatementDictionary.objects.filter(id=36).update(parent_id=43)
    StatementDictionary.objects.filter(id=37).update(parent_id=42)
    StatementDictionary.objects.filter(id=38).update(parent_id=42)
    StatementDictionary.objects.filter(id=39).update(parent_id=42)
    StatementDictionary.objects.filter(id=40).update(parent_id=42)
    StatementDictionary.objects.filter(id=41).update(parent_id=42)
    StatementDictionary.objects.filter(id=42).update(parent_id=43)
    StatementDictionary.objects.filter(id=70).update(parent_id=18)
    StatementDictionary.objects.filter(id=71).update(parent_id=18)
    StatementDictionary.objects.filter(id=72).update(parent_id=18)
    StatementDictionary.objects.filter(id=73).update(parent_id=18)
    StatementDictionary.objects.filter(id=74).update(parent_id=18)
    StatementDictionary.objects.filter(id=75).update(parent_id=43)
    StatementDictionary.objects.filter(id=76).update(parent_id=43)
    StatementDictionary.objects.filter(id=77).update(parent_id=43)
    StatementDictionary.objects.filter(id=78).update(parent_id=43)
    StatementDictionary.objects.filter(id=79).update(parent_id=43)
    StatementDictionary.objects.filter(id=80).update(parent_id=43)
    StatementDictionary.objects.filter(id=81).update(parent_id=43)
    StatementDictionary.objects.filter(id=82).update(parent_id=43)


class Migration(migrations.Migration):
    dependencies = [
        ('bfo', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forward_insert_statement_form, backward_insert_statement_form),
        migrations.RunPython(forward_insert_statement_dictionary, backward_insert_statement_dictionary),
        migrations.RunPython(forward_set_parent_statement_dictionary, migrations.RunPython.noop),
    ]
