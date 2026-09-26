from django.core.mail import send_mail
from courses.models import CourseModule
from Psychology import settings 
from vkbot import services as bot

def get_lessons_dict(course,user_progress):
    lesson_number,flag = 0,0
    lessons_dict = []
    modules = (
        CourseModule.objects
        .filter(course=course)
        .select_related("module")
        .prefetch_related("module__module_lessons__lesson")
        .order_by("order")
    )
    for module in modules:
        module_lessons=module.module.module_lessons.all()
        for module_lesson in module_lessons:
            lesson_number +=1
            if lesson_number <= user_progress.current_class:
                lessons_dict.append(
                    {"module_order":module.order,
                    "module_lesson": module_lesson,
                    'lesson_number':lesson_number,
                    "lesson_id":module_lesson.lesson_id
                    })
            else:
                flag = 1
                break

        if flag: break
    return lessons_dict


def send_email2(topic,text,emailDict):

    if not settings.EMAIL_MESSAGES:
        return 

    send_mail(
            topic,
            text,
            None,
            emailDict,
            fail_silently=False,
        )


def course_finish_aply(user_name,phone_number, course_title):

    if not settings.VK_MESSAGES:
        return 

    user_id = settings.VK_ADMIN_ID

    text = f"Пользователь закончил курс\n" \
        f"Имя пользователя: {user_name}\n" \
        f"Номер телефона: {phone_number}\n" \
        f"Курс: {course_title}\n" \
        f"Пожалуйста, свяжитесь с клиентом как можно скорее."

    bot.send_vk_message(user_id=user_id,text=text)



