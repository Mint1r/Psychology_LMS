import os, django, pytest
from accounts.models import User
from courses.models import Course,Lesson,Module



# Устанавливаем настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Psychology.settings')

# Инициализируем Django
django.setup()


@pytest.fixture
def user():
    return User.objects.create(
        phone_number = '+79533677788',
        email = 'mail@mail.ru'
        )