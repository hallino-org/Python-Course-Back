class LearningConstants:
    # Question Types
    QUESTION_CHOICE = 1
    QUESTION_TEXT = 2

    QUESTION_TYPE_CHOICES = [
        (1, 'Single Choice'),
        (2, 'Multiple Choice'),
        (3, 'Text'),
    ]

    # Lesson Types
    LESSON_TYPE_CHOICES = [
        (1, 'Lesson'),
        (2, 'Quiz'),
    ]

    # Levels of Courses
    LEVEL_CHOICES = [
        (1, 'Elementary'),
        (2, 'Intermediate'),
        (3, 'Upper Intermediate'),
        (4, 'Advanced'),
    ]

    # Programming Languages
    LANG_PYTHON = 'py'

    LANGUAGE_CHOICES = [
        (LANG_PYTHON, 'Python'),
    ]

    # Choice Types
    CHOICE_TYPE_CHOICES = [
        (1, 'Text Choice'),
        (2, 'Picture Choice'),
        (3, 'None'),
        (4, 'All'),
        (5, 'Other'),
    ]

    # Slide tpes
    SLIDE_TYPE_CHOICES = [
        (1, 'Text'),
        (2, 'Quiz'),
    ]
