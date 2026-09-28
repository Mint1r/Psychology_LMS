from django.db import models
from courses.models import Course
from accounts.models import User

class CourseAccess(models.Model):
    
    class Status(models.TextChoices):
        ACTIVE = "active", "Активен"
        INACTIVE = "inactive", "Неактивен"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="course_accesses",
        verbose_name="Пользователь",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="user_accesses",
        verbose_name="Курс",
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Статус",
    )

    granted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата выдачи доступа",
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата окончания доступа",
    )

    class Meta:
        verbose_name = "Доступ к курсу"
        verbose_name_plural = "Доступы к курсам"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"],
                name="unique_user_course_access",
            ),
        ]

    def __str__(self):
        return f"{self.user} → {self.course} ({self.status})"