# Generated by Django 2.2.24 on 2021-09-09 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bfo', '0009_temporaryinn'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinancialReportFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')),
                ('changed_at', models.DateTimeField(auto_now=True, verbose_name='Дата и время редактирования')),
                ('file', models.FileField(upload_to='fin_reports/%Y/%m/%d')),
                ('ogrn', models.CharField(max_length=15)),
                ('year', models.DateField(verbose_name='Дата отчёта')),
            ],
        ),
        migrations.AddIndex(
            model_name='financialreportfile',
            index=models.Index(fields=['ogrn'], name='bfo_financi_ogrn_fbd061_idx'),
        ),
        migrations.AddIndex(
            model_name='financialreportfile',
            index=models.Index(fields=['year'], name='bfo_financi_year_bf7aad_idx'),
        ),
    ]