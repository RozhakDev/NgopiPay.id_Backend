from django.urls import path
from .views import SalesReportView

urlpatterns = [
    path('sales/', SalesReportView.as_view(), name='sales-report'),
]