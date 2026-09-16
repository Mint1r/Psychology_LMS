import uuid,logging
from yookassa import Payment
from yookassa.domain.exceptions import ApiError, NotFoundError
from progress.models import UserProgress, UserModulProgress,UserLessonProgress
from accounts.models import User
from courses.models import Course
from decimal import Decimal
payment_logger = logging.getLogger("payments")

class PaymentCreationError(Exception):
    """Ошибка при создании платежа."""
    pass

class PaymentVerifyError(Exception):
    """Ошибка при валидации платежа."""
    pass

def create_smart_payment(
        amount: str, return_url: str,
        user_id:str, course_id:str, 
        description: str = "Оплата заказа") -> dict:
    
    """Создает платеж в ЮKassa с флагом сохранения карты (Умный платёж).

    Возвращает словарь со ссылкой на оплату и ID платежа.
    """
    idempotence_key = str(uuid.uuid4())

    try:
        payment = Payment.create(
            {
                "amount": {
                    "value": amount,  
                    "currency": "RUB",
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": return_url,
                },
                "capture": True,
                "save_payment_method": True,  
                "description": description,
                "metadata":{
                    "user_id" : user_id,
                    "course_id" : course_id
                }
            },

            idempotence_key,
        )

        return {
            "confirmation_url": payment.confirmation.confirmation_url,
            "payment_id": payment.id,
        }

    except ApiError as e:
        payment_logger.warning(f"Ошибка ЮKassa: {e}")
        raise PaymentCreationError('Ошибка при создании платежа') from e

def set_course_access(user_id,course_id):
    """ Дает пользователю доступ к курсу """
    course = Course.objects.get(id=course_id)
    user=User.objects.get(id = user_id)
    course_modules = course.modules.all()
    for module in course_modules:
        lessons = module.lessons.all()
        for lesson in lessons:
            lesson_prog, created =UserLessonProgress.objects.get_or_create(lesson = lesson, user = user)
            lesson_prog.save()
        lesson_prog, created =UserModulProgress.objects.get_or_create(modul = module, user = user)
        lesson_prog.save()
    
    UserProgress.objects.get_or_create(
         user=user,
         course = course,)
    return True


def verify_payment(payment_id,expected_user_id,expected_course_id,expected_amount):
    """
    Проверяет платеж через API YooKassa
    Возвращает объект Payment или False.
    При ошибке вернет PaymentVerifyError.
    """
    try:
        payment = Payment.find_one(payment_id)

    except NotFoundError:
        payment_logger.warning(
            f'Платеж {payment_id}: не найден, неверный id'
            )
        return False
    
    except Exception as e:
        payment_logger.warning(
            f'Ошибка verify_payment {payment_id}: {e}'
            )
        raise PaymentVerifyError('Неизвестная ошибка YooKassa') from e

    if payment.status != "succeeded":
        payment_logger.warning(
            f'Платеж {payment_id}: неверный статус {payment.status}'
            )
        return False
    
    if not payment.paid:
        payment_logger.warning(
            f"Платеж {payment_id}: paid=False"
        )
        return False

    if Decimal(payment.amount.value) != Decimal(expected_amount):
        payment_logger.warning(
        f"Платеж {payment_id}: неверная сумма"
    )
        return False
    
    if payment.amount.currency != "RUB":
        payment_logger.warning(
            f"Платеж {payment_id}: неверная валюта"
        )
        return False
            
    metadata = payment.metadata or {}

    if metadata.get("user_id") != str(expected_user_id):
        payment_logger.warning(
            f"Платеж {payment_id}: user_id не совпадает"
        )
        return False

    if metadata.get("course_id") != str(expected_course_id):
        payment_logger.warning(
            f"Платеж {payment_id}: course_id не совпадает"
        )
        return False

    return payment