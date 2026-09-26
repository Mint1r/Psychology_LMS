import pytest
from courses.models import Course, CourseModule, Module, ModuleLesson, Lesson
from accounts.models import User, UserDocuments, UserTests
from access.views import get_lessons_dict
from django.urls import reverse
from progress.models import UserLessonProgress, UserProgress, UserModulProgress
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import Mock, patch
from io import BytesIO
from PIL import Image
from django.contrib.messages import get_messages
from progress.services import update_user_course_progress

@pytest.mark.django_db
def test_get_lessons_dict():
    # Arrange
    course = Course.objects.create(
        title="Python Course"
    )

    module_1 = Module.objects.create(
        title="Module 1"
    )

    module_2 = Module.objects.create(
        title="Module 2"
    )

    lesson_1 = Lesson.objects.create(title="Lesson 1")
    lesson_2 = Lesson.objects.create(title="Lesson 2")
    lesson_3 = Lesson.objects.create(title="Lesson 3")
    lesson_4 = Lesson.objects.create(title="Lesson 4")

    CourseModule.objects.create(
        course=course,
        module=module_1,
        order=1
    )

    CourseModule.objects.create(
        course=course,
        module=module_2,
        order=2
    )

    ModuleLesson.objects.create(
        module=module_1,
        lesson=lesson_1,
        order=1
    )

    ModuleLesson.objects.create(
        module=module_1,
        lesson=lesson_2,
        order=2
    )

    ModuleLesson.objects.create(
        module=module_2,
        lesson=lesson_3,
        order=1,
    )

    ModuleLesson.objects.create(
        module=module_2,
        lesson=lesson_4,
        order=2
    )

    user_obj = User.objects.create(
        phon_number = '+79533677788',
        email = 'mail@mail.ru'
        )

    user_progress = UserProgress.objects.create(
        user = user_obj,
        course = course,
        current_class = 3
    )

    # Act
    result = get_lessons_dict(course, user_progress)

    # Assert
    assert len(result) == 3

    assert result[0]["module_order"] == 1
    assert result[0]["module_lesson"] == module_1.module_lessons.get(
        lesson=lesson_1
    )
    assert result[0]["lesson_id"] == lesson_1.id

    assert result[1]["module_order"] == 1
    assert result[1]["lesson_id"] == lesson_2.id

    assert result[2]["module_order"] == 2
    assert result[2]["lesson_id"] == lesson_3.id

@pytest.mark.django_db
def test_learn_course_increments_progress(client, user):
    client.force_login(user)

    course =Course.objects.create(
        title="Python Course"   
    )

    module = Module.objects.create(
        title="Module 1"
    )
    lesson1 = Lesson.objects.create(
        title="Lesson 1"
    )
    lesson2 = Lesson.objects.create(
        title="Lesson 2"
    )

    user_progress = UserProgress.objects.create(
        user=user,
        course=course,
        current_class=1,
        status="started",
    )

    CourseModule.objects.create(
        course=course,
        module=module,
        order=1
    )

    ModuleLesson.objects.create(
        module=module,
        lesson=lesson1,
        order=1
    )

    ModuleLesson.objects.create(
        module=module,
        lesson=lesson2,
        order=2
    )
    
    UserLessonProgress.objects.create(
        user=user,
        lesson=lesson1,
        status="finished",
    )

    UserModulProgress.objects.create(
        user=user,
        modul=module,
    )

    UserLessonProgress.objects.create(
        user=user,
        lesson=lesson2,
        status="started",
    )
    
    update_user_course_progress(
        course = course,
        user_progress = user_progress,
        user = user
    )

    user_progress.refresh_from_db()

    assert user_progress.current_class == 2


@pytest.mark.django_db
def test_learn_course_finish_course(client, user, django_capture_on_commit_callbacks):
    client.force_login(user)

    course =Course.objects.create(
        title="Python Course"   
    )

    module = Module.objects.create(
        title="Module 1"
    )

    lesson1 = Lesson.objects.create(
        title="Lesson 1"
    )
    lesson2 = Lesson.objects.create(
        title="Lesson 2"
    )

    user_progress = UserProgress.objects.create(
        user=user,
        course=course,
        current_class=1,
        status="started",
    )
    
    UserLessonProgress.objects.create(
        user=user,
        lesson=lesson1,
        status="finished",
    )
    UserLessonProgress.objects.create(
        user=user,
        lesson=lesson2,
        status="finished",
    )

    UserModulProgress.objects.create(
        user=user,
        modul=module,
    )

    CourseModule.objects.create(
        course=course,
        module=module,
        order=1
    )

    ModuleLesson.objects.create(
        module=module,
        lesson=lesson1,
        order=1
    )
    ModuleLesson.objects.create(
        module=module,
        lesson=lesson2,
        order=2
    )

    with patch('progress.services.course_finish_aply') as fake_send_aply:
        with django_capture_on_commit_callbacks(execute=True):
            update_user_course_progress(
                course = course,
                user_progress = user_progress,
                user = user
            )
        fake_send_aply.assert_called_once()

    user_progress.refresh_from_db()

    assert user_progress.current_class == 1000
    assert user_progress.status == 'finished'


@pytest.mark.django_db
def test_learn_lesson(client, user):
    client.force_login(user)

    course =Course.objects.create(
        title="Python Course"   
    )

    module = Module.objects.create(
        title="Module 1"
    )

    lesson1 = Lesson.objects.create(
        title="Lesson 1"
    )
    lesson2 = Lesson.objects.create(
        title="Lesson 2"
    )

    user_progress = UserProgress.objects.create(
        user=user,
        course=course,
        current_class=2,
        status="started",
    )
    
    UserLessonProgress.objects.create(
        user=user,
        lesson=lesson1,
        status="finished",
    )
    UserLessonProgress.objects.create(
        user=user,
        lesson=lesson2,
        status="started",
    )

    CourseModule.objects.create(
        course=course,
        module=module,
        order=1
    )

    ModuleLesson.objects.create(
        module=module,
        lesson=lesson1,
        order=1
    )
    ModuleLesson.objects.create(
        module=module,
        lesson=lesson2,
        order=2
    )

    response = client.get(
        reverse(
            "learn:learn_lesson",
            kwargs={"course_id": course.id,
                    'lesson_id':lesson2.id}
        )
    )

    assert response.status_code == 200
    user_progress.refresh_from_db()



@pytest.mark.django_db
def test_applications_accept(client, user,django_capture_on_commit_callbacks):
    admin_group = Group.objects.create(name="admin")
    buy_group = Group.objects.create(name="can_buy_courses")

    user.groups.add(admin_group)

    application = UserDocuments.objects.create(
        user=user,
        diploma=SimpleUploadedFile(
            "diploma.pdf",
            b"test",
            content_type="application/pdf",
        ),
        passport_main=SimpleUploadedFile(
            "passport.jpg",
            b"test",
            content_type="image/jpeg",
        ),
        passport_registration=SimpleUploadedFile(
            "registration.jpg",
            b"test",
            content_type="image/jpeg",
        ),
        snils=SimpleUploadedFile(
            "snils.jpg",
            b"test",
            content_type="image/jpeg",
        ),
        status="pending",
    )

    client.force_login(user)

    with patch('access.views.send_email2') as fake_send_mail:
        with django_capture_on_commit_callbacks(execute=True):
            response = client.post(
                reverse("learn:applications"),
                {
                    "application_id": application.id,
                    "action": "accept",
                },
                HTTP_REFERER="/some-page/",
            )
        fake_send_mail.assert_called_once()

    assert response.status_code == 302

    application.refresh_from_db()

    assert application.status == "approved"
    assert application.user.groups.filter(
        name="can_buy_courses"
    ).exists()

@pytest.mark.django_db
def test_applications_reject(client, user,django_capture_on_commit_callbacks):
    admin_group = Group.objects.create(name="admin")
    buy_group = Group.objects.create(name="can_buy_courses")
    fake_send_mail = Mock()

    user.groups.add(admin_group)

    application = UserDocuments.objects.create(
        user=user,
        diploma=SimpleUploadedFile(
            "diploma.pdf",
            b"test",
            content_type="application/pdf",
        ),
        passport_main=SimpleUploadedFile(
            "passport.jpg",
            b"test",
            content_type="image/jpeg",
        ),
        passport_registration=SimpleUploadedFile(
            "registration.jpg",
            b"test",
            content_type="image/jpeg",
        ),
        snils=SimpleUploadedFile(
            "snils.jpg",
            b"test",
            content_type="image/jpeg",
        ),
        status="pending",
    )

    client.force_login(user)
    with patch('access.views.send_email2') as fake_send_mail:
        with django_capture_on_commit_callbacks(execute=True):
            response = client.post(
                reverse("learn:applications"),
                {
                    "application_id": application.id,
                    "action": "reject",
                },
                HTTP_REFERER="/some-page/",
            )
        fake_send_mail.assert_called_once()

    assert response.status_code == 302

    application.refresh_from_db()

    assert application.status == "rejected"
    assert not application.user.groups.filter(
        name="can_buy_courses"
    ).exists()

@pytest.mark.django_db
def test_admin_panel(client, user):
    admin_group = Group.objects.create(name="admin")
    buy_group = Group.objects.create(name="can_buy_courses")

    user.groups.add(admin_group)

    client.force_login(user)
    response = client.get(
        reverse(
            "learn:admin_panel",
            kwargs={}
        )
    )

    assert response.status_code == 200

@pytest.mark.django_db
def test_admin_panel_no_admin_group(client, user):
    client.force_login(user)
    response = client.get(
        reverse(
            "learn:admin_panel",
            kwargs={}
        )
    )

    assert response.status_code == 404

@pytest.mark.django_db
def test_load_test(client, user):
    buffer = BytesIO()
    client.force_login(user)

    Image.new("RGB", (100, 100), "white").save(
        buffer,
        format="JPEG",
    )

    image = SimpleUploadedFile(
        "test.jpg",
        buffer.getvalue(),
        content_type="image/jpeg",
    )

    course =Course.objects.create(
        title="Python Course"   
    )
    
    lesson1 = Lesson.objects.create(
        title="Lesson 1"
    )


    response = client.post(
        reverse("learn:load_test",
                kwargs={'course_id':course.id,
                        'lesson_id':lesson1.id}),
        {
            "test_file": image,
        },
        HTTP_REFERER="/some-page/",
    )
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 0
    assert response.status_code == 302

@pytest.mark.django_db
def test_load_test_no_file(client, user):
    client.force_login(user)

    course =Course.objects.create(
        title="Python Course"   
    )
    
    lesson1 = Lesson.objects.create(
        title="Lesson 1"
    )

    response = client.post(
        reverse("learn:load_test",
                kwargs={'course_id':course.id,
                        'lesson_id':lesson1.id}),
        {},
        HTTP_REFERER="/some-page/",
    )
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == 'Нет файла'
    assert response.status_code == 302


@pytest.mark.django_db
def test_complite_lesson(client, user):
    client.force_login(user)

    course =Course.objects.create(
        title="Python Course"   
    )

    module = Module.objects.create(
        title="Python Module"
    )

    lesson1 = Lesson.objects.create(
        title="Lesson 1"
    )
        
    lesson2 = Lesson.objects.create(
        title="Lesson 2"
    )

    CourseModule.objects.create(
        course=course,
        module=module,
        order=1
    )

    ModuleLesson.objects.create(
        module=module,
        lesson=lesson1,
        order=1
    )

    ModuleLesson.objects.create(
        module=module,
        lesson=lesson2,
        order=2
    )

    UserLessonProgress.objects.create(
        user=user,
        lesson=lesson1,
        status="started",
    )

    UserLessonProgress.objects.create(
        user=user,
        lesson=lesson2,
        status="started",
    )

    UserModulProgress.objects.create(
        user=user,
        modul=module,
    )

    progress = UserProgress.objects.create(
        user=user,
        course=course,
        current_class = 1,
    )


    response = client.post(
        reverse("learn:complit_lesson",
                kwargs={'course_id':course.id,
                        'lesson_id':lesson1.id,}),
        {},
        HTTP_REFERER="/some-page/",
    )

    assert response.status_code == 302
    progress.refresh_from_db()
    progress.current_class == 1000

@pytest.mark.django_db
def test_test_decision(client, user,django_capture_on_commit_callbacks):
    admin_group = Group.objects.create(name="admin")
    buffer = BytesIO()
    client.force_login(user)

    Image.new("RGB", (100, 100), "white").save(
        buffer,
        format="JPEG",
    )

    image = SimpleUploadedFile(
        "test.jpg",
        buffer.getvalue(),
        content_type="image/jpeg",
    )

    module = Module.objects.create(
        title="Python Module"
    )

    course =Course.objects.create(
        title="Python Course"   
    )

    user.groups.add(admin_group)

    lesson1 = Lesson.objects.create(
        title="Lesson 1"
    )

    lesson2 = Lesson.objects.create(
        title="Lesson 2"
    )

    test = UserTests.objects.create(
        user = user,
        lesson = lesson1,
        test_results = image,
        course_id = course.id
    )
    
    CourseModule.objects.create(
        course=course,
        module=module,
        order=1
    )

    progress = UserLessonProgress.objects.create(
        user=user,
        lesson=lesson1,
        status="started",
    )

    UserLessonProgress.objects.create(
        user=user,
        lesson=lesson2,
        status="started",
    )
    
    UserModulProgress.objects.create(
        user=user,
        modul=module,
    )

    ModuleLesson.objects.create(
        module=module,
        lesson=lesson1,
        order=1
    )

    ModuleLesson.objects.create(
        module=module,
        lesson=lesson2,
        order=2
    )

    user_progress = UserProgress.objects.create(
        user=user,
        course=course,
        current_class=1,
        status="started",
    )


    client.force_login(user)
    with patch('access.views.send_email2') as fake_send_mail:
        with django_capture_on_commit_callbacks(execute=True) as call:
            response = client.post(
                reverse("learn:test_cheek"),
                {
                    "comment": '',
                    'test_id':test.id,
                    "action": "accept",
                },
                HTTP_REFERER="/some-page/",
            )

        fake_send_mail.assert_called_once()

    progress.refresh_from_db()
    test.refresh_from_db()
    assert response.status_code == 302
    assert progress.status == "finished"
    assert test.status == "sucseed"

