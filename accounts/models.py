from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from courses.models import Lesson, Course
from .storage import private_storage
from django.utils import timezone

class User(AbstractUser):
    is_staff = models.BooleanField(
        verbose_name=("Статус персонала"),
        default=False
    )
    is_active = models.BooleanField(
        verbose_name=("Активный"),
        default=True
    )
    is_superuser = models.BooleanField(
        verbose_name=("суперпользователь"),
        default=False,
        help_text=('Указывает, что пользователь имеет все разрешения без их явного назначения.'),
    )

    phon_number = models.CharField(
        max_length=64, 
        unique=True, 
        verbose_name=("Номер телефона")
    )

    email = models.EmailField(
    max_length=254,
    unique=True
)

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",
        blank=True,
        help_text=("Группы, к которым принадлежит пользователь."),
        verbose_name=("группы"),
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_set",
        blank=True,
        help_text=("Конкретные разрешения для этого пользователя."),
        verbose_name=("разрешения пользователя"),
    )

    class Meta:
        verbose_name = ("пользователя")
        verbose_name_plural = ("Пользователи")

class UserDocuments(models.Model):
    
    """Модель для хранения документов пользователя"""
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Пользователь'
    )
    
    # Основные документы
    diploma = models.FileField(
        storage=private_storage,
        upload_to='documents/diploma/',
        verbose_name='Диплом об образовании'
    )
    
    passport_main = models.FileField(
        storage=private_storage,
        upload_to='documents/passport/',
        verbose_name='Паспорт (фото)'
    )
    
    passport_registration = models.FileField(
        storage=private_storage,
        upload_to='documents/passport/',
        verbose_name='Паспорт (прописка)'
    )
    
    snils = models.FileField(
        storage=private_storage,
        upload_to='documents/snils/',
        verbose_name='СНИЛС'
    )
    
    # Статус
    STATUS_CHOICES = [
        ('pending', 'Ожидает проверки'),
        ('approved', 'Проверено'),
        ('rejected', 'Отклонено'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    
    comment = models.TextField(
        verbose_name='Комментарий',
        blank=True
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата загрузки'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    class Meta:
        verbose_name = 'Документы пользователя'
        verbose_name_plural = 'Документы пользователей'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Документы {self.user.username}'
    
class UserTests(models.Model):

    """Модель для хранения тестов пользователя"""

    CANCELED = 'canceled'
    SUCSEED = 'sucseed'
    PROCESSING = "processing"

    STATUS_CHOICES= [
        (CANCELED, 'canceled'),
        (SUCSEED, 'sucseed'),
        (PROCESSING, "processing")
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='test_user',
        verbose_name='Пользователь',
        unique=False
    )

    lesson = models.ForeignKey(
        Lesson, 
        on_delete=models.CASCADE,
        related_name='test_lesson',
        verbose_name='Урок'
    )

    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE,
        related_name='test_course',
        verbose_name='Курс'
    )
    
    test_results = models.FileField(
        storage=private_storage,
        upload_to='tests/',
        verbose_name='Результаты теста'
    )

    status = models.CharField(
        verbose_name=("Статус"),
        choices=STATUS_CHOICES,
        default="processing"
    )
    
    rejection_reason = models.CharField(
        verbose_name=("Причина отказа"),
        blank=True,
        null=True,  
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата загрузки'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Тест пользователя'
        verbose_name_plural = 'Тесты пользователей'
