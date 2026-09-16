from django.core.mail import send_mail
from courses.models import CourseModule,Lesson
from progress.models import UserLessonProgress
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
                    "lesson": module_lesson,
                    'lesson_number':lesson_number,
                    "lesson_id":module_lesson.lesson_id
                    })
            else:
                flag = 1
                break

        if flag: break
    return lessons_dict



def update_user_course_progress(course, user_progress, user):

    """
    Обновляет UserProgress при прохождении урока.
    """

    user_progress.current_class += 1
    user_progress.save()

    lesson_all_cnt = UserLessonProgress.objects.filter(
        lesson__modules__courses=course,
        user=user,
    ).count()

    finished = UserLessonProgress.objects.filter(
        user=user,
        lesson__modules__courses=course,
        status="finished"
    ).count()


    if finished == lesson_all_cnt and user_progress.status != "finished":
        user_progress.status = "finished"
        user_progress.current_class = 1000
        user_progress.save()

        course_finish_aply(
            user.username,
            user.phon_number,
            course.title
        )

        return True


    lesson_progresses = {
        p.lesson_id: p
        for p in UserLessonProgress.objects.filter(user=user)
    }

    
    while True:
        lessons_dict = get_lessons_dict(
            course=course,
            user_progress=user_progress
        )

        if not lessons_dict:
            break

        lesson_id = lessons_dict[-1]["lesson_id"]
        progress = lesson_progresses.get(lesson_id)

        if not progress or progress.status != "finished":
            break

        user_progress.current_class += 1
        user_progress.save()
       

    return True




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



