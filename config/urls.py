from django.contrib import admin
from django.urls import include, path

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Click Billing System API",
        default_version='v1',
        description="[Github Repo](https://github.com/PayTechUz/click-sample)",
        contact=openapi.Contact(url="https://t.me/@Jabborbek_Qobilov"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny, ],
)

urlpatterns = [
    path('', admin.site.urls),
    # path('', include('user.urls')),
    # path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    # path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
