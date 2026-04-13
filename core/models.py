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
