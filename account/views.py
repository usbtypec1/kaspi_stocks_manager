import datetime

from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import FormView, ListView, DetailView, TemplateView, RedirectView
from django.views.generic.edit import FormMixin, ProcessFormView

from .forms import UserCreationForm, CreateCompanyForm, CreateOfferForm
from .models import Company, Offer


class CompaniesPageView(LoginRequiredMixin, FormMixin, ListView):
    template_name = 'account/pages/companies.html'
    queryset = Company.objects.all()
    form_class = CreateCompanyForm
    context_object_name = 'companies'
    success_url = reverse_lazy('companies__index')

    post = ProcessFormView.post

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        return super().form_valid(form)


class CompanyView(LoginRequiredMixin, DetailView):
    queryset = Company.objects.all()
    model = Company
    context_object_name = 'company'
    extra_context = {'form': CreateOfferForm()}
    template_name = 'account/pages/company.html'

    def post(self, *args, pk=None, **kwargs):
        print(args)
        print(kwargs)
        print(pk)
        data = self.request.POST.copy()
        data['company_id'] = [pk]
        form = CreateOfferForm(data)
        print(data)
        if form.is_valid():
            form.save()
        return reverse('companies__detail', kwargs={'pk': pk})

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['companies'] = self.request.user.company_set.all()
        context_data['offers'] = self.object.offer_set.all()
        return context_data


def error_404_view(request, *args):
    return render(request, 'account/errors/404.html')


def xml_data_view(request, company_uuid):
    company = get_object_or_404(Company, uuid=company_uuid)
    offers = Offer.objects.filter(company__uuid=company_uuid)
    now = timezone.now() + datetime.timedelta(hours=3)
    context = {'date': now.date().isoformat(), 'company': company, 'offers': offers}
    return render(request, 'account/offers.xml', context=context, content_type='text/xml')


class LoginView(auth_views.LoginView):
    template_name = 'account/registration/login.html'
    redirect_authenticated_user = True


class RegisterView(FormView):
    form_class = UserCreationForm
    template_name = 'account/registration/register.html'


class LogoutView(auth_views.LogoutView):
    template_name = 'account/registration/logout.html'
    get = TemplateView.get


class AccountsIndexView(RedirectView):
    permanent = True
    pattern_name = 'companies__index'