from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('account.urls')),
]

handler400 = 'account.views.error_400_view'
handler404 = 'account.views.error_404_view'
handler403 = 'account.views.error_403_view'
handler500 = 'account.views.error_500_view'
