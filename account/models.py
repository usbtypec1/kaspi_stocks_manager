from uuid import uuid4

from django.contrib.auth import models as auth_models
from django.db import models
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy


class UserManager(auth_models.BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Users require an email field')
        username = get_random_string(32)
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(auth_models.AbstractUser):
    email = models.EmailField(gettext_lazy('email address'), unique=True, max_length=64)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        self.username = get_random_string(32)
        return super().save(*args, **kwargs)


class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    merchant_id = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'магазин'
        verbose_name_plural = 'магазины'

    def get_absolute_url(self):
        return reverse('companies__update', kwargs={'company_id': self.id})


class OffersStore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    marketplace_store_id = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'склад'
        verbose_name_plural = 'склады'


class Offer(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    sku = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255, null=True, blank=True)
    price = models.IntegerField()
    available_stores = models.ManyToManyField(OffersStore, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'
