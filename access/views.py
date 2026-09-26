from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from accounts.models import UserDocuments,UserTests
from django.views.decorators.http import require_POST
from django.contrib.auth.models import Group
from progress.models import UserProgress,UserLessonProgress
from courses.models import Course,CourseModule,ModuleLesson,Lesson
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db import transaction
from access.handlers import get_lessons_dict, send_email2
from progress.services import update_user_course_progress

@login_required
def learn_main(request):
    progress = UserProgress.objects.filter(user=request.user)
    data={
        "progress2":progress
    }
    
    return render(request, 'learn_main.html',data)


@login_required
@never_cache
def learn_course(request,course_id):

    course = get_object_or_404(Course,pk=course_id)
    user_progres=get_object_or_404(UserProgress,user=request.user, course=course) 


    lessons_dict = get_lessons_dict(course,user_progres)

    data ={
        "lessons_dict":lessons_dict[::-1],
        "course":course,
        "progress":user_progres,
    }

    return render(request, 'learn_course.html',data)

@login_required
def learn_lesson(request,lesson_id,course_id):
    course = get_object_or_404(Course, pk=course_id)
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    lesson_progress = get_object_or_404(
        UserLessonProgress,
        user = request.user,
        lesson=lesson
        )
    
    module_lesson = ModuleLesson.objects.get(
        module__coursemodule__course=course,
        lesson=lesson,
    )

    module_course= CourseModule.objects.get(
        course=course,module=module_lesson.module_id)
    
    test = UserTests.objects.filter(user=request.user,lesson=lesson, course = course_id).first()  
    test_status = test.status if test else 0
    rejection_reason = test.rejection_reason if test else None
    video = lesson.video

    data={
        "course":course,
        "lesson":lesson,
        'video':video,
        "lesson_order":module_lesson.order,
        "module_order": module_course.order,
        "test_status":test_status,
        "test":test,
        "test_coment":rejection_reason,
        "lesson_status":lesson_progress.status,
    }

    return render(request, 'learn_lesson.html',data)


@login_required
def admin_panel(request):
    if not request.user.groups.filter(name='admin').exists():
        return HttpResponse(status=404)
    
    applications = UserDocuments.objects.filter(status="pending")
    tests = UserTests.objects.filter(status="processing")

    data ={
        "applications":applications,'tests':tests
    }

    return render(request, 'admin_panel.html',data)


@require_POST
@login_required
def applications(request):
    if not request.user.groups.filter(name='admin').exists():
        return HttpResponse(status=404)
    application_id = request.POST.get('application_id')
    if not application_id:
        return HttpResponse(status=400)
    application= get_object_or_404(UserDocuments,id=int(application_id))
    group = Group.objects.get(name='can_buy_courses')
    action = request.POST.get('action')  
    with transaction.atomic():
        if action == "accept":
            application.status ="approved"
            application.user.groups.add(group)
            
            text = 'Добрый день, ваши документы прошли проверку и вы можете продолжить покупку'
            topic = 'Проверка документов'
            transaction.on_commit( 
                lambda : send_email2(
                        topic = topic, 
                        text = text, 
                        emailDict = [application.user.email])
                        )
        else:
            application.status ="rejected"
            text = 'Добрый день, ваши документы не прошли проверку, попробуйте прикрепить их снова.'
            topic = 'Проверка документов'
            transaction.on_commit( 
                lambda : send_email2(
                        topic = topic, 
                      text = text, 
                        emailDict = [application.user.email])
                        )
        application.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))


@require_POST
@login_required
def load_test(request, course_id, lesson_id):
    lesson = get_object_or_404(Lesson, id = lesson_id)
    course = get_object_or_404(Course, id = course_id)
    
    test_file = request.FILES.get('test_file')
    
    if not test_file:
        messages.info(request, f"Нет файла")
        return redirect('learn:learn_lesson',course_id, lesson_id)
    
    test = UserTests.objects.create(
        user=request.user,
        test_results = test_file,
        lesson = lesson,
        course = course
    )

    return redirect('learn:learn_course', course_id)



@require_POST
@login_required
def test_decision(request):
    if not request.user.groups.filter(name='admin').exists():
        return HttpResponse(status=400)
    
    test_id = request.POST.get('test_id')

    if not test_id:
        return HttpResponse(status=400)
    
    comment = request.POST.get('comment')

    test = get_object_or_404(UserTests, id = test_id)
    student = test.user
    lesson_progres = get_object_or_404(UserLessonProgress, user=student, lesson = test.lesson)
    user_progress = get_object_or_404(UserProgress, user=student, course = test.course)
    
    action = request.POST.get('action')  

    with transaction.atomic():
        if action == "accept":

            test.status = "sucseed"
            lesson_progres.status = "finished"
            text = 'Добрый день, поздравялем со сдачей теста!'
            topic = 'Проверка теста'
            transaction.on_commit( 
                lambda : send_email2(
                        topic = topic, 
                        text = text, 
                        emailDict = [student.email])
                        )
            lesson_progres.save(update_fields=["status", "updated_at"])
            update_user_course_progress(
                course = test.course,
                user_progress = user_progress,
                user = student
            )

        else:
            test.status ="canceled"
            test.rejection_reason = comment
            text = 'Добрый день, к сожалению, вы не прошли тест, обязательно попробуйте снова.'
            topic = 'Проверка теста'
            transaction.on_commit( 
                lambda : send_email2(
                        topic = topic, 
                        text = text, 
                        emailDict = [student.email])
                        )
            
        test.test_results.delete(save=False) 
        test.save(update_fields=["status", "rejection_reason"])

    return redirect(request.META.get('HTTP_REFERER', '/'))
    

@require_POST
@login_required
def complit_lesson(request,course_id,lesson_id):
    lesson = get_object_or_404(Lesson, id = lesson_id)
    course = get_object_or_404(Course, id = course_id)
    lesson_progres = get_object_or_404(
        UserLessonProgress,
        user=request.user,
        lesson=lesson,
        )
    user_progress = get_object_or_404(
        UserProgress,
        user=request.user,
        course=course_id,
        )
    
    lesson_progres.status = "finished"
    lesson_progres.save(update_fields=["status", "updated_at", 'finished_at'])

    update_user_course_progress(
        course = course,
        user_progress = user_progress,
        user = request.user
        )
    
    return redirect('learn:learn_lesson',course_id,lesson_id )


