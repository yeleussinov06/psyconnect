from django.utils import timezone
from datetime import timedelta

_URL_TO_ACTIVE = {
    'student_dashboard': 'dashboard',
    'parent_dashboard': 'dashboard',
    'teacher_dashboard': 'dashboard',
    'psychologist_dashboard': 'overview',
    'emotion_diary': 'emotions',
    'test_center': 'tests',
    'take_test': 'tests',
    'ai_chat': 'chat',
    'book_appointment': 'appointments',
    'my_appointments': 'appointments',
    'student_psych_tests': 'tests',
    'student_take_psych_test': 'tests',
    'student_psych_test_done': 'tests',
    'psychologist_appointments': 'appointments',
    'manage_schedule': 'schedule',
    'psych_test_list': 'tests',
    'psych_test_create': 'tests',
    'psych_test_detail': 'tests',
    'psych_test_result_detail': 'tests',
    'parent_book_appointment': 'book',
    'teacher_book_appointment': 'book',
    'articles': 'articles',
    'anonymous_support': 'anon',
    'profile': 'profile',
    'notifications': 'notifications',
    # Цикл обращений
    'student_new_request':             'requests',
    'teacher_new_observation':          'observe',
    'psychologist_requests_list':       'cases',
    'psychologist_request_detail':      'cases',
    'psychologist_observation_detail':  'cases',
    'parent_conclusion_view':           'conclusions',
}


def dashboard_data(request):
    if not request.user.is_authenticated:
        return {}

    try:
        profile = request.user.profile
        role = profile.role
    except Exception:
        return {}

    lang = request.session.get('lang', 'ru')

    url_name = getattr(getattr(request, 'resolver_match', None), 'url_name', '')
    active_section = _URL_TO_ACTIVE.get(url_name, '')

    # Panel-based dashboards: sidebar active state comes from ?panel= GET param
    if url_name == 'psychologist_dashboard':
        active_section = request.GET.get('panel', 'overview')
    elif url_name == 'teacher_dashboard':
        active_section = request.GET.get('panel', 'dashboard')

    ctx = {'active_section': active_section, 'lang': lang}

    try:
        ctx.update(_build_panel_ctx(request, role, lang))
    except Exception:
        pass

    return ctx


def _build_panel_ctx(request, role, lang):
    from .models import (
        SchoolClass, ParentStudent, EmotionEntry, TestResult,
        ChatMessage, Appointment, AnonymousRequest, Article, Notification,
        StudentRequest, TeacherObservation,
    )
    from django.contrib.auth.models import User

    ctx = {}
    today = timezone.now().date()

    def _class_sort_key(name):
        import re
        m = re.match(r'(\d+)', name or '')
        return (int(m.group(1)) if m else 999, name or '')

    if role == 'psychologist':
        ctx['student_count'] = User.objects.filter(profile__role='student').count()
        ctx['class_count'] = SchoolClass.objects.count()
        ctx['new_request_count'] = AnonymousRequest.objects.filter(status='new').count()
        ctx['next_confirmed_apt'] = Appointment.objects.filter(
            slot__psychologist=request.user,
            status='confirmed',
            slot__date__gte=today,
        ).select_related('slot', 'student').order_by('slot__date', 'slot__time_start').first()
        ctx['all_classes'] = sorted(SchoolClass.objects.all(), key=lambda c: _class_sort_key(c.name))
        ctx['search'] = ''
        ctx['class_filter'] = ''
        # Счётчик для бейджа в сайдбаре: новые + непросмотренные сигналы
        ctx['new_cases_count'] = (
            StudentRequest.objects.filter(status__in=['new', 'ai_analyzed']).count()
            + TeacherObservation.objects.filter(is_reviewed=False).count()
        )

    elif role == 'parent':
        import json as _json
        children = [lnk.student for lnk in
                    ParentStudent.objects.filter(parent=request.user).select_related('student')]
        ctx['parent_conclusions_count'] = Notification.objects.filter(
            user=request.user, notif_type='parent_conclusion', is_read=False
        ).count()
        score_map = {'happy': 5, 'calm': 4, 'tired': 3, 'sad': 2, 'anxious': 1, 'angry': 1}
        children_data = []
        for child in children:
            last_emotion = EmotionEntry.objects.filter(user=child).order_by('-created_at').first()
            sparkline = []
            for i in range(6, -1, -1):
                day = today - timedelta(days=i)
                e = EmotionEntry.objects.filter(user=child, created_at__date=day).order_by('-created_at').first()
                sparkline.append(score_map.get(e.emotion, 3) if e else None)
            children_data.append({
                'user': child,
                'last_emotion': last_emotion,
                'last_emotions': EmotionEntry.objects.filter(user=child).order_by('-created_at')[:5],
                'last_test': TestResult.objects.filter(user=child).order_by('-created_at').first(),
                'sparkline': _json.dumps(sparkline),
                'has_alert': bool(last_emotion and last_emotion.emotion in ['anxious', 'sad', 'angry']),
            })
        ctx['children_data'] = children_data
        ctx['articles'] = Article.objects.filter(audience='parent')[:6]
        ctx['notifications_count'] = Notification.objects.filter(user=request.user, is_read=False).count()

    elif role == 'student':
        # Optimised streak: one query for distinct diary dates, then count backwards
        from django.db.models.functions import TruncDate
        diary_dates = set(
            EmotionEntry.objects.filter(user=request.user)
            .annotate(d=TruncDate('created_at'))
            .values_list('d', flat=True)
            .distinct()
        )
        streak = 0
        check_day = today
        for _ in range(366):
            if check_day in diary_dates:
                streak += 1
                check_day -= timedelta(days=1)
            else:
                break
        ctx['emotion_count'] = EmotionEntry.objects.filter(user=request.user).count()
        ctx['test_count'] = TestResult.objects.filter(user=request.user).count()
        ctx['chat_count'] = ChatMessage.objects.filter(user=request.user).count()
        ctx['diary_streak'] = streak

    elif role == 'teacher':
        teacher_class = getattr(request.user.profile, 'school_class', None)
        if teacher_class:
            students = list(User.objects.filter(
                profile__role='student', profile__school_class=teacher_class
            ).select_related('profile__school_class')[:50])
            available_classes = [teacher_class]
        else:
            students = list(User.objects.filter(
                profile__role='student'
            ).select_related('profile__school_class')[:50])
            available_classes = sorted(SchoolClass.objects.all(), key=lambda c: _class_sort_key(c.name))

        student_ids = [u.id for u in students]
        em_keys = ['happy', 'calm', 'anxious', 'sad', 'angry', 'tired']
        em_stats = {k: EmotionEntry.objects.filter(
            emotion=k, user__id__in=student_ids,
            created_at__date__gte=today - timedelta(days=7)
        ).count() for k in em_keys}

        attention_flags = []
        for student in students:
            bad = EmotionEntry.objects.filter(
                user=student, emotion__in=['anxious', 'sad', 'angry'],
                created_at__date__gte=today - timedelta(days=7)
            ).count()
            if bad > 0:
                attention_flags.append({'user': student, 'count': bad})
        attention_flags.sort(key=lambda x: -x['count'])

        total_em = sum(em_stats.values())
        positive_em = em_stats.get('happy', 0) + em_stats.get('calm', 0)

        ctx['student_count'] = len(students)
        ctx['emotion_count'] = EmotionEntry.objects.filter(user__id__in=student_ids).count()
        ctx['test_count'] = TestResult.objects.filter(user__id__in=student_ids).count()
        ctx['teacher_class'] = teacher_class
        ctx['available_classes'] = available_classes
        ctx['class_filter'] = ''
        ctx['attention_flags'] = attention_flags[:3]
        ctx['class_climate'] = round(positive_em / total_em * 100) if total_em > 0 else 50

    return ctx
