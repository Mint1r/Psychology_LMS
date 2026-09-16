from django.db import models
from courses.models import Course
from accounts.models import User
import uuid 

class UserPayments(models.Model):
    """Модель для хранения платежей пользователей"""

    CANCELED = 'canceled'
    PAID = 'paid'
    PROCESSING = 'processing'
    COMPLITED = 'access_granted'
    CREATION_FAILED = 'creation_error'
    VERIFY_ERROR = 'verify_error'


    STATUS_CHOICES = [
        (CANCELED, 'Отменён'),
        (PAID, 'Оплачен'),
        (PROCESSING, 'В обработке'),
        (COMPLITED, 'Доступ предоставлен'),
        (CREATION_FAILED, 'Ошибка создания платежа'),
        (VERIFY_ERROR, 'Ошибка верификации платежа'),
    ]

    id = models.UUIDField(
        primary_key=True,
        editable=False
    )

    status = models.CharField(
        max_length=20,
        verbose_name='Статус',
        choices=STATUS_CHOICES,
        default=PROCESSING,
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_payments',
        verbose_name='Пользователь',
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name='Курс',
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Сумма',
    )

    provider_payment_id = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        verbose_name='ID платежа в платёжной системе',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления',
    )

    def __str__(self):
        return f'{self.user} — {self.course} — {self.amount} ₽'

    class Meta:
        verbose_name = 'Платёж пользователя'
        verbose_name_plural = 'Платежи пользователей'
        ordering = ['-created_at']



