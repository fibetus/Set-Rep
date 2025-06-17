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
    # Serve static files with proper MIME types
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve_static),
    ]
    
    # Serve HTML files
    urlpatterns += [
        re_path(r'^login\.html$', TemplateView.as_view(template_name='login.html')),
        re_path(r'^register\.html$', TemplateView.as_view(template_name='register.html')),
        re_path(r'^$', TemplateView.as_view(template_name='index.html'), name='home'),
        re_path(r'^index\.html$', TemplateView.as_view(template_name='index.html')),
        re_path(r'^workout\.html$', TemplateView.as_view(template_name='workout.html')),
        re_path(r'^plan\.html$', TemplateView.as_view(template_name='plan.html')),
    ]

    # Serve any HTML file in the frontend directory (for development only)
    urlpatterns += [
        re_path(r'^(?P<filename>[-\w]+\.html)$', TemplateView.as_view(), name='catch_all_html'),
    ] 