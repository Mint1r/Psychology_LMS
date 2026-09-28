from .models import Lesson, Course
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseForbidden,FileResponse
from access.decorators import login_or_404
from access.models import CourseAccess

@login_or_404
def get_lesson_video(request, lesson_pk, course_pk):
    lesson = get_object_or_404(Lesson, pk=lesson_pk)

    if not lesson.video:
        raise Http404()

    course = get_object_or_404(Course, pk=course_pk)

    if not course.modules.filter(lessons=lesson).exists():
        raise Http404()

    if not CourseAccess.objects.filter(
        user=request.user,
        course=course,
        status=CourseAccess.Status.ACTIVE,
    ).exists():
        return HttpResponseForbidden()

    response = HttpResponse()
    response["X-Accel-Redirect"] = f"/protected/{lesson.video.name}"

    return response

@login_or_404
def get_lesson_materials(request,lesson_pk,course_pk, material_pk):

    lesson = get_object_or_404(Lesson, pk=lesson_pk)
    course = get_object_or_404(Course, pk=course_pk)

    if not course.modules.filter(lessons=lesson).exists():
        raise Http404()
    
    material = lesson.materials.filter(id=material_pk).first()

    if not material:
        raise Http404()

    if CourseAccess.objects.filter(
        user = request.user, 
        course = course,
        status = CourseAccess.Status.ACTIVE
        ).exists():
        
        return FileResponse(
            material.file.open("rb"),
            as_attachment=True,
            filename=material.file.name.split("/")[-1],
        )

    return HttpResponseForbidden()