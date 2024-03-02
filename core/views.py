# Create your views here.
# core/views.py
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout


from core.lib.api import get_company_list, format_json_response, get_data_scrapit_mpages, format_json_response_scrapit
from core.lib.score.openai_api import sort_by_stars

CACHE_ECOMMERCE = []
CACHE_GMAP = []

@login_required
def settings_view(request):
    if request.htmx:
        return render(request, 'core/app/settings/settings.html')
    return render(request, 'core/app/settings/settings_full.html')


@login_required
def app_view_ecommerce(request):
    print("Views: app_view_ecommerce()")
    global CACHE_ECOMMERCE
    # Check if the request is made via HTMX
    if request.htmx:
            # Check if the clear cache action was triggered
        if 'clear_cache' in request.GET.keys():
            CACHE_ECOMMERCE = [] 
            return render(request, 'core/app/dashboard/app_ecommerce.html', {'projects': CACHE_ECOMMERCE})

        # Check if the request is specifically from the left menu
        if 'hx_menu_request' in request.GET.keys():
            return render(request, 'core/app/dashboard/app_ecommerce.html', {'projects': CACHE_ECOMMERCE})
        else:
            # time.sleep(15)
            # Process the request as before
            CACHE_ECOMMERCE = None
            query = request.GET.get('query', '')
            country = request.GET.get('country', '')
            city = request.GET.get('city', '')
            url_lead_example = request.GET.get('lead_url', '')
            print(url_lead_example)
            raw = get_company_list(query=query, location=country, city=city)  # Adjust this function as needed
            data = format_json_response(raw, url_lead_example, query)
            data = sort_by_stars(data)
            CACHE_ECOMMERCE = data
            print("Load complete")
            return render(request, 'core/app/dashboard/app_ecommerce.html', {'projects': CACHE_ECOMMERCE})
    else:
        # Return the full page if not an HTMX request
        return render(request, 'core/app/dashboard/app_ecommerce_full.html', {})



@login_required
def app_view_gmap(request):
    print("Views: app_view_gmap()")
    if request.htmx:
        if 'hx_menu_request' in request.GET:
            print("htmx_menu")
            return render(request, 'core/app/dashboard/app_gmap.html')
        else:
            print("htmx_load_data")
            query = request.GET.get('query', '')
            country = request.GET.get('country', '')
            city = request.GET.get('city', '')
            url_lead_example = request.GET.get('lead_url', '')
            print(url_lead_example)
            raw_google = get_data_scrapit_mpages(query=query, country=country, city=city)
            data = format_json_response_scrapit(raw_google, url_lead_example, query)
            data = sort_by_stars(data)
            print("Load complete")
            return render(request, 'core/app/dashboard/app_gmap.html', {'projects': data})
    else:
        # Return the full page if not an HTMX request
        return render(request, 'core/app/dashboard/app_gmap_full.html', {})


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
