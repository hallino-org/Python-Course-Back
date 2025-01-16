from django.contrib import admin

from .models import User, Author, UserCourse, Streak, UserResponse, Staff


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'phone_number', 'type', 'level', 'is_active', 'is_confirmed', 'is_staff')
    list_filter = ('is_active', 'is_confirmed', 'is_staff', 'type', 'level', 'gender')
    search_fields = ('email', 'firstname', 'lastname', 'phone_number')
    ordering = ('-created_at',)

    fieldsets = (
        ('Personal Info', {
            'fields': ('email', 'password', 'firstname', 'lastname', 'phone_number', 'gender', 'birth_date')
        }),
        ('Status', {
            'fields': ('type', 'level', 'is_active', 'is_confirmed', 'is_staff', 'expire_date')
        }),
        ('Important Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return (
                (None, {
                    'classes': ('wide',),
                    'fields': ('email', 'firstname', 'lastname', 'phone_number', 'password1', 'password2'),
                }),
            )
        return self.fieldsets


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('user_full_name', 'specialization_count')
    search_fields = ('user__firstname', 'user__lastname', 'user__email', 'bio')
    filter_horizontal = ('specializations',)
    raw_id_fields = ('user',)

    def user_full_name(self, obj):
        return obj.user.full_name

    user_full_name.short_description = 'Author Name'

    def specialization_count(self, obj):
        return obj.specializations.count()

    specialization_count.short_description = 'Specializations'


@admin.register(UserCourse)
class UserCourseAdmin(admin.ModelAdmin):
    list_display = ('user', 'progress', 'score', 'rank', 'course_count')
    list_filter = ('progress', 'rank')
    search_fields = ('user__email', 'user__firstname', 'user__lastname')
    raw_id_fields = ('user',)
    filter_horizontal = ('courses',)

    def course_count(self, obj):
        return obj.courses.count()

    course_count.short_description = 'Number of Courses'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Streak)
class StreakAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_streak', 'highest_streak', 'type', 'last_interaction')
    list_filter = ('type', 'last_interaction')
    search_fields = ('user__email', 'user__firstname', 'user__lastname')
    raw_id_fields = ('user',)
    readonly_fields = ('current_streak', 'highest_streak', 'last_interaction')

    actions = ['reset_streaks']

    def reset_streaks(self, request, queryset):
        queryset.update(current_streak=0, highest_streak=0, last_interaction=None)

    reset_streaks.short_description = "Reset selected streaks"


@admin.register(UserResponse)
class UserResponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'submitted_at', 'question_count', 'has_text_answer', 'choice_count')
    list_filter = ('submitted_at',)
    search_fields = ('user__email', 'text_answer')
    raw_id_fields = ('user',)
    filter_horizontal = ('question', 'choice_answers')
    readonly_fields = ('submitted_at',)

    def question_count(self, obj):
        return obj.question.count()

    question_count.short_description = 'Questions'

    def has_text_answer(self, obj):
        return bool(obj.text_answer)

    has_text_answer.boolean = True
    has_text_answer.short_description = 'Has Text Answer'

    def choice_count(self, obj):
        return obj.choice_answers.count()

    choice_count.short_description = 'Selected Choices'


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('user_full_name', 'user_email', 'role_type')
    list_filter = ('role_type',)
    search_fields = ('user__email', 'user__firstname', 'user__lastname')
    raw_id_fields = ('user',)

    def user_full_name(self, obj):
        return obj.user.full_name

    user_full_name.short_description = 'Staff Name'

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'Email'
