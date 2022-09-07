import datetime

from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render
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

from .forms import UserCreationForm, CreateCompanyForm, CreateOfferForm
from .models import Company, Offer, OffersStore


class OfferDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'account/pages/offer_delete.html'

    def get_success_url(self):
        return reverse('companies__detail', kwargs={'company_id': self.kwargs['company_id']})


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


class CompanyView(LoginRequiredMixin, DetailView):
    model = Company
    pk_url_kwarg = 'company_id'
    context_object_name = 'company'
    extra_context = {'form': CreateOfferForm()}
    template_name = 'account/pages/company.html'

    def get_object(self, queryset=None):
        company_id = self.kwargs.get('company_id')
        company = get_object_or_404(Company, id=company_id)
        if company.user != self.request.user:
            raise PermissionDenied
        return company

    def post(self, *args, company_id=None, **kwargs):
        print(args)
        print(kwargs)
        data = self.request.POST.copy()
        data['company_id'] = [company_id]
        form = CreateOfferForm(data)
        print(data)
        if form.is_valid():
            form.save()
        return reverse('companies__detail', kwargs={'company_id': company_id})

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['companies'] = self.request.user.company_set.all()
        context_data['offers'] = self.object.offer_set.all()
        return context_data


def error_404_view(request, *args):
    return render(request, 'account/errors/404.html')


def xml_data_view(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    offers = Offer.objects.filter(company=company_id)
    now = timezone.now() + datetime.timedelta(hours=3)
    context = {'date': now.date().isoformat(), 'company': company, 'offers': offers,
               'stores': OffersStore.objects.filter(company=company)}
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
