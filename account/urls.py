from django.urls import path, include

from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    CompanyUpdateView,
    AccountsIndexView,
    CompaniesPageView,
    xml_data_view,
    OfferDeleteView,
    OfferUpdateView,
    StoresListView,
    StoreCreateView,
    StoreUpdateView,
    StoreDeleteView,
    OfferCreateView,
    CompanyCreateView,
    CompanyDeleteView,
    OffersListView,
)


stores_patterns = [
    path('', StoresListView.as_view(), name='stores__list'),
    path('create/', StoreCreateView.as_view(), name='stores__create'),
    path('<int:store_id>/', StoreUpdateView.as_view(), name='stores__update'),
    path('<int:store_id>/delete/', StoreDeleteView.as_view(), name='stores__delete'),
]


companies_patterns = [
    path('', CompaniesPageView.as_view(), name='companies__list'),
    path('create/', CompanyCreateView.as_view(), name='companies__create'),
    path('<int:company_id>/', CompanyUpdateView.as_view(), name='companies__update'),
    path('<int:company_id>/delete/', CompanyDeleteView.as_view(), name='companies__delete'),
    path('<int:company_id>/offers/', OffersListView.as_view(), name='offers__list'),
    path('<int:company_id>/offers/create/', OfferCreateView.as_view(), name='offers__create'),
    path('<int:company_id>/offers/<int:offer_id>/', OfferUpdateView.as_view(), name='offers__update'),
    path('<int:company_id>/offers/<int:offer_id>/delete/', OfferDeleteView.as_view(), name='offers__delete'),
    path('<int:company_id>/offers/xml/', xml_data_view, name='offers__xml'),
]

urlpatterns = [
    path('login/', LoginView.as_view(), name='accounts__login'),
    path('logout/', LogoutView.as_view(), name='accounts__logout'),
    path('register/', RegisterView.as_view(), name='accounts__register'),
    path('', AccountsIndexView.as_view(), name='accounts__index'),
    path('companies/', include(companies_patterns)),
    path('stores/', include(stores_patterns)),
]
