from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import SchoolClass, UserProfile, ParentStudent, EmotionEntry, TestResult, ChatMessage, AnonymousRequest, Article


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'get_teacher', 'get_student_count', 'created_at']
    search_fields = ['name']

    def get_teacher(self, obj):
        t = obj.members.filter(role='teacher').first()
        return t.user.get_full_name() if t else '—'
    get_teacher.short_description = 'Учитель'

    def get_student_count(self, obj):
        return obj.members.filter(role='student').count()
    get_student_count.short_description = 'Учеников'


@admin.register(ParentStudent)
class ParentStudentAdmin(admin.ModelAdmin):
    list_display = ['parent', 'student', 'created_at']
    search_fields = ['parent__username', 'parent__first_name', 'student__username', 'student__first_name']
    autocomplete_fields = ['parent', 'student']


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль'
    fields = ['role', 'school_class', 'phone', 'bio']


class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = ['username', 'first_name', 'last_name', 'get_role', 'get_class', 'date_joined']
    search_fields = ['username', 'first_name', 'last_name']

    def get_role(self, obj):
        try: return obj.profile.get_role_display()
        except: return '—'
    get_role.short_description = 'Роль'

    def get_class(self, obj):
        try: return obj.profile.school_class or '—'
        except: return '—'
    get_class.short_description = 'Класс'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(EmotionEntry)
class EmotionEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'emotion', 'note', 'created_at']
    list_filter = ['emotion', 'created_at']
    search_fields = ['user__username', 'user__first_name']
    date_hierarchy = 'created_at'


@admin.register(AnonymousRequest)
class AnonymousRequestAdmin(admin.ModelAdmin):
    list_display = ['short_message', 'status', 'created_at']
    list_filter = ['status']
    list_editable = ['status']

    def short_message(self, obj):
        return obj.message[:60] + '...' if len(obj.message) > 60 else obj.message
    short_message.short_description = 'Сообщение'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title_ru', 'audience', 'created_at']
    list_filter = ['audience']


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'score', 'max_score', 'created_at']
    list_filter = ['category']


admin.site.register(ChatMessage)

admin.site.site_header = 'PsyConnect — Администрирование'
admin.site.site_title = 'PsyConnect'
admin.site.index_title = 'Панель управления'


# ── Добавляем кнопку импорта в admin ──────────────────────────
from django.contrib.admin import AdminSite
from django.urls import path as urlpath
from django.shortcuts import redirect

class PsyConnectAdminSite(AdminSite):
    site_header = 'PsyConnect — Администрирование'
    site_title = 'PsyConnect'
    index_title = 'Панель управления'

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            urlpath('import-users/', self.admin_view(self.import_users_view), name='import_users'),
        ]
        return custom + urls

    def import_users_view(self, request):
        return redirect('/admin-tools/import/')

    def each_context(self, request):
        ctx = super().each_context(request)
        ctx['import_url'] = '/admin-tools/import/'
        return ctx


from .models import PsychologistSchedule, Appointment

@admin.register(PsychologistSchedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['psychologist', 'date', 'time_start', 'time_end', 'is_available']
    list_filter  = ['is_available', 'date', 'psychologist']
    list_editable = ['is_available']
    date_hierarchy = 'date'

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display  = ['student', 'get_psychologist', 'get_date', 'get_time', 'reason', 'status', 'created_at']
    list_filter   = ['status', 'reason']
    list_editable = ['status']

    def get_psychologist(self, obj): return obj.slot.psychologist.get_full_name()
    get_psychologist.short_description = 'Психолог'

    def get_date(self, obj): return obj.slot.date
    get_date.short_description = 'Дата'

    def get_time(self, obj): return f"{obj.slot.time_start}-{obj.slot.time_end}"
    get_time.short_description = 'Время'

from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notif_type', 'is_read', 'created_at']
    list_filter  = ['notif_type', 'is_read']
    list_editable = ['is_read']


from .models import StudentRequest, TeacherObservation

@admin.register(StudentRequest)
class StudentRequestAdmin(admin.ModelAdmin):
    list_display  = [
        'student_display', 'category', 'status',
        'ai_risk_level', 'effective_risk_display',
        'is_approved', 'assigned_to', 'created_at',
    ]
    list_filter   = ['status', 'category', 'ai_risk_level', 'psy_risk_override', 'is_approved', 'lang']
    search_fields = ['student__username', 'student__first_name', 'student__last_name', 'text']
    readonly_fields = [
        'ai_tone', 'ai_risk_level', 'ai_summary', 'ai_tags', 'ai_analyzed_at',
        'approved_at', 'parent_notified_at', 'created_at', 'updated_at',
    ]
    date_hierarchy = 'created_at'
    fieldsets = [
        ('Ученик', {'fields': ['student', 'category', 'text', 'is_anonymous', 'lang', 'status']}),
        ('ИИ-анализ', {'fields': ['ai_tone', 'ai_risk_level', 'ai_summary', 'ai_tags', 'ai_analyzed_at'], 'classes': ['collapse']}),
        ('Психолог', {'fields': ['assigned_to', 'psy_risk_override', 'psy_conclusion', 'psy_recommendations', 'is_approved', 'approved_at']}),
        ('Родитель', {'fields': ['parent_message', 'parent_notified', 'parent_notified_at']}),
        ('Служебное', {'fields': ['created_at', 'updated_at'], 'classes': ['collapse']}),
    ]

    def student_display(self, obj):
        return '***' if obj.is_anonymous else obj.student.get_full_name() or obj.student.username
    student_display.short_description = 'Ученик'

    def effective_risk_display(self, obj):
        labels = {'low': 'Низкий', 'medium': 'Средний', 'high': 'Высокий', 'critical': '⚠ Критический'}
        return labels.get(obj.effective_risk, '—')
    effective_risk_display.short_description = 'Финальный риск'


@admin.register(TeacherObservation)
class TeacherObservationAdmin(admin.ModelAdmin):
    list_display  = [
        'teacher', 'student', 'category', 'urgency',
        'duration_days', 'is_reviewed', 'linked_request', 'created_at',
    ]
    list_filter   = ['urgency', 'category', 'is_reviewed']
    search_fields = [
        'teacher__username', 'teacher__first_name',
        'student__username', 'student__first_name', 'description',
    ]
    readonly_fields = ['reviewed_at', 'created_at', 'updated_at']
    raw_id_fields   = ['linked_request']
    date_hierarchy  = 'created_at'
    fieldsets = [
        ('Сигнал', {'fields': ['teacher', 'student', 'category', 'urgency', 'description', 'duration_days']}),
        ('Связь', {'fields': ['linked_request']}),
        ('Психолог', {'fields': ['is_reviewed', 'reviewed_by', 'reviewed_at', 'psy_note']}),
        ('Служебное', {'fields': ['created_at', 'updated_at'], 'classes': ['collapse']}),
    ]
