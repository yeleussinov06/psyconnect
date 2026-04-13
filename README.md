# PsyConnect: Junior & Family

## 🚀 Запуск (3 команды)

```bash
cd psyconnect
pip install django
python manage.py migrate
python manage.py runserver
```

Открой: http://127.0.0.1:8000/

## 👤 Создать пользователей для теста

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from core.models import UserProfile

# Суперпользователь для /admin/
u = User.objects.create_superuser('admin', '', 'admin123')

# Ученик
u1 = User.objects.create_user('student1', password='pass123', first_name='Айгерим')
UserProfile.objects.create(user=u1, role='student')

# Родитель
u2 = User.objects.create_user('parent1', password='pass123', first_name='Назгуль')
UserProfile.objects.create(user=u2, role='parent')

# Психолог
u3 = User.objects.create_user('psych1', password='pass123', first_name='Нурсулу')
UserProfile.objects.create(user=u3, role='psychologist')

exit()
```

## 📌 URL-ы

| URL | Кто видит |
|-----|-----------|
| `/` | Лендинг / редирект |
| `/login/` | Все |
| `/register/` | Все |
| `/student/` | Ученик |
| `/emotions/` | Ученик — дневник эмоций |
| `/tests/` | Ученик — тесты |
| `/chat/` | Ученик — AI-чат |
| `/parent/` | Родитель |
| `/psychologist/` | Психолог |
| `/anonymous/` | Все (без регистрации) |
| `/admin/` | Суперпользователь |

## 🛠 Admin панель (/admin/)

Войди как `admin` / `admin123` — там управляй всем:
- Пользователи и профили
- Эмоции учеников
- Анонимные запросы
- Тесты и результаты
- Статьи для родителей
