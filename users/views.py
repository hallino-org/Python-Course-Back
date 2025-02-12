from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from learning.models import Course
from learning.serializers import CourseSerializer
from .models import User, Author, UserCourse, Streak, UserResponse, Staff
from .permissions import IsOwnerOrStaff, IsStaffOrReadOnly
from .serializers import (
    UserSerializer, LoginSerializer, AuthorSerializer,
    UserCourseSerializer, StreakSerializer, UserResponseSerializer,
    StaffSerializer, PasswordChangeSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['email', 'firstname', 'lastname', 'phone_number']
    filterset_fields = ['type', 'level', 'is_active', 'is_confirmed']

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        user = self.get_object()
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not user.check_password(serializer.data.get('old_password')):
            return Response({'error': 'Wrong password'},
                            status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.data.get('new_password'))
        user.save()
        return Response({'status': 'password changed'})

    @action(detail=True, methods=['post'])
    def confirm_email(self, request, pk=None):
        user = self.get_object()
        user.is_confirmed = True
        user.save()
        return Response({'status': 'email confirmed'})


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__firstname', 'user__lastname', 'bio']

    @action(detail=True, methods=['get'])
    def courses(self, request, pk=None):
        author = self.get_object()
        active_courses = author.courses.filter(is_active=True)
        page = self.paginate_queryset(active_courses)
        serializer = CourseSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['post'])
    def become_author(self, request):
        """
        Allow a user to become an author
        """
        # Check if user is already an author
        if hasattr(request.user, 'author'):
            return Response(
                {'error': 'User is already an author'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create author profile
        data = request.data.copy()
        author = Author.objects.create(
            user=request.user,
            bio=data.get('bio', ''),
            specializations_id=data.get('specializations')
        )

        return Response(
            AuthorSerializer(author).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def add_to_course(self, request, pk=None):
        """
        Add author to a course
        """
        author = self.get_object()
        course_id = request.data.get('course_id')

        if not course_id:
            return Response(
                {'error': 'Course ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            course = Course.objects.get(id=course_id)
            course.authors.add(author)
            return Response({'status': 'Author added to course'})
        except Course.DoesNotExist:
            return Response(
                {'error': 'Course not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def remove_from_course(self, request, pk=None):
        """
        Remove author from a course
        """
        author = self.get_object()
        course_id = request.data.get('course_id')

        if not course_id:
            return Response(
                {'error': 'Course ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            course = Course.objects.get(id=course_id)
            course.authors.remove(author)
            return Response({'status': 'Author removed from course'})
        except Course.DoesNotExist:
            return Response(
                {'error': 'Course not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class UserCourseViewSet(viewsets.ModelViewSet):
    queryset = UserCourse.objects.all()
    serializer_class = UserCourseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course', 'progress']

    def get_queryset(self):
        if self.request.user.is_staff:
            return UserCourse.objects.all()
        return UserCourse.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        user_course = self.get_object()
        progress = request.data.get('progress', 0)

        if not 0 <= progress <= 100:
            return Response(
                {'error': 'Progress must be between 0 and 100'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_course.progress = progress
        user_course.save()
        return Response(UserCourseSerializer(user_course).data)


class StreakViewSet(viewsets.ModelViewSet):
    queryset = Streak.objects.all()
    serializer_class = StreakSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Streak.objects.all()
        return Streak.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def record_interaction(self, request, pk=None):
        streak = self.get_object()
        streak.update_streak()
        return Response(StreakSerializer(streak).data)


class UserResponseViewSet(viewsets.ModelViewSet):
    queryset = UserResponse.objects.all()
    serializer_class = UserResponseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['question']

    def get_queryset(self):
        if self.request.user.is_staff:
            return UserResponse.objects.all()
        return UserResponse.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__firstname', 'user__lastname', 'role_type']
