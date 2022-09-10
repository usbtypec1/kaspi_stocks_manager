import datetime

from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import (
    ListView,
    DetailView,
    TemplateView,
    RedirectView,
    DeleteView,
    UpdateView,
    CreateView,
)
from django.views.generic.edit import FormMixin, ProcessFormView

from .forms import UserCreationForm, CreateCompanyForm, CreateOfferForm, CreateStoreForm
from .models import Company, Offer, OffersStore


class OfferDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'account/pages/offer_delete.html'

    def get_success_url(self):
        return reverse('companies__detail', kwargs={'company_id': self.kwargs['company_id']})


class OfferCreateView(LoginRequiredMixin, CreateView):
    form_class = CreateOfferForm
    template_name = 'account/pages/offer_create.html'
    success_url = reverse_lazy('companies__detail')


class OffersListView(LoginRequiredMixin, ListView):
    allow_empty = False
    template_name = 'account/pages/offers.html'

    def get_queryset(self):
        return Offer.objects.filter(company__user=self.request.user)

    def dispatch(self, *args, **kwargs):
        try:
            super().dispatch(*args, **kwargs)
            print('here')
        except Http404:
            return reverse('offers__create')


class OfferUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'account/pages/offer.html'
    queryset = Offer.objects.all()
    context_object_name = 'offer'
    pk_url_kwarg = 'offer_id'
    form_class = CreateOfferForm

    def get_object(self, queryset=None):
        offer_id = self.kwargs.get('offer_id')
        offer = get_object_or_404(Offer, id=offer_id)
        if offer.company.user != self.request.user:
            raise PermissionDenied
        return offer

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data |= {'company_id': self.kwargs['company_id']}
        return data

    def get_success_url(self):
        return reverse('companies__detail', kwargs={'company_id': self.kwargs['company_id']})


class CompaniesPageView(LoginRequiredMixin, FormMixin, ListView):
    template_name = 'account/pages/companies.html'
    model = Company
    form_class = CreateCompanyForm
    context_object_name = 'companies'
    success_url = reverse_lazy('companies__index')

    post = ProcessFormView.post

    def get_queryset(self):
        return Company.objects.filter(user=self.request.user)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        return super().form_valid(form)


class CompanyUpdateView(LoginRequiredMixin, UpdateView):
    pk_url_kwarg = 'company_id'
    context_object_name = 'company'
    form_class = CreateCompanyForm
    template_name = 'account/pages/company.html'

    def get_object(self, queryset=None):
        company_id = self.kwargs.get('company_id')
        company = get_object_or_404(Company, id=company_id)
        if company.user != self.request.user:
            raise PermissionDenied
        return company

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['companies'] = self.request.user.company_set.all()
        return context_data


class CompanyCreateView(CreateView):
    pk_url_kwarg = 'company_id'
    context_object_name = 'company'
    form_class = CreateCompanyForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        return reverse('companies__list', kwargs={'form': form})


def error_404_view(request, *args):
    return render(request, 'account/errors/404.html')


def xml_data_view(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    offers = Offer.objects.filter(company=company_id)
    now = timezone.now() + datetime.timedelta(hours=3)
    context = {'date': now.date().isoformat(), 'company': company, 'offers': offers,
               'stores': OffersStore.objects.filter(user=company.user)}
    return render(request, 'account/offers.xml', context=context, content_type='text/xml')


class LoginView(auth_views.LoginView):
    template_name = 'account/registration/login.html'
    redirect_authenticated_user = True


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'account/registration/register.html'
    success_url = reverse_lazy('companies__index')

    def form_valid(self, form):
        form.save(commit=True)
        return super().form_valid(form)


class LogoutView(auth_views.LogoutView):
    template_name = 'account/registration/logout.html'
    get = TemplateView.get


class AccountsIndexView(RedirectView):
    permanent = True
    pattern_name = 'companies__index'


class StoreCreateView(LoginRequiredMixin, CreateView):
    success_url = reverse_lazy('stores__list')
    form_class = CreateStoreForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class StoresListView(LoginRequiredMixin, ListView):
    template_name = 'account/pages/stores.html'
    context_object_name = 'stores'
    extra_context = {'form': CreateStoreForm()}

    def get_queryset(self):
        return OffersStore.objects.filter(user=self.request.user)


class StoreUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'account/pages/store.html'
    context_object_name = 'store'
    form_class = CreateStoreForm
    pk_url_kwarg = 'store_id'
    success_url = reverse_lazy('stores__list')

    def get_object(self, store_id=None):
        return get_object_or_404(OffersStore, pk=self.kwargs.get('store_id'), user=self.request.user)


class StoreDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'account/pages/store_delete.html'
    context_object_name = 'store'
    pk_url_kwarg = 'store_id'
    success_url = reverse_lazy('stores__list')

    def get_object(self, store_id=None):
        return get_object_or_404(OffersStore, pk=self.kwargs.get('store_id'), user=self.request.user)
