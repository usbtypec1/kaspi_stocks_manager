from django.urls import path

from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    CompanyView,
    AccountsIndexView,
    CompaniesPageView,
    xml_data_view,
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='accounts__login'),
    path('logout/', LogoutView.as_view(), name='accounts__logout'),
    path('register/', RegisterView.as_view(), name='accounts__register'),
    path('companies/', CompaniesPageView.as_view(), name='companies__index'),
    path('companies/<int:pk>', CompanyView.as_view(), name='companies__detail'),
    path('companies/<uuid:company_uuid>/offers/xml', xml_data_view, name='offers__xml'),
    path('', AccountsIndexView.as_view(), name='accounts__index'),
]
