from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (UserViewSet, send_confirmation_code, obtain_token,
                    CategoryViewSet, GenreViewSet, TitleViewSet, ReviewViewSet, CommentViewSet)


router = DefaultRouter()
router.register('users', UserViewSet, basename='User')
router.register(r'categories', CategoryViewSet)
router.register(r'genres', GenreViewSet)
router.register(r'titles', TitleViewSet)
router.register(r'titles/(?P<title_id>\d+)/reviews',
                ReviewViewSet, basename='Review')
router.register(r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
                CommentViewSet, basename='Comment')

auth_patterns = [
    path('email/', send_confirmation_code),
    path('token/', obtain_token)
]

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include(auth_patterns))
]
