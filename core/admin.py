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
