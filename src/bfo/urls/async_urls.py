from django.urls import path

from bfo.views.async_views import (
    fin_report_api_view,
    fin_statements_api_view,
)

urlpatterns = [
    path('finreports/', fin_report_api_view, name='fin_reports_async'),
    path('finstatements/', fin_statements_api_view, name='fin_statements_async'),
]
