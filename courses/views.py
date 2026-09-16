from django.contrib.auth.decorators import login_required
from .models import Lesson, Course
from progress.models import UserProgress
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.http import HttpResponseForbidden
from django.http import Http404
from access.decorators import login_or_404

@login_or_404
def get_lesson_video(request,lesson_pk,course_pk):

    lesson = get_object_or_404(Lesson, pk=lesson_pk)
    if not lesson.video:
        raise Http404()
    
    course = get_object_or_404(Course, pk=course_pk)
    if not course.modules.filter(lessons=lesson).exists():
        raise Http404()

    if UserProgress.objects.filter(user = request.user, course = course).exists():
        return FileResponse(
            lesson.video.open("rb"),
            content_type="video/mp4"
        )
    return HttpResponseForbidden()

@login_or_404
def get_lesson_materials(request,lesson_pk,course_pk, material_pk):

    lesson = get_object_or_404(Lesson, pk=lesson_pk)
    course = get_object_or_404(Course, pk=course_pk)

    if not course.modules.filter(lessons=lesson).exists():
        raise Http404()
    
    material = lesson.materials.filter(id=material_pk).first()

    if not material:
        raise Http404()

    if UserProgress.objects.filter(
        user=request.user,
        course=course
    ).exists():
        return FileResponse(
            material.file.open("rb"),
            as_attachment=True,
            filename=material.file.name.split("/")[-1],
        )

    return HttpResponseForbidden()