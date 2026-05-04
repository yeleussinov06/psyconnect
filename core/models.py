from django.db import models
from django.contrib.auth.models import User


class SchoolClass(models.Model):
    """Класс/группа школы"""
    name = models.CharField(max_length=50, verbose_name='Название')
    description = models.CharField(max_length=200, blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def student_count(self):
        return self.members.filter(role='student').count()

    def teacher(self):
        t = self.members.filter(role='teacher').first()
        return t.user.get_full_name() if t else '—'

    class Meta:
        verbose_name = 'Класс'
        verbose_name_plural = 'Классы'
        ordering = ['name']


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Оқушы / Ученик'),
        ('parent', 'Ата-ана / Родитель'),
        ('teacher', 'Мұғалім / Учитель'),
        ('psychologist', 'Психолог'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    school_class = models.ForeignKey(
        SchoolClass, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='members',
        verbose_name='Класс'
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    bio = models.TextField(blank=True, verbose_name='О себе')
    avatar_color = models.CharField(max_length=7, default='#4A90D9')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        cls = f" [{self.school_class}]" if self.school_class else ""
        return f"{self.user.get_full_name()} ({self.role}){cls}"

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class ParentStudent(models.Model):
    """Связь родитель ↔ ученик"""
    parent = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='children_links',
        verbose_name='Родитель'
    )
    student = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='parent_links',
        verbose_name='Ученик'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('parent', 'student')
        verbose_name = 'Связь родитель — ученик'
        verbose_name_plural = 'Связи родитель — ученик'

    def __str__(self):
        return f"{self.parent.get_full_name()} → {self.student.get_full_name()}"


class EmotionEntry(models.Model):
    EMOTION_CHOICES = [
        ('happy',   'Жақсы / Хорошо'),
        ('calm',    'Тыныш / Спокойно'),
        ('anxious', 'Алаңдаулы / Тревожно'),
        ('sad',     'Қайғылы / Грустно'),
        ('angry',   'Ашулы / Злой'),
        ('tired',   'Шаршаулы / Устал'),
    ]
    EVENT_CHOICES = [
        ('',           '—'),
        ('bullying',   'Буллинг'),
        ('conflict',   'Семейный конфликт'),
        ('study',      'Стресс от учёбы'),
        ('loneliness', 'Одиночество'),
        ('other',      'Другое'),
    ]
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emotions')
    emotion    = models.CharField(max_length=20, choices=EMOTION_CHOICES)
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES, blank=True, default='', verbose_name='Тип события')
    note       = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.emotion} - {self.created_at.date()}"


class TestQuestion(models.Model):
    CATEGORY_CHOICES = [
        ('anxiety', 'Мазасыздық / Тревожность'),
        ('stress', 'Стресс'),
        ('motivation', 'Мотивация'),
        ('social', 'Әлеуметтік / Социальное'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    question_kz = models.TextField()
    question_ru = models.TextField()
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['category', 'order']

    def __str__(self):
        return f"[{self.category}] {self.question_ru[:60]}"


class TestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_results')
    category = models.CharField(max_length=20)
    score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=0)
    interpretation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    message = models.TextField()
    is_bot = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class AnonymousRequest(models.Model):
    STATUS_CHOICES = [
        ('new', 'Жаңа / Новый'),
        ('in_progress', 'Өңделуде / В работе'),
        ('closed', 'Жабылды / Закрыт'),
    ]
    REASON_CHOICES = [
        ('',           '—'),
        ('bullying',   'Буллинг'),
        ('conflict',   'Конфликт'),
        ('anxiety',    'Тревога'),
        ('family',     'Семейные проблемы'),
        ('study',      'Проблемы с учёбой'),
        ('other',      'Другое'),
    ]
    session_key = models.CharField(max_length=100)
    message     = models.TextField()
    reason      = models.CharField(max_length=20, choices=REASON_CHOICES, blank=True, default='', verbose_name='Причина обращения')
    response    = models.TextField(blank=True)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class Article(models.Model):
    AUDIENCE_CHOICES = [
        ('parent', 'Ата-аналар / Родители'),
        ('student', 'Оқушылар / Ученики'),
        ('teacher', 'Мұғалімдер / Учителя'),
    ]
    title_kz = models.CharField(max_length=200)
    title_ru = models.CharField(max_length=200)
    content_kz = models.TextField()
    content_ru = models.TextField()
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='parent')
    icon = models.CharField(max_length=10, default='📚')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title_ru


# Verbose names for admin
EmotionEntry._meta.verbose_name = 'Запись эмоции'
EmotionEntry._meta.verbose_name_plural = 'Записи эмоций'
AnonymousRequest._meta.verbose_name = 'Анонимный запрос'
AnonymousRequest._meta.verbose_name_plural = 'Анонимные запросы'
Article._meta.verbose_name = 'Статья'
Article._meta.verbose_name_plural = 'Статьи'
TestResult._meta.verbose_name = 'Результат теста'
TestResult._meta.verbose_name_plural = 'Результаты тестов'


class PsychologistSchedule(models.Model):
    """Свободный слот психолога"""
    psychologist = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='schedule_slots',
        verbose_name='Психолог'
    )
    date = models.DateField(verbose_name='Дата')
    time_start = models.TimeField(verbose_name='Начало')
    time_end = models.TimeField(verbose_name='Конец')
    is_available = models.BooleanField(default=True, verbose_name='Свободен')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'time_start']
        verbose_name = 'Слот расписания'
        verbose_name_plural = 'Расписание психолога'

    def __str__(self):
        return f"{self.psychologist.get_full_name()} — {self.date} {self.time_start}-{self.time_end}"


class Appointment(models.Model):
    """Запись ученика к психологу"""
    STATUS_CHOICES = [
        ('pending',   'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('rejected',  'Отклонено'),
        ('cancelled', 'Отменено'),
    ]
    REASON_CHOICES = [
        ('test',  'По результату теста'),
        ('chat',  'Через AI-чат'),
        ('manual','Самостоятельно'),
    ]
    student = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Ученик'
    )
    slot = models.OneToOneField(
        PsychologistSchedule, on_delete=models.CASCADE,
        related_name='appointment',
        verbose_name='Слот'
    )
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, default='manual', verbose_name='Причина')
    student_note = models.TextField(blank=True, verbose_name='Заметка ученика')
    psychologist_note = models.TextField(blank=True, verbose_name='Комментарий психолога')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Запись на приём'
        verbose_name_plural = 'Записи на приём'

    def __str__(self):
        return f"{self.student.get_full_name()} → {self.slot}"


class Notification(models.Model):
    """Уведомления внутри сайта"""
    TYPE_CHOICES = [
        ('appointment_new',       'Новая заявка на приём'),
        ('appointment_confirmed', 'Запись подтверждена'),
        ('appointment_rejected',  'Запись отклонена'),
        ('anonymous_new',         'Новый анонимный запрос'),
        # Цикл жалоб
        ('request_new',           'Новая жалоба ученика'),
        ('request_ai_ready',      'ИИ-анализ готов'),
        ('request_concluded',     'Психолог вынес заключение'),
        ('observation_new',       'Новый сигнал от учителя'),
        ('parent_conclusion',     'Заключение для родителя'),
    ]
    user      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notif_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    text      = models.TextField()
    link      = models.CharField(max_length=200, blank=True)
    is_read   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'

    def __str__(self):
        return f"{self.user.username} — {self.notif_type}"


# ══════════════════════════════════════════════════════════════
# ПСИХОЛОГИЧЕСКИЙ ТЕСТ-ЦЕНТР
# ══════════════════════════════════════════════════════════════

class PsychTest(models.Model):
    """Тест созданный психологом"""
    STATUS_CHOICES = [
        ('draft',  'Черновик'),
        ('active', 'Активен'),
        ('closed', 'Закрыт'),
    ]
    SOURCE_CHOICES = [
        ('manual', 'Конструктор'),
        ('ai',     'ИИ генерация'),
    ]
    TOPIC_CHOICES = [
        ('anxiety',    'Тревожность'),
        ('depression', 'Депрессия'),
        ('stress',     'Стресс'),
        ('selfesteem', 'Самооценка'),
        ('relations',  'Отношения'),
        ('bullying',   'Буллинг'),
        ('motivation', 'Мотивация'),
        ('other',      'Другое'),
    ]
    DIFFICULTY_CHOICES = [
        ('easy',   'Лёгкий'),
        ('medium', 'Средний'),
        ('hard',   'Сложный'),
    ]

    title        = models.CharField(max_length=200, verbose_name='Название')
    description  = models.TextField(blank=True, verbose_name='Описание')
    psychologist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='psych_tests')
    source       = models.CharField(max_length=10, choices=SOURCE_CHOICES, default='manual')
    topic        = models.CharField(max_length=20, choices=TOPIC_CHOICES, default='anxiety')
    difficulty   = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    status       = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    target_class = models.ForeignKey(SchoolClass, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_tests', verbose_name='Класс')
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Психологический тест'
        verbose_name_plural = 'Психологические тесты'

    def __str__(self):
        return self.title

    def question_count(self):
        return self.questions.count()

    def result_count(self):
        return self.results.count()


class PsychTestQuestion(models.Model):
    """Вопрос теста"""
    TYPE_CHOICES = [
        ('radio',    'Один вариант'),
        ('checkbox', 'Несколько вариантов'),
        ('scale',    'Шкала 1-5'),
        ('text',     'Открытый ответ'),
    ]
    test    = models.ForeignKey(PsychTest, on_delete=models.CASCADE, related_name='questions')
    text    = models.TextField(verbose_name='Текст вопроса')
    q_type  = models.CharField(max_length=10, choices=TYPE_CHOICES, default='radio')
    options = models.JSONField(default=list, blank=True, verbose_name='Варианты ответов')
    # Для radio/checkbox — список строк ["Никогда","Иногда","Часто","Всегда"]
    # Для scale — пустой список (1-5 автоматически)
    # Для text — пустой список
    weight  = models.IntegerField(default=1, verbose_name='Вес вопроса')
    order   = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Вопрос теста'
        verbose_name_plural = 'Вопросы теста'

    def __str__(self):
        return f"[{self.test.title}] {self.text[:60]}"


class PsychTestResult(models.Model):
    """Результат прохождения теста учеником"""
    RISK_CHOICES = [
        ('low',    'Низкий'),
        ('medium', 'Средний'),
        ('high',   'Высокий'),
    ]
    test      = models.ForeignKey(PsychTest, on_delete=models.CASCADE, related_name='results')
    student   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='psych_test_results')
    answers   = models.JSONField(default=dict, verbose_name='Ответы')
    # {question_id: answer_value}
    score     = models.IntegerField(default=0, verbose_name='Балл')
    max_score = models.IntegerField(default=0)
    risk_level = models.CharField(max_length=10, choices=RISK_CHOICES, default='low')
    ai_analysis  = models.TextField(blank=True, verbose_name='Анализ ИИ')
    psy_conclusion = models.TextField(blank=True, verbose_name='Заключение психолога')
    is_approved  = models.BooleanField(default=False, verbose_name='Утверждено')
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-completed_at']
        unique_together = ('test', 'student')
        verbose_name = 'Результат теста'
        verbose_name_plural = 'Результаты тестов'

    def __str__(self):
        return f"{self.student.get_full_name()} — {self.test.title}"

    def percent(self):
        if self.max_score == 0: return 0
        return round(self.score / self.max_score * 100)


# ══════════════════════════════════════════════════════════════
# ЦИКЛ ОБРАБОТКИ ЖАЛОБ
# ══════════════════════════════════════════════════════════════

class StudentRequest(models.Model):
    """
    Жалоба / запрос от авторизованного ученика.
    Центральная сущность цикла: ученик → ИИ → психолог → родитель.
    """

    # ── Категория обращения ──────────────────────────────────
    CATEGORY_CHOICES = [
        ('anxiety',  'Тревога / Стресс'),
        ('bullying', 'Буллинг'),
        ('family',   'Семейные проблемы'),
        ('study',    'Проблемы с учёбой'),
        ('behavior', 'Поведение'),
        ('relations','Отношения в классе'),
        ('other',    'Другое'),
    ]

    # ── Статус жизненного цикла ───────────────────────────────
    STATUS_CHOICES = [
        ('new',          'Новая'),          # только что отправлена
        ('ai_analyzed',  'ИИ проанализировал'),  # ai_summary заполнен
        ('in_review',    'На рассмотрении'), # психолог открыл кейс
        ('concluded',    'Заключение готово'),   # psy_conclusion заполнен
        ('archived',     'Архив'),           # закрыта / не требует действий
    ]

    # ── Уровень риска (заполняет ИИ, психолог может изменить) ──
    RISK_CHOICES = [
        ('low',    'Низкий'),
        ('medium', 'Средний'),
        ('high',   'Высокий'),
        ('critical', 'Критический'),
    ]

    # ── Тональность (заполняет ИИ) ────────────────────────────
    TONE_CHOICES = [
        ('neutral',    'Нейтральная'),
        ('anxiety',    'Тревожность'),
        ('depression', 'Подавленность'),
        ('aggression', 'Агрессия'),
        ('fear',       'Страх'),
        ('confusion',  'Растерянность'),
    ]

    # ── Основные поля ─────────────────────────────────────────
    student     = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='student_requests',
        verbose_name='Ученик'
    )
    category    = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES,
        default='other', verbose_name='Категория'
    )
    text        = models.TextField(verbose_name='Текст жалобы')
    is_anonymous = models.BooleanField(
        default=False,
        verbose_name='Скрыть имя от психолога',
        help_text='Психолог видит класс и возраст, но не имя'
    )
    status      = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='new', verbose_name='Статус'
    )
    lang        = models.CharField(
        max_length=5, default='ru',
        verbose_name='Язык обращения'
    )

    # ── ИИ-слой (заполняется автоматически) ──────────────────
    ai_tone       = models.CharField(
        max_length=20, choices=TONE_CHOICES,
        blank=True, default='', verbose_name='Тональность (ИИ)'
    )
    ai_risk_level = models.CharField(
        max_length=10, choices=RISK_CHOICES,
        blank=True, default='', verbose_name='Уровень риска (ИИ)'
    )
    ai_summary    = models.TextField(
        blank=True, verbose_name='Резюме для психолога (ИИ)'
    )
    ai_tags       = models.JSONField(
        default=list, blank=True,
        verbose_name='Теги ИИ',
        help_text='Список ключевых сигналов, например ["буллинг","изоляция"]'
    )
    ai_analyzed_at = models.DateTimeField(
        null=True, blank=True, verbose_name='Время анализа ИИ'
    )

    # ── Слой психолога ────────────────────────────────────────
    assigned_to   = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_requests',
        verbose_name='Назначен психолог'
    )
    psy_risk_override = models.CharField(
        max_length=10, choices=RISK_CHOICES,
        blank=True, default='',
        verbose_name='Уровень риска (психолог)',
        help_text='Если пусто — используется оценка ИИ'
    )
    psy_conclusion = models.TextField(
        blank=True, verbose_name='Заключение психолога'
    )
    psy_recommendations = models.TextField(
        blank=True, verbose_name='Рекомендации психолога'
    )
    is_approved    = models.BooleanField(
        default=False, verbose_name='Заключение утверждено'
    )
    approved_at    = models.DateTimeField(
        null=True, blank=True, verbose_name='Время утверждения'
    )

    # ── Слой родителя ─────────────────────────────────────────
    parent_message = models.TextField(
        blank=True,
        verbose_name='Сообщение для родителя',
        help_text='Эмпатичная версия заключения, сформированная ИИ или психологом'
    )
    parent_notified = models.BooleanField(
        default=False, verbose_name='Родитель уведомлён'
    )
    parent_notified_at = models.DateTimeField(
        null=True, blank=True, verbose_name='Время уведомления родителя'
    )

    # ── Служебные ─────────────────────────────────────────────
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Жалоба ученика'
        verbose_name_plural = 'Жалобы учеников'

    def __str__(self):
        name = '***' if self.is_anonymous else self.student.get_full_name() or self.student.username
        return f"[{self.get_status_display()}] {name} — {self.get_category_display()}"

    @property
    def effective_risk(self):
        """Финальный уровень риска: психолог имеет приоритет над ИИ."""
        return self.psy_risk_override or self.ai_risk_level or 'low'

    @property
    def is_high_risk(self):
        return self.effective_risk in ('high', 'critical')


class TeacherObservation(models.Model):
    """
    Поведенческий сигнал от учителя об ученике.
    Не привязан к жалобе — учитель может отправить независимо.
    Психолог видит эти сигналы как дополнительный контекст к кейсу.
    """

    # ── Тип наблюдения ────────────────────────────────────────
    CATEGORY_CHOICES = [
        ('withdrawal',       'Замкнутость / изоляция'),
        ('aggression',       'Агрессивное поведение'),
        ('mood_drop',        'Резкая смена настроения'),
        ('academic_decline', 'Резкое снижение успеваемости'),
        ('absence',          'Частые пропуски'),
        ('anxiety_signs',    'Признаки тревоги / страха'),
        ('peer_conflict',    'Конфликт с одноклассниками'),
        ('self_harm_risk',   'Признаки самоповреждения'),
        ('other',            'Другое'),
    ]

    # ── Срочность ─────────────────────────────────────────────
    URGENCY_CHOICES = [
        ('low',      'Низкая — для наблюдения'),
        ('medium',   'Средняя — требует внимания'),
        ('high',     'Высокая — нужна реакция'),
        ('critical', 'Критическая — немедленно'),
    ]

    # ── Основные поля ─────────────────────────────────────────
    teacher   = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='teacher_observations',
        verbose_name='Учитель'
    )
    student   = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='observations',
        verbose_name='Ученик'
    )
    category  = models.CharField(
        max_length=25, choices=CATEGORY_CHOICES,
        default='other', verbose_name='Тип наблюдения'
    )
    urgency   = models.CharField(
        max_length=10, choices=URGENCY_CHOICES,
        default='low', verbose_name='Срочность'
    )
    description = models.TextField(
        verbose_name='Описание наблюдения',
        help_text='Что именно изменилось в поведении, когда началось, контекст'
    )
    duration_days = models.PositiveSmallIntegerField(
        null=True, blank=True,
        verbose_name='Продолжительность (дней)',
        help_text='Сколько дней наблюдается изменение поведения'
    )

    # ── Связь с жалобой (опциональная) ───────────────────────
    linked_request = models.ForeignKey(
        StudentRequest, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='teacher_observations',
        verbose_name='Связанная жалоба'
    )

    # ── Слой психолога ────────────────────────────────────────
    is_reviewed  = models.BooleanField(
        default=False, verbose_name='Просмотрено психологом'
    )
    reviewed_by  = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='reviewed_observations',
        verbose_name='Просмотрел психолог'
    )
    reviewed_at  = models.DateTimeField(
        null=True, blank=True, verbose_name='Время просмотра'
    )
    psy_note     = models.TextField(
        blank=True,
        verbose_name='Заметка психолога по сигналу'
    )

    # ── Служебные ─────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Наблюдение учителя'
        verbose_name_plural = 'Наблюдения учителей'

    def __str__(self):
        return (
            f"[{self.get_urgency_display()}] "
            f"{self.teacher.get_full_name()} → "
            f"{self.student.get_full_name()} — "
            f"{self.get_category_display()}"
        )

    @property
    def is_critical(self):
        return self.urgency == 'critical'
