from courses.models import CourseModule
from progress.models import UserLessonProgress,UserModulProgress
from django.db import transaction
from access.handlers import course_finish_aply

def get_course_structure(course):
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
            lessons_dict.append(
                {"module_lesson": module_lesson,
                "lesson_id":module_lesson.lesson_id,
                })
            
    return lessons_dict

def module_progress_update(user,current_class,lessons_dict ):
    current_module_lesson = lessons_dict[current_class - 1]['module_lesson']
    previous_module_lesson = lessons_dict[current_class - 2]['module_lesson']

    if current_module_lesson.module_id != previous_module_lesson.module_id:
        module_progress = UserModulProgress.objects.get(
            user=user,
            modul_id=previous_module_lesson.module_id
        )
        module_progress.status = 'finished'
        module_progress.save(update_fields=["status", "updated_at"])




@transaction.atomic
def update_user_course_progress(course, user_progress, user):

    """
    Обновляет UserProgress,UserModulProgress,UserLessonProgress при прохождении урока.
    """

    user_progress.current_class += 1

    lessons_dict = get_course_structure(course=course)
    all_course_lessons_cnt = len(lessons_dict)


    
    module_progress_update(
        user = user,
        current_class = user_progress.current_class,
        lessons_dict = lessons_dict)


    finished = UserLessonProgress.objects.filter(
        user=user,
        lesson__modules__courses=course,
        status="finished"
    ).count()


    if finished == all_course_lessons_cnt and user_progress.status != "finished":
        user_progress.status = "finished"
        user_progress.current_class = 1000
        user_progress.save(update_fields=["status", "updated_at",'current_class'])

        course_finish_aply(
            user.username,
            user.phon_number,
            course.title
        )

        return True


    lesson_progresses = {
        p.lesson_id: p
        for p in UserLessonProgress.objects
        .filter(user=user)
    }

    

    while True:    
        lesson_id = lessons_dict[user_progress.current_class - 1]['lesson_id']
        current_lesson = lessons_dict[user_progress.current_class - 1]['module_lesson']
        module_progress = UserModulProgress.objects.select_related('modul').get(
            user=user,
            modul_id=current_lesson.module_id
        )

        if user_progress.current_class > all_course_lessons_cnt :
            user_progress.status = "finished"
            user_progress.current_class = 1000

            course_finish_aply(
                user.username,
                user.phon_number,
                course.title
            )

            break

        if module_progress.status == 'finished':
            user_progress.current_class += module_progress.modul.lessons.count()
            continue
            
        if lesson_progresses.get(lesson_id).status == 'finished':
            user_progress.current_class += 1
            continue
        
        break

    module_progress.save(
    update_fields=['status', 'finished_at', 'updated_at']
    )
    user_progress.save(update_fields=["status", "updated_at",'current_class'])
    return True