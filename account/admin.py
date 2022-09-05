from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .forms import UserCreationForm, UserChangeForm
from .models import User, Company, Offer, OfferAvailability, OffersStore

admin.site.unregister(Group)


@admin.register(User)
class AccountAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    pass


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    pass


@admin.register(OfferAvailability)
class OfferAvailabilityAdmin(admin.ModelAdmin):
    pass


@admin.register(OffersStore)
class OffersStoreAdmin(admin.ModelAdmin):
    pass
