from django.shortcuts import redirect, get_object_or_404,render
from courses.models import Course
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from vkbot import services as bot
from .models import Documents
import logging
from progress.models import UserProgress
from django.contrib import messages
from django.conf import settings

payment_logger = logging.getLogger("payments")

def main(request):
    return render(request, 'main.html',)

def documents(request):
    docs = Documents.objects.all()
    data = {"data":docs}
    return render(request, 'docs_main.html',data)

def catolog(request):
    courses = Course.objects.all()
    data={
        'courses':courses
    }
    return render(request, 'catalog.html',data)

def course(request,course_id):
    has_course = False
    purchase_error = False
    
    for message in messages.get_messages(request):
        if message.tags == 'error':
            purchase_error = True

    course = get_object_or_404(Course,id=course_id)

    if request.user.is_authenticated:
        has_course = UserProgress.objects.filter(user = request.user, course = course).exists()

    data={
        'course':course,
        'has_course': has_course,
        'purchase_error': purchase_error
    }

    return render(request, 'about_course.html', data)

def info(request):
    return render(request, 'info.html')

def policy(request):
    return render(request, 'policy.html')


@require_POST
def cal_aply(request):
    user_name = request.POST.get('name')
    phone_number = request.POST.get('phone')

    if not all([user_name,phone_number]): 
        return JsonResponse({'error': 'Заполните все поля'}, status=400)
    
    user_id = settings.VK_ADMIN_ID

    text = f"📞 Новый заказ звонка!\n" \
        f"Имя пользователя: {user_name}\n" \
        f"Номер телефона: {phone_number}\n" \
        f"Пожалуйста, свяжитесь с клиентом как можно скорее."

    bot.send_vk_message(user_id=user_id,text=text)

    return redirect('main')


def bad_request(request, exception):
    return render(request, "error_page.html", status=400)


def permission_denied(request, exception):
    return render(request, "error_page.html", status=403)


def page_not_found(request, exception):
    return render(request, "error_page.html", status=404)


def server_error(request):
    return render(request, "error_page.html", status=500)