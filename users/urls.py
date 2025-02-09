from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .views import (
    UserViewSet, AuthorViewSet, UserCourseViewSet,
    StreakViewSet, UserResponseViewSet, StaffViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'authors', AuthorViewSet)
router.register(r'user-courses', UserCourseViewSet)
router.register(r'streaks', StreakViewSet)
router.register(r'user-responses', UserResponseViewSet)
router.register(r'staff', StaffViewSet)

app_name = 'users'

urlpatterns = [
    path('', include(router.urls)),

    # JWT Authentication endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # Custom User endpoints
    path('users/<int:pk>/change-password/',
         UserViewSet.as_view({'post': 'change_password'}),
         name='user-change-password'),
    path('users/<int:pk>/confirm-email/',
         UserViewSet.as_view({'post': 'confirm_email'}),
         name='user-confirm-email'),
    path('users/login/',
         UserViewSet.as_view({'post': 'login'}),
         name='user-login'),

    # Author endpoints
    path('authors/<int:pk>/courses/',
         AuthorViewSet.as_view({'get': 'courses'}),
         name='author-courses'),

    # UserCourse endpoints
    path('user-courses/<int:pk>/update-progress/',
         UserCourseViewSet.as_view({'post': 'update_progress'}),
         name='usercourse-update-progress'),

    # Streak endpoints
    path('streaks/<int:pk>/record-interaction/',
         StreakViewSet.as_view({'post': 'record_interaction'}),
         name='streak-record-interaction'),
]
