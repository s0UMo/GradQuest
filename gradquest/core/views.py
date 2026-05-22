from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models.functions import Lower
from .models import Company, SiteSetting
from .forms import CompanyForm, ChangeCredentialsForm

def index(request):
    companies = Company.objects.all().order_by(Lower('name'))
    return render(request, 'core/index.html', {'companies': companies})

def pyq_redirect(request):
    pyq_link = SiteSetting.get_pyq_link()
    if not pyq_link:
        return redirect('/?coming_soon=true')
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
    companies = Company.objects.all().order_by(Lower('name'))
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
        pyq_link = request.POST.get('pyq_link', '').strip()
        setting, created = SiteSetting.objects.get_or_create(id=1)
        setting.pyq_link = pyq_link
        setting.save()
        if pyq_link:
            messages.success(request, "IEM PYQ redirection link updated successfully.")
        else:
            messages.success(request, "IEM PYQ link cleared. Users will see a 'Coming Soon' popup.")
    return redirect('dashboard')

@staff_required
def change_credentials_view(request):
    if request.method == 'POST':
        form = ChangeCredentialsForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = request.user
            new_username = form.cleaned_data.get('new_username')
            new_password = form.cleaned_data.get('new_password')
            
            updated_fields = []
            if new_username:
                user.username = new_username
                updated_fields.append("username")
            if new_password:
                user.set_password(new_password)
                updated_fields.append("password")
            
            user.save()
            
            # Keep the user logged in after password change
            if new_password:
                update_session_auth_hash(request, user)
                
            msg = f"Admin {' and '.join(updated_fields)} updated successfully."
            messages.success(request, msg)
        else:
            # Join errors to display as a single toast message
            error_list = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_list.append(error)
            for error in form.non_field_errors():
                error_list.append(error)
            
            messages.error(request, "Failed to update credentials: " + " ".join(error_list))
            
    return redirect('dashboard')