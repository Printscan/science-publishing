from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    EditorialRoleViewSet,
    PublicationViewSet,
    UserProfileRoleViewSet,
    UserProfileViewSet,
    WorkViewSet,
)

router = DefaultRouter()
router.register('roles', EditorialRoleViewSet, basename='science-publishing-role')
router.register('profiles', UserProfileViewSet, basename='science-publishing-profile')
router.register('profile-roles', UserProfileRoleViewSet, basename='science-publishing-profile-role')
router.register('works', WorkViewSet, basename='science-publishing-work')
router.register('publications', PublicationViewSet, basename='science-publishing-publication')

urlpatterns = [
    path('', include(router.urls)),
]
