from django.db import models

# Create your models here.
class Documents(models.Model):

    STATUS_CHOICES = [
        ("structure", "Структура"),
        ("local", "Локальные"),
    ]
    
    link = models.CharField(
        verbose_name=("Ссылка на документ"),
    )

    title = models.CharField(
        verbose_name=("Название документа"),
    )

    status = models.CharField(
        choices=STATUS_CHOICES,
        verbose_name=("Вид"),
        default='local'
    )

    class Meta:
        verbose_name = 'Документы'
        verbose_name_plural = 'Документы'


