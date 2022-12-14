from django.urls import path, include

from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    CompanyView,
    AccountsIndexView,
    CompaniesPageView,
    xml_data_view,
    OffersListView,
    OfferDeleteView,
    OfferUpdateView,
)


companies_patterns = [
    path('', CompaniesPageView.as_view(), name='companies__index'),
    path('<int:company_id>/', CompanyView.as_view(), name='companies__detail'),
    path('<int:company_id>/offers/', OffersListView.as_view(), name='offers__list'),
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
]
