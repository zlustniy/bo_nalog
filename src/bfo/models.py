from dj_model_utils.abstract_models.datetime_tracking import DatetimeTrackingModel
from django.db import models
from django.db.models import JSONField, Q
from django.utils.translation import gettext_lazy as _


def base_url_setting_default_value():
    return 'https://api.bo.nalog.ru/'


class Setting(DatetimeTrackingModel):
    base_url = models.CharField(
        max_length=500,
        default=base_url_setting_default_value,
        verbose_name=_('URL для скачивания'),
    )
    last_at = models.DateTimeField(
        null=True,
        blank=True,
        default=None,
        verbose_name=_('Дата последнего успешного сохранения данных в таблицу bfo_orgstatement'),
    )
    username = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        verbose_name=_('Логин'),
    )
    password = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        verbose_name=_('Пароль (зашифрованный)'),
    )

    class Meta:
        verbose_name = _('Настройки загрузки финансовых показателей')
        verbose_name_plural = _('Настройки загрузки финансовых показателей')

    def __str__(self):
        return 'Настройка загрузки финансовых показателей'


class FinancialStatementPage(DatetimeTrackingModel):
    year = models.IntegerField(
        verbose_name=_('Год'),
    )
    page = models.IntegerField(
        verbose_name=_('Номер страницы'),
    )
    total_pages = models.IntegerField(
        verbose_name=_('Общее количество страниц'),
    )
    size = models.IntegerField(
        verbose_name=_('Количество записей на странице'),
    )
    actual_size = models.IntegerField(
        verbose_name=_('Фактическое количество элементов на странице'),
    )
    sort = models.CharField(
        max_length=255,
        verbose_name=_('Параметры сортировки'),
    )
    params = JSONField(
        verbose_name=_('Параметры запроса'),
    )

    class Meta:
        verbose_name = _('Страница финансовой отчетности')
        verbose_name_plural = _('Страницы финансовой отчетности')

    def __str__(self):
        return f'{self.year}: page {self.page} of {self.total_pages - 1}'


class FinancialStatementFile(DatetimeTrackingModel):
    downloaded_page = models.ForeignKey(
        FinancialStatementPage,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name=_('Страница внутри фин. показателей.'),
    )
    external_id = models.IntegerField(
        verbose_name=_('ID на ГИРБО'),
        primary_key=False,
    )
    token = models.CharField(
        max_length=50,
        verbose_name=_('Токен'),
        unique=True,
    )
    inn = models.CharField(
        max_length=10,
        verbose_name=_('ИНН'),
    )
    file_name = models.CharField(
        max_length=500,
        verbose_name=_('Название файла'),
    )
    report_type = models.CharField(
        max_length=50,
        verbose_name=_('Тип отчёта'),
    )
    period = models.CharField(
        max_length=4,
        verbose_name=_('Отчётный период'),
    )
    upload_date = models.DateField(
        verbose_name=_('Дата представления файла'),
    )
    is_downloaded = models.BooleanField(
        default=False,
        verbose_name=_('Файл загружен и обработан'),
    )

    class Meta:
        verbose_name = _('Файл финансовой отчетности')
        verbose_name_plural = _('Файлы финансовой отчетности')
        indexes = [
            models.Index(fields=['inn', ]),
            models.Index(fields=['token', ]),
        ]

    def __str__(self):
        return f'{self.token}: {self.file_name} ({self.report_type})'


class StatementForm(DatetimeTrackingModel):
    form_name = models.CharField(
        max_length=255,
        verbose_name=_('Наименование формы'),
    )

    class Meta:
        verbose_name = _('Форма отчетности')
        verbose_name_plural = _('Формы отчетности')

    def __str__(self):
        return self.form_name


class StatementDictionary(DatetimeTrackingModel):
    title = models.CharField(
        max_length=500,
        verbose_name=_('Название показателя'),
    )
    code = models.CharField(
        max_length=4,
        null=True,
        blank=True,
        verbose_name=_('Код'),
    )
    ext_name = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_('Название параметра, пришедшего из ГИР БО'),
    )
    form = models.ForeignKey(
        StatementForm,
        on_delete=models.CASCADE,
        verbose_name=_('Форма отчетности'),
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='child',
        blank=True,
        null=True,
        verbose_name=_('Родительский финансовый показатель'),
    )

    class Meta:
        verbose_name = _('Справочник финансовых показателей')
        verbose_name_plural = _('Справочники финансовых показателей')

    def __str__(self):
        return f'{self.code}: {self.title} ({self.ext_name})'


class OrgStatementSharedFields(DatetimeTrackingModel):
    statement_file = models.ForeignKey(
        FinancialStatementFile,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_('Актуальные значения финансовых показателей'),
    )
    report_date = models.DateField(
        null=False,
        verbose_name=_('Дата отчёта'),
    )
    data_from_src = JSONField(
        null=True,
        blank=True,
        default=None,
        verbose_name=_('Значения финансовых показателей'),
    )
    inn = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name=_('ИНН организации'),
    )
    kpp = models.CharField(
        max_length=9,
        null=True,
        blank=True,
        verbose_name=_('КПП организации'),
    )

    class Meta:
        abstract = True


class OrgStatement(OrgStatementSharedFields):
    class Meta:
        verbose_name = _('Значения финансовых показателей по организациям')
        verbose_name_plural = _('Значения финансовых показателей по организациям')
        index_together = [
            ('inn', 'kpp'),
        ]

    def __str__(self):
        return f'OrgStatement id={self.id}, inn={self.inn}, kpp={self.kpp}'


class PreviousOrgStatement(OrgStatementSharedFields):
    class Meta:
        verbose_name = _('Устаревшие значения финансовых показателей по организациям')
        verbose_name_plural = _('Устаревшие значения финансовых показателей по организациям')
        index_together = [
            ('inn', 'kpp'),
        ]

    def __str__(self):
        return f'PreviousOrgStatement id={self.id}, inn={self.inn}, kpp={self.kpp}'


class DifferenceStatement(DatetimeTrackingModel):
    org_statement = models.ForeignKey(
        OrgStatement,
        on_delete=models.CASCADE,
        verbose_name=_('Актуальные значения финансовых показателей'),
    )
    previous_org_statement = models.ForeignKey(
        PreviousOrgStatement,
        on_delete=models.CASCADE,
        verbose_name=_('Устаревшие значения финансовых показателей'),
    )
    diff = JSONField(
        null=True,
        blank=True,
        default=None,
        verbose_name=_('Разница'),
    )

    class Meta:
        verbose_name = _('Разница актуальных и устаревших значений финансовых показателей')
        verbose_name_plural = _('Разница актуальных и устаревших значений финансовых показателей')

    def __str__(self):
        return f'DifferenceStatement inn={self.org_statement.inn}'


class TemporaryINN(DatetimeTrackingModel):
    statement_file = models.ForeignKey(
        FinancialStatementFile,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_('Актуальные значения финансовых показателей'),
    )
    inn = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name=_('ИНН организации'),
    )


class FinancialReportFile(models.Model):
    file = models.FileField(upload_to='fin_reports/%Y/%m/%d')
    ogrn = models.CharField(
        max_length=15,
    )
    inn = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_('ИНН организации'),
    )
    year = models.SmallIntegerField(
        null=False,
        verbose_name=_('Дата отчёта'),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата и время создания'))
    is_active = models.BooleanField(default=True, verbose_name=_('Файл актуален'))

    class Meta:
        index_together = [
            ('ogrn', 'year', 'is_active'),
        ]
        constraints = [
            models.UniqueConstraint(
                name='ogrn_year_is_active_unique',
                fields=['ogrn', 'year', 'is_active'],
                condition=Q(is_active=True),
            ),
        ]
