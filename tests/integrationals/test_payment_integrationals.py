from payment.payment import create_smart_payment,verify_payment
from unittest.mock import Mock, patch
from decimal import Decimal
from payment.payment import PaymentCreationError, PaymentVerifyError
from payment.models import UserPayments
from progress.models import UserProgress
import pytest, json
from courses.models import Course
from yookassa.domain.exceptions import ApiError, NotFoundError
from django.urls import reverse
from django.contrib.messages import get_messages

# def test_create_smart_payment_sucseed():
#     mock_payment = Mock()
#     mock_payment.id = "test-payment-id"
#     mock_payment.confirmation.confirmation_url = "http://test-payment"

#     with patch("payment.payment.Payment", return_value=mock_payment) as mock_Payment:
#         result = create_smart_payment(
#             amount="1500.00",
#             return_url="https://example.com/success",
#             user_id="10",
#             course_id="25",
#             description="Оплата курса",
#         )

#     assert result["payment_id"] == "test-payment-id"
#     assert result["confirmation_url"] == "http://test-payment"

#     mock_Payment.assert_called_once()

@pytest.mark.django_db
def test_payment_smart_payment_error(client, user):
    client.force_login(user)

    course = Course.objects.create(
        title="Course 1",
        price = Decimal(300),
    )

    with patch("payment.views.create_smart_payment") as mock_smart_payment:
        mock_smart_payment.side_effect = PaymentCreationError('')
        response = client.post(
        reverse("purchase_redirect",
                kwargs={'course_id':course.id}),
        data = {},
        HTTP_REFERER="/some-page/",
        )

    assert response.status_code == 302

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1

    db_payment = UserPayments.objects.get(
        user=user,
        course=course,
        )

    assert not db_payment.provider_payment_id
    assert db_payment.status == 'creation_error'


@pytest.mark.django_db
def test_payment_sucseed(client, user):
    client.force_login(user)

    course = Course.objects.create(
        title="Course 1",
        price = Decimal(300),
    )

    with patch("payment.views.create_smart_payment",) as mock_create:
        mock_create.return_value = {
                "payment_id": "test-payment-id",
                "confirmation_url": "http://test-payment",
            }
        response = client.post(
        reverse("purchase_redirect",
                kwargs={'course_id':course.id}),
        data = {},
        HTTP_REFERER="/some-page/",
        )

    assert response.status_code == 302

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 0

    db_payment = UserPayments.objects.get(
        user=user,
        course=course,
        )

    webhook_payload = {
        "type": "notification",
        "event": "payment.succeeded",
        "object": {
            "id": str(db_payment.provider_payment_id),
            "status": "succeeded",
            "amount": {
                "value": str(db_payment.amount),
                "currency": "RUB",
            },
            "metadata": {
                "user_id": str(user.id),
                "course_id": str(course.id),
            },
        },
    }

    with patch("payment.views.verify_payment", return_value=True) as mock_verify:
        response = client.post(
            reverse("payment_webhook"),
            data=json.dumps(webhook_payload),
            content_type="application/json",
        )


        assert response.status_code == 200

        mock_verify.assert_called_once_with(
            str(db_payment.provider_payment_id),
            expected_user_id=user.id,
            expected_course_id=course.id,
            expected_amount=db_payment.amount,
        )

    db_payment.refresh_from_db()

    assert db_payment.status == 'access_granted'
    assert UserProgress.objects.get(user=user,course = course)


@pytest.mark.django_db
def test_payment_canceled(client, user):
    client.force_login(user)

    course = Course.objects.create(
        title="Course 1",
        price = Decimal(300),
    )

    with patch("payment.views.create_smart_payment",) as mock_create:
        mock_create.return_value = {
                "payment_id": "test-payment-id",
                "confirmation_url": "http://test-payment",
            }
        response = client.post(
        reverse("purchase_redirect",
                kwargs={'course_id':course.id}),
        data = {},
        HTTP_REFERER="/some-page/",
        )

    assert response.status_code == 302

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 0

    db_payment = UserPayments.objects.get(
        user=user,
        course=course,
        )

    webhook_payload = {
        "type": "notification",
        "event": "payment.canceled",
        "object": {
            "id": str(db_payment.provider_payment_id),
            "status": "canceled",
            "amount": {
                "value": str(db_payment.amount),
                "currency": "RUB",
            },
            "metadata": {
                "user_id": str(user.id),
                "course_id": str(course.id),
            },
        },
    }

    response = client.post(
        reverse("payment_webhook"),
        data=json.dumps(webhook_payload),
        content_type="application/json",
    )

    db_payment.refresh_from_db()
    
    assert response.status_code == 200
    assert db_payment.status == 'canceled'

@pytest.mark.django_db
def test_payment_verify_error(client, user):
    client.force_login(user)

    course = Course.objects.create(
        title="Course 1",
        price = Decimal(300),
    )
    with patch("payment.views.create_smart_payment",) as mock_create:
        mock_create.return_value = {
                "payment_id": "test-payment-id",
                "confirmation_url": "http://test-payment",
            }
        response = client.post(
        reverse("purchase_redirect",
                kwargs={'course_id':course.id}),
        data = {},
        HTTP_REFERER="/some-page/",
        )

    assert response.status_code == 302

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 0

    db_payment = UserPayments.objects.get(
        user=user,
        course=course,
        )

    webhook_payload = {
        "type": "notification",
        "event": "payment.succeeded",
        "object": {
            "id": str(db_payment.provider_payment_id),
            "status": "succeeded",
            "amount": {
                "value": str(db_payment.amount),
                "currency": "RUB",
            },
            "metadata": {
                "user_id": str(user.id),
                "course_id": str(course.id),
            },
        },
    }

    with patch("payment.views.verify_payment", return_value=False) as mock_verify:
        response = client.post(
            reverse("payment_webhook"),
            data=json.dumps(webhook_payload),
            content_type="application/json",
        )

        assert response.status_code == 200

        mock_verify.assert_called_once_with(
            str(db_payment.provider_payment_id),
            expected_user_id=user.id,
            expected_course_id=course.id,
            expected_amount=db_payment.amount,
        )

    db_payment.refresh_from_db()

    assert db_payment.status == 'verify_error'

@pytest.mark.django_db
def test_payment_verify_YKassa_error(client, user):
    client.force_login(user)

    course = Course.objects.create(
        title="Course 1",
        price = Decimal(300),
    )

    with patch("payment.views.create_smart_payment",) as mock_create:
        mock_create.return_value = {
                "payment_id": "test-payment-id",
                "confirmation_url": "http://test-payment",
            }
        response = client.post(
        reverse("purchase_redirect",
                kwargs={'course_id':course.id}),
        data = {},
        HTTP_REFERER="/some-page/",
        )

    assert response.status_code == 302

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 0

    db_payment = UserPayments.objects.get(
        user=user,
        course=course,
        )

    webhook_payload = {
        "type": "notification",
        "event": "payment.succeeded",
        "object": {
            "id": str(db_payment.provider_payment_id),
            "status": "succeeded",
            "amount": {
                "value": str(db_payment.amount),
                "currency": "RUB",
            },
            "metadata": {
                "user_id": str(user.id),
                "course_id": str(course.id),
            },
        },
    }

    with patch("payment.views.verify_payment") as mock_verify:
        original_error = PaymentVerifyError('')
        mock_verify.side_effect = original_error
        response = client.post(
            reverse("payment_webhook"),
            data=json.dumps(webhook_payload),
            content_type="application/json",
        )

        assert response.status_code == 200

        mock_verify.assert_called_once_with(
            str(db_payment.provider_payment_id),
            expected_user_id=user.id,
            expected_course_id=course.id,
            expected_amount=db_payment.amount,
        )

    db_payment.refresh_from_db()

    assert db_payment.status == 'verify_error'

@pytest.mark.django_db
def test_payment_no_metadata(client, user):
    client.force_login(user)

    course = Course.objects.create(
        title="Course 1",
        price = Decimal(300),
    )
    with patch("payment.views.create_smart_payment",) as mock_create:
        mock_create.return_value = {
                "payment_id": "test-payment-id",
                "confirmation_url": "http://test-payment",
            }
        response = client.post(
        reverse("purchase_redirect",
                kwargs={'course_id':course.id}),
        data = {},
        HTTP_REFERER="/some-page/",
        )

    assert response.status_code == 302

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 0

    db_payment = UserPayments.objects.get(
        user=user,
        course=course,
        )

    webhook_payload = {
        "type": "notification",
        "event": "payment.succeeded",
        "object": {
            "id": str(db_payment.provider_payment_id),
            "status": "succeeded",
            "amount": {
                "value": str(db_payment.amount),
                "currency": "RUB",
            },
            "metadata": {
            },
        },
    }

    response = client.post(
        reverse("payment_webhook"),
        data=json.dumps(webhook_payload),
        content_type="application/json",
    )

    assert response.status_code == 200

@pytest.mark.django_db
def test_payment_incorrect_metadata(client, user):
    client.force_login(user)

    course = Course.objects.create(
        title="Course 1",
        price = Decimal(300),
    )

    with patch("payment.views.create_smart_payment",) as mock_create:
        mock_create.return_value = {
                "payment_id": "test-payment-id",
                "confirmation_url": "http://test-payment",
            }
        response = client.post(
        reverse("purchase_redirect",
                kwargs={'course_id':course.id}),
        data = {},
        HTTP_REFERER="/some-page/",
        )

    assert response.status_code == 302

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 0

    db_payment = UserPayments.objects.get(
        user=user,
        course=course,
        )

    webhook_payload = {
        "type": "notification",
        "event": "payment.succeeded",
        "object": {
            "id": str(db_payment.provider_payment_id),
            "status": "succeeded",
            "amount": {
                "value": str(db_payment.amount),
                "currency": "RUB",
            },
            "metadata": {
                "user_id": str(user.id),
            },
        },
    }

    response = client.post(
        reverse("payment_webhook"),
        data=json.dumps(webhook_payload),
        content_type="application/json",
    )

    assert response.status_code == 200

@pytest.mark.django_db
def test_payment_notification_idempatation(client, user):
    client.force_login(user)

    course = Course.objects.create(
        title="Course 1",
        price = Decimal(300),
    )

    with patch("payment.views.create_smart_payment",) as mock_create:
        mock_create.return_value = {
                "payment_id": "test-payment-id",
                "confirmation_url": "http://test-payment",
            }
        response = client.post(
        reverse("purchase_redirect",
                kwargs={'course_id':course.id}),
        data = {},
        HTTP_REFERER="/some-page/",
        )

    assert response.status_code == 302

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 0

    db_payment = UserPayments.objects.get(
        user=user,
        course=course,
        )

    webhook_payload = {
        "type": "notification",
        "event": "payment.succeeded",
        "object": {
            "id": str(db_payment.provider_payment_id),
            "status": "succeeded",
            "amount": {
                "value": str(db_payment.amount),
                "currency": "RUB",
            },
            "metadata": {
                "user_id": str(user.id),
                "course_id": str(course.id),
            },
        },
    }

    with patch("payment.views.verify_payment", return_value=True) as mock_verify:
        response = client.post(
            reverse("payment_webhook"),
            data=json.dumps(webhook_payload),
            content_type="application/json",
        )

        assert response.status_code == 200

        mock_verify.assert_called_once_with(
            str(db_payment.provider_payment_id),
            expected_user_id=user.id,
            expected_course_id=course.id,
            expected_amount=db_payment.amount,
        )

    db_payment.refresh_from_db()

    assert db_payment.status == 'access_granted'
    assert UserProgress.objects.get(user=user,course = course)

    with patch("payment.views.verify_payment", return_value=True) as mock_verify:
        response = client.post(
            reverse("payment_webhook"),
            data=json.dumps(webhook_payload),
            content_type="application/json",
        )

        assert response.status_code == 200

        mock_verify.assert_not_called()

    db_payment.refresh_from_db()

    assert db_payment.status == 'access_granted'
    assert UserProgress.objects.get(user=user,course = course)