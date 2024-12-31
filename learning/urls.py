from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, CourseViewSet, ChapterViewSet,
    LessonViewSet, EditorViewSet, BaseQuestionViewSet,
    ChoiceViewSet, SlideViewSet
)

router = DefaultRouter()

# Register ViewSets
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'chapters', ChapterViewSet, basename='chapter')
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'editors', EditorViewSet, basename='editor')
router.register(r'questions', BaseQuestionViewSet, basename='question')
router.register(r'choices', ChoiceViewSet, basename='choice')
router.register(r'slides', SlideViewSet, basename='slide')

app_name = 'learning'

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),

    # Custom Course URLs
    path('courses/<int:pk>/publish/',
         CourseViewSet.as_view({'post': 'publish'}),
         name='course-publish'),
    path('courses/<int:pk>/statistics/',
         CourseViewSet.as_view({'get': 'statistics'}),
         name='course-statistics'),

    # Custom Category URLs
    path('categories/<int:pk>/courses/',
         CategoryViewSet.as_view({'get': 'courses'}),
         name='category-courses'),

    # Custom Lesson URLs
    path('lessons/<int:pk>/reorder-slides/',
         LessonViewSet.as_view({'post': 'reorder_slides'}),
         name='lesson-reorder-slides'),

    # Custom Question URLs
    path('questions/<int:pk>/add-choice/',
         BaseQuestionViewSet.as_view({'post': 'add_choice'}),
         name='question-add-choice'),

    # Custom Slide URLs
    path('slides/<int:pk>/toggle-activity/',
         SlideViewSet.as_view({'post': 'toggle_activity'}),
         name='slide-toggle-activity'),
    path('slides/<int:pk>/increment-comments/',
         SlideViewSet.as_view({'post': 'increment_comments'}),
         name='slide-increment-comments'),

    path('courses/<int:pk>/add-categories/',
         CourseViewSet.as_view({'post': 'add_categories'}),
         name='course-add-categories'),
    path('courses/<int:pk>/remove-categories/',
         CourseViewSet.as_view({'post': 'remove_categories'}),
         name='course-remove-categories'),
]