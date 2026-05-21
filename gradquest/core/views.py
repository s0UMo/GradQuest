from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Company, SiteSetting
from .forms import CompanyForm

def index(request):
    companies = Company.objects.all()
    return render(request, 'core/index.html', {'companies': companies})

def pyq_redirect(request):
    pyq_link = SiteSetting.get_pyq_link()
    return render(request, 'core/PYQ.html', {'pyq_link': pyq_link})

def login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_staff or user.is_superuser:
                    login(request, user)
                    messages.success(request, f"Welcome back, {username}!")
                    return redirect('dashboard')
                else:
                    messages.error(request, "Access denied. Admin privileges required.")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid login credentials.")
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('index')

def staff_required(view_func):
    """Custom decorator to check if logged in user is a staff member."""
    @login_required(login_url='login')
    def _wrapped_view(request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied("You do not have permission to access this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@staff_required
def dashboard_view(request):
    companies = Company.objects.all()
    pyq_link = SiteSetting.get_pyq_link()
    return render(request, 'core/dashboard.html', {
        'companies': companies,
        'pyq_link': pyq_link
    })

@staff_required
def company_create_view(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Company created successfully.")
            return redirect('dashboard')
        else:
            messages.error(request, "Failed to create company. Please check the inputs.")
    else:
        form = CompanyForm()
    return render(request, 'core/company_form.html', {'form': form, 'action': 'Add'})

@staff_required
def company_edit_view(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, f"{company.name} updated successfully.")
            return redirect('dashboard')
        else:
            messages.error(request, "Failed to update company. Please check the inputs.")
    else:
        form = CompanyForm(instance=company)
    return render(request, 'core/company_form.html', {'form': form, 'company': company, 'action': 'Edit'})

@staff_required
def company_delete_view(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        name = company.name
        company.delete()
        messages.success(request, f"{name} deleted successfully.")
        return redirect('dashboard')
    return render(request, 'core/company_confirm_delete.html', {'company': company})

@staff_required
def update_pyq_link_view(request):
    if request.method == 'POST':
        pyq_link = request.POST.get('pyq_link')
        if pyq_link:
            setting, created = SiteSetting.objects.get_or_create(id=1)
            setting.pyq_link = pyq_link
            setting.save()
            messages.success(request, "IEM PYQ redirection link updated successfully.")
        else:
            messages.error(request, "Failed to update link. URL cannot be empty.")
    return redirect('dashboard')