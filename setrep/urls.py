from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from django.views.generic.base import RedirectView
from django.http import HttpResponse

def serve_static(request, path):
    return serve(request, path, document_root=settings.STATICFILES_DIRS[0])

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('workouts.urls')),
    path('api/v1/users/', include('users.urls', namespace='users')),
    path('api/v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Serve frontend files
if settings.DEBUG:
    # This will serve static files like CSS, JS, and also our HTML files
    # if they are requested with /static/ prefix.
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # This will serve the root path with index.html
    urlpatterns += [
        re_path(r'^$', TemplateView.as_view(template_name='index.html'), name='home'),
        re_path(r'^favicon\.ico$', lambda request: HttpResponse(status=204)),
    ]

    # Add this to handle direct navigation to your main html pages
    # without the need for them to be in a static folder.
    # The 'catch_all_html' was the problem, so let's be explicit.
    urlpatterns += [
        re_path(r'^(?P<page_name>index|login|register|plan|workout|edit-template|edit-workout)\.html$', 
                lambda request, page_name: TemplateView.as_view(template_name=f"{page_name}.html")(request), 
                name='html_pages'),
    ] 