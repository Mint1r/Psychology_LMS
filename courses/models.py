from django.utils.translation import gettext as _ 
from django.db import models
from accounts.storage import private_storage
from django.core.exceptions import ValidationError

class Lesson(models.Model):

    title = models.CharField(
        max_length=500,
        verbose_name=("Название")
        )
    
    video = models.FileField(
        storage=private_storage,
        upload_to="materials/lessons_video",
        blank=True, null=True,
        verbose_name=("Видеоурок")
            )
    
    has_video = models.BooleanField(
        default=False,
        verbose_name=("Наличие видео")
        )

    text_info = models.TextField(
        blank=True, 
        null=True, 
        verbose_name=("Введение")
        )

    test = models.CharField(
        max_length=500,
        verbose_name=("Ссылка на тест")
        ,blank=True, null=True,)

    description = models.TextField(
        verbose_name=("Описание"),
        blank=True, null=True,
        max_length=330,
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = ("Урок")
        verbose_name_plural = ("Уроки")

class LessonMaterials(models.Model):

    TYPE_CHOICES = [
        ("link", "Ссылка"),
        ("file", "Файл"),
    ]

    NECESSITY_CHOICES = [
        ("necessary", "Обязательный"),
        ("recommended", "Дополнительный"),
    ]

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="materials",
        verbose_name="Уроки",
    )

    material_type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        verbose_name="Тип материала",
    )

    necessity = models.CharField(
        max_length=20,
        choices=NECESSITY_CHOICES,
        verbose_name="Обязательность",
    )

    link = models.URLField(
        blank=True,
        verbose_name="Ссылка",
    )

    file = models.FileField(
        storage=private_storage,
        upload_to="materials/files",
        blank=True,
        verbose_name="Файл",
    )

    title = models.CharField(
        max_length=150,
        verbose_name="Название",
    )

    order = models.PositiveIntegerField(
        verbose_name="Порядковый номер",
    )

    def __str__(self):
        return self.title
    
    def clean(self):
        super().clean()

        if self.material_type == "link" and not self.link:
            raise ValidationError({
                "link": "Для материала типа «Ссылка» необходимо указать ссылку."
            })

        if self.material_type == "file" and not self.file:
            raise ValidationError({
                "file": "Для материала типа «Файл» необходимо загрузить файл."
            })

    class Meta:
        verbose_name = "Материал"
        verbose_name_plural = "Материалы"
        ordering = ["order"]


class Module(models.Model):

    title = models.CharField(
        verbose_name=("Название"),
    )

    lessons = models.ManyToManyField(
        Lesson,
        through='ModuleLesson',
        related_name='modules'
    )

    description = models.TextField(
        verbose_name=("Описание"),)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = ("Модуль")
        verbose_name_plural = ("Модули")


class Course(models.Model):
    title = models.CharField(
        verbose_name="Название",
    )

    image = models.ImageField(
        upload_to="materials/course_images",
        blank=True,
        null=True,
        verbose_name="Баннер",
    )

    modules = models.ManyToManyField(
        Module,
        through="CourseModule",
        related_name="courses",
        verbose_name="Модули",
    )

    short_description = models.TextField(
        verbose_name="Краткое описание",
        max_length=400,
    )

    description = models.TextField(
        verbose_name="Описание",
    )

    lenth = models.CharField(
        max_length=64,
        verbose_name="Продолжительность курса",
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Цена",
    )

    output = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Что вы получите",
    )

    def amount(self):
        length = 0

        for module in self.modules.all():
            length += module.lessons.count()

        return length

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

class CourseModule(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='course_modules',
        verbose_name=("Курс")
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        verbose_name=("Модуль"),
    )
    order = models.PositiveIntegerField(
        verbose_name=("Порядковый номер"),
                                        )

    class Meta:
        ordering = ['order']
        verbose_name = "Модули"
        verbose_name_plural = "Модули"
        unique_together = ('course', 'module')


class ModuleLesson(models.Model):
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='module_lessons'
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE
    )
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']
        unique_together = ('module', 'lesson')
        verbose_name = "Уроки"
        verbose_name_plural = "Уроки"




