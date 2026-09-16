from django.db import models
from accounts.models import User
from courses.models import Course,Lesson,Module

class UserProgress(models.Model):
    """Модель для хранения прогресса по курсам пользователя"""
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='lesson_progres_us',
        verbose_name='Пользователь'
    )

    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE,
        related_name='course_progress',
        verbose_name='Курс'
    )
    
    
    STATUS_CHOICES = [
        ('started', 'Начат'),
        ('finished', 'Закончен'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='started',
        verbose_name='Статус'
    )

    finished_at = models.DateTimeField(
        verbose_name='Дата окончания',
        blank=True,
        null=True,
    )
    
    current_class = models.IntegerField(
        verbose_name='Текущий урок',
        default=1
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата начала'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    class Meta:
        verbose_name = 'Доступ к курсам'
        verbose_name_plural = 'Доступ к курсам'
        ordering = ['-created_at']
    
    def percent(self):
        now = self.current_class -1
        all = self.course.amount()
        if self.status == "finished":
            return  100
        return  int((now / all) * 100)

    def __str__(self):
        return f'Пользователь {self.user.username}'
    

class UserLessonProgress(models.Model):
    """Модель для хранения информации о уроках пройденых пользователем """
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='user_module_progress',
        verbose_name='Пользователь'
    )

    lesson = models.ForeignKey(
        Lesson, 
        on_delete=models.CASCADE,
        related_name='lesson_progress',
        verbose_name='Урок'
    )
    
    
    STATUS_CHOICES = [
        ('started', 'Начат'),
        ('finished', 'Закончен'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='started',
        verbose_name='Статус'
    )

    finished_at = models.DateTimeField(
        verbose_name='Дата окончания',
        blank=True,
        null=True,
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата начала'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    class Meta:
        verbose_name = 'Прохождение урока'
        verbose_name_plural = 'Прохождение урока'
        ordering = ['-created_at']

    def __str__(self):
        return f'Пользователь {self.user.username}'

class UserModulProgress(models.Model):
    """Модель для хранения информации о модулях пройденых пользователем """
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='progress',
        verbose_name='Пользователь'
    )

    modul = models.ForeignKey(
        Module, 
        on_delete=models.CASCADE,
        related_name='modul_progress',
        verbose_name='Модуль'
    )
    
    
    STATUS_CHOICES = [
        ('started', 'Начат'),
        ('finished', 'Закончен'),
        ('waiting', 'Не начат'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='waiting',
        verbose_name='Статус'
    )

    finished_at = models.DateTimeField(
        verbose_name='Дата окончания',
        blank=True,
        null=True,
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата начала'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    class Meta:
        verbose_name = 'Прогресс модулей'
        verbose_name_plural = 'Прогресс модулей'
        ordering = ['-created_at']

    def __str__(self):
        return f'Пользователь {self.user.username}'