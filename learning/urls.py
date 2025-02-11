from django.urls import path, include
from rest_framework_nested import routers

from .views import (
    CategoryViewSet, CourseViewSet, ChapterViewSet,
    LessonViewSet, EditorViewSet, BaseQuestionViewSet,
    ChoiceViewSet, SlideViewSet
)

router = routers.DefaultRouter()

# Register ViewSets
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'chapters', ChapterViewSet, basename='chapter')
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'editors', EditorViewSet, basename='editor')
router.register(r'questions', BaseQuestionViewSet, basename='question')
router.register(r'choices', ChoiceViewSet, basename='choice')
router.register(r'slides', SlideViewSet, basename='slide')

categories_router = routers.NestedDefaultRouter(router, r'categories', lookup='category')
categories_router.register(r'courses', CourseViewSet, basename='category-courses')

courses_router = routers.NestedDefaultRouter(router, r'courses', lookup='course')
courses_router.register(r'chapters', ChapterViewSet, basename='course-chapters')

chapters_router = routers.NestedDefaultRouter(router, r'chapters', lookup='chapter')
chapters_router.register(r'lessons', LessonViewSet, basename='chapter-lessons')

lessons_router = routers.NestedDefaultRouter(router, r'lessons', lookup='lesson')
lessons_router.register(r'slides', SlideViewSet, basename='lesson-slides')

slides_router = routers.NestedDefaultRouter(router, r'slides', lookup='slide')
slides_router.register(r'questions', BaseQuestionViewSet, basename='slide-questions')
slides_router.register(r'editors', EditorViewSet, basename='slide-editors')

questions_router = routers.NestedDefaultRouter(router, r'questions', lookup='question')
questions_router.register(r'choices', ChoiceViewSet, basename='question-choices')

app_name = 'learning'

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    path('', include(categories_router.urls)),
    path('', include(courses_router.urls)),
    path('', include(chapters_router.urls)),
    path('', include(lessons_router.urls)),
    path('', include(slides_router.urls)),
    path('', include(questions_router.urls)),

    path('courses/<int:pk>/publish/',
         CourseViewSet.as_view({'post': 'publish'}),
         name='course-publish'),
    path('courses/<int:pk>/statistics/',
         CourseViewSet.as_view({'get': 'statistics'}),
         name='course-statistics'),

    path('lessons/<int:pk>/reorder-slides/',
         LessonViewSet.as_view({'post': 'reorder_slides'}),
         name='lesson-reorder-slides'),

    path('questions/<int:pk>/add-choice/',
         BaseQuestionViewSet.as_view({'post': 'add_choice'}),
         name='question-add-choice'),

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
