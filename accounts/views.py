from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from access.forms import CustomAuthenticationForm
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import UserTests, UserDocuments
from django.http import Http404, FileResponse
from .forms import UserDocumentsForm


def register(request):
    return render(request, 'register.html',)

@require_POST
def user_create(request):

    username = request.POST.get("username")
    phon = request.POST.get("phon_number")
    request.session['form_data'] = {
            'username': username,
            'phon': phon
        }
    form = CustomUserCreationForm(request.POST)
    if form.is_valid():
        new_user = form.save()
        login(request, new_user)
        if 'form_data' in request.session:
             del request.session['form_data']
        return redirect('learn:learn_main')
    if not form.is_valid():
        return render(request, "register.html", {
        "form": form,
    })
    return JsonResponse({"error": "POST request required"}, status=405)



class CustomLoginView(LoginView):
    template_name = 'login.html'  
    redirect_authenticated_user = True 
    authentication_form = CustomAuthenticationForm



@login_required
def get_student_test(request,test_pk):
    if not request.user.groups.filter(name = "admin").exists():
        raise Http404()
    test = get_object_or_404(UserTests,id=test_pk)
    if not test.test_results:
        raise Http404()
    return FileResponse(
            test.test_results.open("rb"),
        )


@login_required
def get_user_documents(request,doc_type,apply_pk):

    ALLOWED_FIELDS = {
        "snils",'passport_main','diploma',
        'passport_registration'
    }

    if doc_type not in ALLOWED_FIELDS:
        raise Http404()
    
    if not request.user.groups.filter(name = "admin").exists():
        raise Http404()
    
    apply = get_object_or_404(UserDocuments,id=apply_pk)

    if apply.status != "pending":
        raise Http404()
    
    doc = getattr(apply, doc_type)

    return FileResponse(
            doc.open("rb"),
        )



@login_required
def documents_input(request,id):
    if request.user.groups.filter(name='can_buy_courses').exists():
        return redirect('purchase', course_id=id)
    user = request.user
    data ={
        'status' : '',
        "id" : id,
           }
    
    user_docs = UserDocuments.objects.filter(user=user).first()
    if user_docs:
        data['status'] = user_docs.status
    return render(request, 'documents_input.html', data)

@require_POST
@login_required
def upload_documents(request,id):

    old_record = UserDocuments.objects.filter(user=request.user).first()
    if old_record:
        old_record.diploma.delete(save=False) 
        old_record.passport_main.delete(save=False) 
        old_record.passport_registration.delete(save=False) 
        old_record.snils.delete(save=False) 
        old_record.delete()

    form = UserDocumentsForm(request.POST,request.FILES)
    if form.is_valid():
        user_docs = form.save(commit=False)
        user_docs.user = request.user
        user_docs.save()
        return redirect("documents_load_page", id=id)
    else:
        return JsonResponse(
            {'error': form.errors},
            status=400
        )
