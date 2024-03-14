# Create your views here.
# core/views.py
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import redirect
import uuid
import time


from core.lib.api import get_company_list, format_json_response, get_data_scrapit_mpages, format_json_response_scrapit, get_current_time, update_job_status, stop_job, update_job_data
from core.lib.score.background_score import notify_user


from rq import Queue
from rq.job import Job
from worker import conn
q = Queue(connection=conn)

def end_task(request, job_id):
    print("View: end_task()")

    cache_id = f"{request.user.email}_scorelist"
    stop_job(cache_id=cache_id, job_id=job_id)
    print(job_id)

    response = HttpResponse('Task Ended', status=204)  # No Content, or choose an appropriate status
    response['HX-Trigger'] = 'finishTaskEvent'  # Custom event name
    return response


def load_score(request, job_id):
    print("View: load_score()")
    score_id = f"{request.user.email}_scorelist"
    job_list = cache.get(score_id)
    for job in job_list:
        if job['job_id'] == job_id:
            if job['source'] == 'ecom':
                return render(request, 'core/app/dashboard/app_ecommerce.html', {'projects': job['data']['data'], "score_list": job_list})
            if job['source'] == 'gmap':
                return render(request, 'core/app/dashboard/app_gmap.html', {'projects': job['data']['data'], "score_list": job_list})


def check_task_status(request, job_id):
    print("View: check_task_status()")
    print(job_id)
    job = Job.fetch(job_id, connection=conn)
    if job.is_finished == True:
        result = job.result
        score_list_id = f"{request.user.email}_scorelist"
        update_job_status(score_list_id, job.id, "Ok")
        update_job_data(score_list_id, job.id, result)
        return JsonResponse({"status": "complete"})
    else:
        return JsonResponse({"status": "pending"})


def check_task_status_gmap(request, job_id):
    print("View: check_task_status()")
    print(job_id)
    job = Job.fetch(job_id, connection=conn)
    if job.is_finished == True:
        result = job.result
        score_list_id = f"{request.user.email}_scorelist"
        update_job_status(score_list_id, job.id, "Ok")
        update_job_data(score_list_id, job.id, result)
        return JsonResponse({"status": "complete"})
    else:
        return JsonResponse({"status": "pending"})


def start_task_ecommerce(request):
    print("Fuction: start_task_ecommerce()")
    global q
    
    cache_id = f"{request.user.email}_ecommerce"
    data = cache.get(cache_id)
    url_lead = request.POST.get('icp_url')
    product = request.POST.get('product')
    lead_type = request.POST.get('lead_type')
    
    
    job = q.enqueue(notify_user, data, url_lead, product, lead_type, job_timeout=100000)
    
    task_idx = get_current_time()
    score_list = cache.get(f"{request.user.email}_scorelist", [])
    score_list.append({"id": task_idx, "status": "pending", "job_id": job.id, "data": {}, "source": "ecom"})
    cache.set(f"{request.user.email}_scorelist", score_list,timeout=604800)
    print(url_lead)
    return JsonResponse({"job_id": job.id})


def start_task_gmap(request):
    print("Fuction: start_task_gmap()")
    global q
    
    cache_id = f"{request.user.email}_gmap"
    data = cache.get(cache_id)
    url_lead = request.POST.get('icp_url')
    product = request.POST.get('product')
    lead_type = request.POST.get('lead_type')
    job = q.enqueue(notify_user, data, url_lead, product, lead_type, job_timeout=100000)
    
    task_idx = get_current_time()
    score_list = cache.get(f"{request.user.email}_scorelist", [])
    score_list.append({"id": task_idx, "status": "pending", "job_id": job.id, "data": {}, "source": "gmap"})
    cache.set(f"{request.user.email}_scorelist", score_list,timeout=604800)
    print(url_lead)
    return JsonResponse({"job_id": job.id})


@login_required
def app_view_ecommerce(request):
    print("Views: app_view_ecommerce()")
    cache_id = f"{request.user.email}_ecommerce"
    print(cache_id)
    score_list_id = f"{request.user.email}_scorelist"
    score_list = cache.get(score_list_id)
    # Check if the request is made via HTMX
    if request.htmx:
            # Check if the clear cache action was triggered
        if 'clear_cache' in request.GET.keys():
            CACHE_ECOMMERCE = {}
            cache.set(cache_id, CACHE_ECOMMERCE, timeout=3600)
            return render(request, 'core/app/dashboard/app_ecommerce.html', {'projects': CACHE_ECOMMERCE.get('data', {}), "score_list": score_list})

        # Check if the request is specifically from the left menu
        if 'hx_menu_request' in request.GET.keys():
            CACHE_ECOMMERCE = cache.get(cache_id)
            if CACHE_ECOMMERCE is not None:
                return render(request, 'core/app/dashboard/app_ecommerce.html', {'projects': CACHE_ECOMMERCE.get('data', {}), "score_list": score_list})
            else:
                return render(request, 'core/app/dashboard/app_ecommerce.html', {"score_list": score_list})
        else:
            # Process the request as before
            CACHE_ECOMMERCE = {}
            query = request.GET.get('query', '')
            country = request.GET.get('country', '')
            city = request.GET.get('city', '')
            revenue = request.GET.get('revenue', '')
            nb_results = int(request.GET.get('results', '10'))
            raw = get_company_list(query=query, location=country, city=city, revenue=revenue, nb_results=nb_results)  # Adjust this function as needed
            data = format_json_response(raw)
            CACHE_ECOMMERCE = {"data": data, "product": query}
            cache.set(cache_id, CACHE_ECOMMERCE, timeout=3600)

            print("Load complete")
            return render(request, 'core/app/dashboard/app_ecommerce.html', {'projects': CACHE_ECOMMERCE.get('data', {}), "score_list": score_list})
    else:
        CACHE_ECOMMERCE = cache.get(cache_id)
        if CACHE_ECOMMERCE is not None:
            return render(request, 'core/app/dashboard/app_ecommerce_full.html', {'projects': CACHE_ECOMMERCE.get('data', {}), "score_list": score_list})
        else:
            return render(request, 'core/app/dashboard/app_ecommerce_full.html', {"score_list": score_list})
            # return render(request, 'core/app/dashboard/app_ecommerce_full.html')


@login_required
def app_view_gmap(request):
    print("Views: app_view_gmap()")
    cache_id = f"{request.user.email}_gmap"
    score_list_id = f"{request.user.email}_scorelist"
    score_list = cache.get(score_list_id)
    print(cache_id)
    # Check if the request is made via HTMX
    if request.htmx:
            # Check if the clear cache action was triggered
        if 'clear_cache' in request.GET.keys():
            CACHE_GMAP = {}
            cache.set(cache_id, CACHE_GMAP, timeout=3600)
            return render(request, 'core/app/dashboard/app_gmap.html', {'projects': CACHE_GMAP.get('data', {}), "score_list": score_list})

        # Check if the request is specifically from the left menu
        if 'hx_menu_request' in request.GET.keys():
            CACHE_GMAP = cache.get(cache_id)
            if CACHE_GMAP is not None:
                return render(request, 'core/app/dashboard/app_gmap.html', {'projects': CACHE_GMAP.get('data', {}), "score_list": score_list})
            else:
                return render(request, 'core/app/dashboard/app_gmap.html', {})
        else:
            # Process the request as before
            CACHE_GMAP = {}
            query = request.GET.get('query', '')
            country = request.GET.get('country', '')
            city = request.GET.get('city', '')
            raw_google = get_data_scrapit_mpages(query=query.strip(), country=country.strip(), city=city.strip())
            data = format_json_response_scrapit(raw_google)
            CACHE_GMAP = {"data": data, "product": query}
            cache.set(cache_id, CACHE_GMAP, timeout=3600)

            print("Load complete")
            return render(request, 'core/app/dashboard/app_gmap.html', {'projects': CACHE_GMAP.get('data', {}), "score_list": score_list})
    else:
        CACHE_GMAP = cache.get(cache_id)
        if CACHE_GMAP is not None:
            return render(request, 'core/app/dashboard/app_gmap_full.html', {'projects': CACHE_GMAP.get('data', {}), "score_list": score_list})
        else:
            return render(request, 'core/app/dashboard/app_gmap_full.html', {"score_list": score_list})


@login_required
def settings_view_ecom(request):
    cache_id = f"{request.user.email}_ecommerce"
    data = cache.get(cache_id)

    if data is None:
        return JsonResponse({"error": "no data in cache"})
        # return render(request, 'core/app/dashboard/app_ecommerce.html', {"score_list": score_list})
    if request.htmx:
        return render(request, 'core/app/settings/settings.html')
    return render(request, 'core/app/settings/settings_full.html')

@login_required
def settings_view_gmap(request):
    cache_id = f"{request.user.email}_gmap"
    data = cache.get(cache_id)

    if data is None:
        return JsonResponse({"error": "no data in cache"})
        # return render(request, 'core/app/dashboard/app_ecommerce.html', {"score_list": score_list})
    if request.htmx:
        return render(request, 'core/app/settings_gmap/settings.html')
    return render(request, 'core/app/settings_gmap/settings_full.html')




@login_required
def app_view_2(request):
    if request.htmx:
        return render(request, 'core/app/dashboard_2/app.html', {'user': request.user})
    return render(request, 'core/app/dashboard_2/app_full.html', {'user': request.user})


def register(request):
    # Redirect to app if user is already logged in
    if request.user.is_authenticated:
        return redirect('app')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login')  # Redirect to a login page or dashboard
        else:
            # Form is not valid, show a message to the user
            messages.error(request, "Register failed, please retry.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    # Redirect to dashboard if user is already logged in
    if request.user.is_authenticated:
        return redirect('app_gmap')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('app_ecommerce')  # Redirect only if user is authenticated
        else:
            messages.error(request, "Username or password incorrect")
            return render(request, 'core/login.html')  # Stay on login page if not authenticated
    return render(request, 'core/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def home(request):
    return render(request, 'core/home.html', {})
