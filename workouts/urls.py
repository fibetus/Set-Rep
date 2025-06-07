from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

router = DefaultRouter()
router.register(r'muscle-groups', views.MuscleGroupViewSet)
router.register(r'exercises', views.ExerciseViewSet)
router.register(r'workout-templates', views.WorkoutTemplateViewSet, basename='workout-template')
router.register(r'workouts', views.WorkoutViewSet, basename='workout')
router.register(r'sessions', views.WorkoutSessionViewSet, basename='session')
router.register(r'logged-exercises', views.LoggedExerciseViewSet, basename='logged-exercise')
router.register(r'sets', views.SetViewSet, basename='set')
router.register(r'plans', views.TrainingPlanViewSet, basename='plan')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', views.RegisterView.as_view(), name='register'),
] 