from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('account.urls')),
]

handler404 = 'account.views.error_404_view'
