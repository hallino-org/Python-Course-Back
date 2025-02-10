from django.db import models
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import (
    CourseFilter, ChapterFilter, LessonFilter,
    QuestionFilter, SlideFilter
)
from .models import (
    Category, Course, Chapter, Lesson,
    Editor, BaseQuestion, Choice, Slide
)
from .permissions import (
    IsAuthorOrReadOnly, IsStaffOrReadOnly,
    IsCourseAuthorOrReadOnly
)
from .serializers import (
    CategorySerializer, CourseSerializer, ChapterSerializer,
    LessonSerializer, EditorSerializer, BaseQuestionSerializer,
    ChoiceSerializer, SlideSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'slug', 'description']
    ordering_fields = ['title', 'created_at']
    ordering = ['title']


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [IsCourseAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CourseFilter
    search_fields = ['title', 'description', 'authors__username']
    ordering_fields = ['title', 'created_at', 'price', 'rating']
    ordering = ['-created_at']

    def get_queryset(self):
        category_pk = self.kwargs.get('category_pk')
        if category_pk:
            return Course.objects.filter(categories__id=category_pk, is_published=True, is_active=True)

        return Course.objects.filter(is_published=True, is_active=True)

    @action(detail=True, methods=['post'])
    def add_categories(self, request, pk=None):
        """
        Add additional categories to a course
        Expects a list of category IDs in the request body:
        {
            "category_ids": [1, 2, 3]
        }
        """
        course = self.get_object()
        category_ids = request.data.get('category_ids', [])

        try:
            categories = Category.objects.filter(id__in=category_ids)
            if len(categories) != len(category_ids):
                return Response(
                    {'error': 'One or more category IDs are invalid'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Add new categories without removing existing ones
            course.categories.add(*categories)
            return Response({
                'status': 'success',
                'categories': CategorySerializer(course.categories.all(), many=True).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def remove_categories(self, request, pk=None):
        """
        Remove categories from a course
        Expects a list of category IDs in the request body:
        {
            "category_ids": [1, 2, 3]
        }
        """
        course = self.get_object()
        category_ids = request.data.get('category_ids', [])

        try:
            categories = Category.objects.filter(id__in=category_ids)
            course.categories.remove(*categories)
            return Response({
                'status': 'success',
                'categories': CategorySerializer(course.categories.all(), many=True).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        course = self.get_object()
        course.is_published = not course.is_published
        course.save()
        return Response({
            'status': 'success',
            'is_published': course.is_published
        })

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        course = self.get_object()
        return Response({
            'total_chapters': course.chapters.count(),
            'total_lessons': Lesson.objects.filter(chapter__course=course).count(),
        })


class ChapterViewSet(viewsets.ModelViewSet):
    serializer_class = ChapterSerializer
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ChapterFilter
    search_fields = ['title', 'description']
    ordering_fields = ['order', 'created_at']
    ordering = ['order']

    def get_queryset(self):
        course_pk = self.kwargs.get('course_pk')
        if course_pk:
            return Chapter.objects.filter(course__id=course_pk, is_active=True)

        return Chapter.objects.filter(is_active=True)

    def perform_create(self, serializer):
        course = serializer.validated_data['course']
        if not serializer.validated_data.get('order'):
            last_order = course.chapters.aggregate(models.Max('order'))['order__max']
            serializer.save(order=last_order + 1 if last_order else 1)
        else:
            serializer.save()


class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = LessonFilter
    search_fields = ['title', 'description']
    ordering_fields = ['order', 'created_at']
    ordering = ['order']

    def get_queryset(self):
        chapter_pk = self.kwargs.get('chapter_pk')
        if chapter_pk:
            return Lesson.objects.filter(chapter__id=chapter_pk, is_active=True)

        return Lesson.objects.filter(is_active=True)

    @action(detail=True, methods=['post'])
    def reorder_slides(self, request, pk=None):
        """Reorder slides in the lesson"""
        lesson = self.get_object()
        slide_orders = request.data.get('slide_orders', [])

        if not slide_orders:
            return Response(
                {'error': 'No slide orders provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        for order_data in slide_orders:
            slide = get_object_or_404(Slide, id=order_data['slide_id'])
            slide.order = order_data['order']
            slide.save()

        return Response({'status': 'success'})


class EditorViewSet(viewsets.ModelViewSet):
    queryset = Editor.objects.all()
    serializer_class = EditorSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['initial_code']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class BaseQuestionViewSet(viewsets.ModelViewSet):
    queryset = BaseQuestion.objects.all()
    serializer_class = BaseQuestionSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = QuestionFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def add_choice(self, request, pk=None):
        """Add a new choice to the question"""
        question = self.get_object()
        serializer = ChoiceSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(question=question)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['text']
    ordering_fields = ['order']
    ordering = ['order']


class SlideViewSet(viewsets.ModelViewSet):
    queryset = Slide.objects.all()
    serializer_class = SlideSerializer
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SlideFilter
    search_fields = ['title', 'content']
    ordering_fields = ['order', 'created_at']
    ordering = ['order']

    @action(detail=True, methods=['post'])
    def toggle_activity(self, request, pk=None):
        """Toggle slide active status"""
        slide = self.get_object()
        slide.is_active = not slide.is_active
        slide.save()
        return Response({
            'status': 'success',
            'is_active': slide.is_active
        })

    @action(detail=True, methods=['post'])
    def increment_comments(self, request, pk=None):
        """Increment comments count"""
        slide = self.get_object()
        slide.comments_count += 1
        slide.save()
        return Response({
            'status': 'success',
            'comments_count': slide.comments_count
        })
