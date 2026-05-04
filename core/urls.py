from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('landing/', views.landing, name='landing'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('lang/<str:lang>/', views.set_language, name='set_language'),

    # Student
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('emotions/', views.emotion_diary, name='emotion_diary'),
    path('tests/', views.test_center, name='test_center'),
    path('tests/<str:category>/', views.take_test, name='take_test'),
    path('chat/', views.ai_chat_view, name='ai_chat'),
    path('api/chat/', views.ai_chat_api, name='ai_chat_api'),

    # Parent
    path('parent/', views.parent_dashboard, name='parent_dashboard'),
    path('parent/book/', views.parent_book_appointment, name='parent_book_appointment'),
    path('articles/', views.articles_view, name='articles'),

    # Psychologist
    path('psychologist/', views.psychologist_dashboard, name='psychologist_dashboard'),
    path('psychologist/respond/<int:req_id>/', views.respond_to_request, name='respond_to_request'),

    # Teacher
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/book/', views.teacher_book_appointment, name='teacher_book_appointment'),

    # Appointments
    path('book/', views.book_appointment, name='book_appointment'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('psychologist/appointments/', views.psychologist_appointments, name='psychologist_appointments'),
    path('psychologist/schedule/', views.manage_schedule, name='manage_schedule'),

    # Admin tools
    path('admin-tools/import/', views.admin_import_view, name='admin_import'),
    path('admin-tools/import/template/', views.download_import_template, name='download_import_template'),
    path('admin-tools/import/result/', views.download_import_result, name='download_import_result'),

    # Notifications
    path('notifications/', views.notifications_view, name='notifications'),
    path('api/notifications/count/', views.notifications_count, name='notifications_count'),

    # Public
    path('anonymous/', views.anonymous_support, name='anonymous_support'),
    path('profile/', views.profile_view, name='profile'),

    # Psychologist Test Center
    path('psychologist/tests/', views.psych_test_list, name='psych_test_list'),
    path('psychologist/tests/create/', views.psych_test_create, name='psych_test_create'),
    path('psychologist/tests/<int:test_id>/', views.psych_test_detail, name='psych_test_detail'),
    path('psychologist/tests/<int:test_id>/delete/', views.psych_test_delete, name='psych_test_delete'),
    path('psychologist/tests/results/<int:result_id>/', views.psych_test_result_detail, name='psych_test_result_detail'),

    # Student Psych Tests
    path('student/psych-tests/', views.student_psych_tests, name='student_psych_tests'),
    path('student/psych-tests/<int:test_id>/', views.student_take_psych_test, name='student_take_psych_test'),
    path('student/psych-tests/<int:test_id>/done/', views.student_psych_test_done, name='student_psych_test_done'),

    # Цикл обращений — Шаг 1
    path('student/requests/new/', views.student_new_request, name='student_new_request'),
    path('teacher/observe/', views.teacher_new_observation, name='teacher_new_observation'),

    # Цикл обращений — Шаг 3: кейсы психолога
    path('psychologist/requests/', views.psychologist_requests_list, name='psychologist_requests_list'),
    path('psychologist/requests/<int:req_id>/', views.psychologist_request_detail, name='psychologist_request_detail'),
    path('psychologist/observations/<int:obs_id>/', views.psychologist_observation_detail, name='psychologist_observation_detail'),

    # Цикл обращений — Шаг 4: заключение для родителя
    path('parent/conclusions/<int:req_id>/', views.parent_conclusion_view, name='parent_conclusion_view'),
]
