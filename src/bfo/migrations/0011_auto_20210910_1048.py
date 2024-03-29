# Generated by Django 2.2.24 on 2021-09-10 10:48

from django.db import migrations, models


def forward(apps, schema_editor):
    FinancialReportFile = apps.get_model('bfo', 'FinancialReportFile')
    FinancialReportFile.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('bfo', '0010_auto_20210909_1542'),
    ]

    operations = [
        migrations.RunPython(forward, migrations.RunPython.noop),
        migrations.RemoveIndex(
            model_name='financialreportfile',
            name='bfo_financi_ogrn_fbd061_idx',
        ),
        migrations.RemoveIndex(
            model_name='financialreportfile',
            name='bfo_financi_year_bf7aad_idx',
        ),
        migrations.RemoveField(
            model_name='financialreportfile',
            name='year',
        ),
        migrations.AddField(
            model_name='financialreportfile',
            name='year',
            field=models.SmallIntegerField(verbose_name='Дата отчёта'),
        ),
        migrations.AlterIndexTogether(
            name='financialreportfile',
            index_together={('ogrn', 'year')},
        ),
        migrations.RemoveField(
            model_name='financialreportfile',
            name='changed_at',
        ),
    ]
