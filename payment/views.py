from django.shortcuts import redirect, get_object_or_404,render
from payment.models import UserPayments
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from payment.payment import set_course_access,verify_payment,create_smart_payment, PaymentCreationError, PaymentVerifyError
import logging,json
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from courses.models import Course
from django.urls import reverse
from progress.models import UserProgress
import uuid
payment_logger = logging.getLogger("payments")


@csrf_exempt
@require_POST
def payment_webhook(request):
    """
    Вебхук юкассы, обрабатывает данные о платеже, проводит верификацию.

    Выдает доступ пользователю при успешной верификации платежа.
    """
    try:
        event_json = json.loads(request.body.decode('utf-8'))
        event_type = event_json.get('event')
        payment_obj = event_json.get('object',{})
        payment_id = payment_obj.get('id')
        metadata = payment_obj.get('metadata',{}) or {}

        if not metadata:
            payment_logger.error(f"Платеж с provider_payment_id={payment_id} пришел без metadata")
            return HttpResponse(status=200) 

        user_id = metadata.get('user_id')
        course_id = metadata.get('course_id')

        if not user_id or not course_id:
            payment_logger.error(
                f"Платеж с provider_payment_id={payment_id} "
                f"пришел с неполной metadata"
            )
            return HttpResponse(status=200)

        if event_type == "payment.canceled":
            try:
                db_payment = UserPayments.objects.get(
                    user_id = user_id, 
                    course_id=course_id,
                    provider_payment_id = payment_id)
           
            except ObjectDoesNotExist:
                payment_logger.error(f"Платеж с provider_payment_id={payment_id} не найден в БД")
                return HttpResponse(status=200)    
            
            db_payment.status = "canceled"
            db_payment.save(update_fields=["status"])

            return HttpResponse(status=200)

        if event_type != "payment.succeeded":
            payment_logger.info(f"Webhook ignored: {event_type}")
            return HttpResponse(status=200)

        if not user_id or not course_id:
            payment_logger.error(f"Webhook без metadata ")
            return HttpResponse(status=200)

        if not payment_id:
            payment_logger.error(f"Webhook без payment_id")
            return HttpResponse(status=200)
        try:
           db_payment = UserPayments.objects.get(
               user_id = user_id, 
               course_id=course_id,
               provider_payment_id = payment_id)
           
        except ObjectDoesNotExist:
            payment_logger.error(f"Платеж с provider_payment_id={payment_id} не найден в БД")
            return HttpResponse(status=200)            

        if db_payment.status == 'access_granted':
            return HttpResponse(status=200)

        try:
            payment = verify_payment(payment_id,expected_user_id=db_payment.user_id,
                                 expected_course_id=db_payment.course_id,
                                 expected_amount=db_payment.amount)
        except PaymentVerifyError as e:
            payment_logger.error(f"Неизвестная ошибка ЮKassa : {db_payment.id} ")
            db_payment.status = 'verify_error'
            db_payment.save(update_fields=['status'])
            return HttpResponse(status=200)

        if not payment:
            db_payment.status = 'verify_error'
            db_payment.save(update_fields=['status'])
            payment_logger.error(f"Ошибка верификации платежа id : {db_payment.id} ")
            return HttpResponse(status=200)
        
        db_payment.status = 'paid'

        db_payment.provider_payment_id = payment_id
        db_payment.save(update_fields=['status'])

        if set_course_access(user_id=user_id,course_id=course_id):
            db_payment.status = 'access_granted'
            db_payment.save(update_fields=['status'])
        return HttpResponse(status=200)

    except Exception:
        payment_logger.exception(f"Ошибка обработки YooKassa webhook")
        return HttpResponse(status=400)


@login_required
def payment_complited(request, payment_id):
    """
    Страница отображает статус обработки платежа.
    """
    payment_obj = get_object_or_404(UserPayments,id = payment_id)

    data = {
        'payment' : payment_obj,
    }

    return render(request, 'payment_complited.html', data)

@login_required
def purchase(request,course_id):
    """
    Информация перед совершением покупки.
    """
    course = get_object_or_404(Course,id=course_id)
    if UserProgress.objects.filter(user = request.user, course = course).exists():
        return redirect('learn:learn_main')
    data={'course':course}
    return render(request, 'purchase.html',data)

@require_POST
@login_required
def purchase_redirect(request,course_id):
    """
    Редиректит пользователя на страницу юкассы и создает объект

    платежа в бд. При ошибках юкассы меняет статус платежу и выдает

    информацию пользователю.
    """
    payment_id = uuid.uuid4()

    return_url = request.build_absolute_uri(
        reverse('payment_complited',
            kwargs={'payment_id': payment_id})
    )

    course = get_object_or_404(Course, id=int(course_id))

    if not settings.PAYMENT: # для тестирования 
        set_course_access(user_id = request.user.id, 
                          course_id = course_id)
        return redirect('course', course_id)

    payment_db = UserPayments.objects.create(    
        id = payment_id,
        user = request.user, 
        course = course, 
        amount = course.price
        )

    try:
        payment_obj = create_smart_payment(course.price,return_url, 
                                       user_id = request.user.id,
                                       course_id = course_id)
    except PaymentCreationError:
        messages.error(
            request,
            "Не удалось создать платёж. Попробуйте ещё раз."
        )

        payment_db.status = 'creation_error'
        payment_db.save(update_fields=['status'])

        return redirect('course', course_id)
    
    payment_db.provider_payment_id = payment_obj['payment_id']
    payment_db.save(update_fields=['provider_payment_id'])

    redirect_url = payment_obj['confirmation_url']

    return redirect(redirect_url)
