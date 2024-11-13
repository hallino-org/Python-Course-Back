from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Course, Lesson, Slide
from .serializers import (
    CourseListSerializer, CourseDetailSerializer,
    LessonSerializer, SlideSerializer, ChapterSerializer
)


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['level', 'language', 'categories', 'is_published']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'rating', 'price']

    def get_serializer_class(self):
        if self.action == 'list':
            return CourseListSerializer
        return CourseDetailSerializer

    @action(detail=True, methods=['get'])
    def chapters(self, request):
        course = self.get_object()
        chapters = course.get_active_chapters()
        serializer = ChapterSerializer(chapters, many=True)
        return Response(serializer.data)


class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Lesson.objects.filter(is_active=True)
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['lesson_type', 'is_required']
    ordering_fields = ['order', 'created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        chapter_id = self.request.query_params.get('chapter', None)
        if chapter_id:
            queryset = queryset.filter(chapter_id=chapter_id)
        return queryset


class SlideViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Slide.objects.filter(is_active=True)
    serializer_class = SlideSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['type', 'is_required']
    ordering_fields = ['order', 'created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        lesson_id = self.request.query_params.get('lesson', None)
        if lesson_id:
            queryset = queryset.filter(lesson_id=lesson_id)
        return queryset
