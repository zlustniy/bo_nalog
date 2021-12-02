from dj_model_utils.mixins.approx import ApproxCountPaginatorMixin
from django.contrib import admin
from django.db.models import JSONField
from django_json_widget.widgets import JSONEditorWidget
from dynamic_raw_id.admin import DynamicRawIDMixin

from .models import (
    Setting,
    StatementDictionary,
    StatementForm,
    OrgStatement,
    PreviousOrgStatement,
    DifferenceStatement,
    FinancialStatementPage,
    FinancialStatementFile,
)


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = (
        'base_url',
        'last_at',
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(OrgStatement)
class OrgStatementAdmin(
    # DisablePreselectMixin,
    ApproxCountPaginatorMixin,
    DynamicRawIDMixin,
    admin.ModelAdmin,
):
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }
    list_display = (
        'inn',
        'kpp',
        'report_date',
        'created_at',
        'changed_at',
    )
    readonly_fields = (
        'created_at',
        'changed_at',
        'report_date',
        'inn',
        'kpp',
    )
    dynamic_raw_id_fields = (
        'statement_file',
    )
    search_fields = (
        'inn',
    )

    def has_add_permission(self, request):
        return False


@admin.register(PreviousOrgStatement)
class PreviousOrgStatementAdmin(
    # DisablePreselectMixin,
    ApproxCountPaginatorMixin,
    DynamicRawIDMixin,
    admin.ModelAdmin,
):
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }
    list_display = (
        'inn',
        'kpp',
        'report_date',
    )
    readonly_fields = (
        'report_date',
        'inn',
        'kpp',
    )
    dynamic_raw_id_fields = (
        'statement_file',
    )
    search_fields = (
        'inn',
    )

    def has_add_permission(self, request):
        return False


@admin.register(DifferenceStatement)
class DifferenceStatementAdmin(
    # DisablePreselectMixin,
    ApproxCountPaginatorMixin,
    DynamicRawIDMixin,
    admin.ModelAdmin,
):
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }
    dynamic_raw_id_fields = (
        'org_statement',
        'previous_org_statement',
    )
    search_fields = (
        'org_statement__inn',
    )

    def has_add_permission(self, request):
        return False


@admin.register(FinancialStatementPage)
class FinancialStatementPageAdmin(
    # DisablePreselectMixin,
    ApproxCountPaginatorMixin,
    admin.ModelAdmin,
):
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }
    search_fields = (
        'page',
    )
    list_display = (
        'get_name',
        'created_at',
    )
    ordering = ('-year', '-page', '-created_at')

    def get_name(self, obj):
        return str(obj)

    get_name.short_description = 'Страница'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(FinancialStatementFile)
class FinancialStatementFileAdmin(
    # DisablePreselectMixin,
    ApproxCountPaginatorMixin,
    DynamicRawIDMixin,
    admin.ModelAdmin,
):
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }
    list_display = (
        'token',
        'inn',
        'file_name',
        'report_type',
        'period',
        'upload_date',
        'is_downloaded',
    )
    search_fields = (
        'inn',
        'token',
    )
    dynamic_raw_id_fields = (
        'downloaded_page',
    )

    def has_add_permission(self, request):
        return False


admin.site.register(StatementDictionary)
admin.site.register(StatementForm)
