from django.contrib.auth import forms as auth_forms
from django import forms

from .models import User, Company, Offer, OffersStore


class UserCreationForm(auth_forms.UserCreationForm):
    class Meta:
        model = User
        fields = ('email',)


class UserChangeForm(auth_forms.UserChangeForm):
    class Meta:
        model = User
        fields = ('email',)


class CreateCompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ('name', 'merchant_id')


class CreateOfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ('sku', 'name', 'brand', 'price', 'available_stores')


class CreateStoreForm(forms.ModelForm):
    class Meta:
        model = OffersStore
        fields = ('name', 'marketplace_store_id')


class OffersBatchUploadForm(forms.Form):
    file = forms.FileField()
