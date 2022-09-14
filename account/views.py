import datetime
from pathlib import Path

from django.conf import settings
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404, FileResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import (
    ListView,
    TemplateView,
    RedirectView,
    DeleteView,
    UpdateView,
    CreateView,
)

from .forms import UserCreationForm, CreateCompanyForm, CreateOfferForm, CreateStoreForm, OffersBatchUploadForm
from .models import Company, Offer, OffersStore
from .services import generate_offers_xlsx


class CompaniesContextDataMixin:

    def get_user_companies(self):
        return Company.objects.filter(user=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['companies'] = self.get_user_companies()
        return context


class OfferDeleteView(LoginRequiredMixin, DeleteView):
    model = Offer
    pk_url_kwarg = 'offer_id'

    def get_success_url(self):
        return reverse('offers__list', kwargs={'company_id': self.kwargs['company_id']})


class OfferCreateView(LoginRequiredMixin, CompaniesContextDataMixin, CreateView):
    form_class = CreateOfferForm
    template_name = 'account/pages/offer_create.html'
    extra_context = {'offers_batch_upload_form': OffersBatchUploadForm()}
    context_object_name = 'company'
    pk_url_kwarg = 'company_id'

    def get_success_url(self):
        return reverse('offers__list', kwargs={'company_id': self.kwargs.get('company_id')})

    def form_valid(self, form):
        company = get_object_or_404(Company, id=self.kwargs.get('company_id'))
        if company.user != self.request.user:
            raise PermissionDenied
        form.instance.company = company
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company_id = self.kwargs.get('company_id')
        context['company'] = context['companies'].get(id=company_id)
        return context


class OffersListView(LoginRequiredMixin, CompaniesContextDataMixin, ListView):
    allow_empty = False
    context_object_name = 'offers'
    template_name = 'account/pages/offers.html'

    def get_queryset(self):
        return Offer.objects.filter(company__user=self.request.user).order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_id'] = self.kwargs.get('company_id')
        return context

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            company_id = self.kwargs.get('company_id')
            return redirect(reverse('offers__create', kwargs={'company_id': company_id}))


class OfferUpdateView(LoginRequiredMixin, CompaniesContextDataMixin, UpdateView):
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
        return reverse('offers__list', kwargs={'company_id': self.kwargs['company_id']})


class CompanyUpdateView(LoginRequiredMixin, CompaniesContextDataMixin, UpdateView):
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


class CompanyCreateView(LoginRequiredMixin, CompaniesContextDataMixin, CreateView):
    pk_url_kwarg = 'company_id'
    context_object_name = 'company'
    form_class = CreateCompanyForm
    template_name = 'account/pages/company_create.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class CompanyDeleteView(DeleteView):
    pk_url_kwarg = 'company_id'
    context_object_name = 'company'
    success_url = reverse_lazy('companies__list')

    def get_object(self, queryset=None):
        return get_object_or_404(Company, user=self.request.user, id=self.kwargs.get('company_id'))


def error_404_view(request, *args):
    return render(request, 'account/errors/404.html')


def error_403_view(request, *args):
    return render(request, 'account/errors/403.html')


def error_400_view(request, *args):
    return render(request, 'account/errors/400.html')


def error_500_view(request, *args):
    return render(request, 'account/errors/500.html')


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
    success_url = reverse_lazy('accounts__index')

    def form_valid(self, form):
        form.save(commit=True)
        return super().form_valid(form)


class LogoutView(auth_views.LogoutView):
    template_name = 'account/registration/logout.html'
    get = TemplateView.get


class AccountsIndexView(LoginRequiredMixin, RedirectView):
    permanent = True
    pattern_name = 'companies__list'

    def get_redirect_url(self, *args, **kwargs):
        company = Company.objects.filter(user=self.request.user).order_by('id').first()
        if company is None:
            return reverse('companies__create')
        return reverse('companies__update', kwargs={'company_id': company.id})


class StoreCreateView(LoginRequiredMixin, CompaniesContextDataMixin, CreateView):
    success_url = reverse_lazy('stores__list')
    form_class = CreateStoreForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class StoresListView(LoginRequiredMixin, CompaniesContextDataMixin, ListView):
    template_name = 'account/pages/stores.html'
    context_object_name = 'stores'
    extra_context = {'form': CreateStoreForm()}

    def get_queryset(self):
        return OffersStore.objects.filter(user=self.request.user)


class StoreUpdateView(LoginRequiredMixin, CompaniesContextDataMixin, UpdateView):
    template_name = 'account/pages/store.html'
    context_object_name = 'store'
    form_class = CreateStoreForm
    pk_url_kwarg = 'store_id'
    success_url = reverse_lazy('stores__list')

    def get_object(self, store_id=None):
        return get_object_or_404(OffersStore, pk=self.kwargs.get('store_id'), user=self.request.user)


class StoreDeleteView(LoginRequiredMixin, CompaniesContextDataMixin, DeleteView):
    template_name = 'account/pages/store_delete.html'
    context_object_name = 'store'
    pk_url_kwarg = 'store_id'
    success_url = reverse_lazy('stores__list')

    def get_object(self, store_id=None):
        return get_object_or_404(OffersStore, pk=self.kwargs.get('store_id'), user=self.request.user)


class PasswordChangeView(CompaniesContextDataMixin, auth_views.PasswordChangeView):
    template_name = 'account/registration/change_password.html'
    form_class = auth_forms.PasswordChangeForm
    success_url = reverse_lazy('accounts__index')


class FAQPageView(CompaniesContextDataMixin, TemplateView):
    template_name = 'account/pages/faq.html'


def download_offers_xlsx_view(request, company_id=None):
    company = Company.objects.get(pk=company_id)
    file_path = Path.joinpath(settings.OFFER_FILES_ROOT, f'{company.id}.xlsx')
    generate_offers_xlsx(file_path, company)
    file_buffer = open(file_path, 'rb')
    return FileResponse(file_buffer, as_attachment=True, filename=f'{company.name} - товары.xlsx')
