
from payment.payment import create_smart_payment,verify_payment
from unittest.mock import Mock, patch
from decimal import Decimal
from payment.payment import PaymentCreationError, PaymentVerifyError
import pytest
from yookassa.domain.exceptions import ApiError, NotFoundError

def test_create_smart_payment_sucseed():
    # Arrange
    payment = Mock()
    payment.id = "payment_123"
    payment.confirmation.confirmation_url = "https://yookassa.ru/checkout/payment_123"

    with patch('payment.payment.Payment') as MockPayment:
        MockPayment.create.return_value = payment

    # Act
        result = create_smart_payment(
            amount="1500.00",
            return_url="https://example.com/success",
            user_id="10",
            course_id="25",
            description="Оплата курса",
        )

        assert result == {
            "confirmation_url": "https://yookassa.ru/checkout/payment_123",
            "payment_id": "payment_123",
        }

        MockPayment.create.assert_called_once()

        payload, idempotence_key = MockPayment.create.call_args.args

    assert payload == {
        "amount": {
            "value": "1500.00",
            "currency": "RUB",
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://example.com/success",
        },
        "capture": True,
        "save_payment_method": True,
        "description": "Оплата курса",
        "metadata": {
            "user_id": "10",
            "course_id": "25",
        },
    }

def test_create_smart_payment_ycassa_error():
    with patch("payment.payment.Payment") as PaymentMock:
        original_error = ApiError({})

        PaymentMock.create.side_effect = original_error

        with pytest.raises(PaymentCreationError) as exc_info:
            create_smart_payment(
                amount="1500.00",
                return_url="https://example.com/success",
                user_id="10",
                course_id="25",
                description="Оплата курса",
            )

    assert str(exc_info.value) == "Ошибка при создании платежа"
    assert exc_info.value.__cause__ is original_error


def test_verify_payment_sucseed():
    payment = Mock()
    payment.status = "succeeded"
    payment.paid = True
    payment.amount = Mock()
    payment.amount.value = "1500.00"
    payment.amount.currency = "RUB"
    payment.metadata = {'user_id':'1234', 'course_id':'1234'}

    with patch('payment.payment.Payment') as PaymentMock:
        PaymentMock.find_one.return_value = payment

        result = verify_payment(payment_id='1234',
                       expected_user_id='1234',
                       expected_course_id='1234',
                       expected_amount=Decimal('1500.00'))

        PaymentMock.find_one.assert_called_once()

        assert result == payment

        payment_id = PaymentMock.find_one.call_args.args
    assert payment_id[0] == '1234'


def test_verify_payment_wrong_amount():
    payment = Mock()
    payment.status = "succeeded"
    payment.paid = True
    payment.amount = Mock()
    payment.amount.value = "1600.00"
    payment.amount.currency = "RUB"
    payment.metadata = {'user_id':'1234', 'course_id':'1234'}

    with patch('payment.payment.Payment') as PaymentMock:
        PaymentMock.find_one.return_value = payment

        result = verify_payment(payment_id='1234',
                       expected_user_id='1234',
                       expected_course_id='1234',
                       expected_amount=Decimal('1500.00'))

        PaymentMock.find_one.assert_called_once()

        assert result == False

        payment_id = PaymentMock.find_one.call_args.args
    assert payment_id[0] == '1234'

def test_verify_payment_wrong_course_id():
    payment = Mock()
    payment.status = "succeeded"
    payment.paid = True
    payment.amount = Mock()
    payment.amount.value = "1500.00"
    payment.amount.currency = "RUB"
    payment.metadata = {'user_id':'1234', 'course_id':'1234'}

    with patch('payment.payment.Payment') as PaymentMock:
        PaymentMock.find_one.return_value = payment

        result = verify_payment(payment_id='1234',
                       expected_user_id='1234',
                       expected_course_id='12345',
                       expected_amount=Decimal('1500.00'))

        PaymentMock.find_one.assert_called_once()

        assert result == False

        payment_id = PaymentMock.find_one.call_args.args
    assert payment_id[0] == '1234'

def test_verify_payment_wrong_payment_id():

    with patch('payment.payment.Payment') as PaymentMock:
        error = NotFoundError({})
        PaymentMock.find_one.side_effect = error

        result = verify_payment(payment_id='1234',
                    expected_user_id='1234',
                    expected_course_id='12345',
                    expected_amount=Decimal('1500.00'))

        PaymentMock.find_one.assert_called_once()
        assert result == False

        payment_id = PaymentMock.find_one.call_args.args
    assert payment_id[0] == '1234'

def test_verify_payment_wrong_status():
    payment = Mock()
    payment.status = "canceled"
    payment.paid = True
    payment.amount = Mock()
    payment.amount.value = "1500.00"
    payment.amount.currency = "RUB"
    payment.metadata = {'user_id':'1234', 'course_id':'1234'}

    with patch('payment.payment.Payment') as PaymentMock:
        PaymentMock.find_one.return_value = payment

        result = verify_payment(payment_id='1234',
                       expected_user_id='1234',
                       expected_course_id='1234',
                       expected_amount=Decimal('1500.00'))

        PaymentMock.find_one.assert_called_once()

        assert result == False

        payment_id = PaymentMock.find_one.call_args.args
    assert payment_id[0] == '1234'