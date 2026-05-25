from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.cache import cache
from django.db.models.functions import Lower
from .models import Company, SiteSetting
from .forms import CompanyForm, ChangeCredentialsForm

def index(request):
    companies = cache.get_or_set(
        'sorted_companies',
        lambda: list(Company.objects.all().order_by(Lower('name'))),
        3600
    )
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
    companies = cache.get_or_set(
        'sorted_companies',
        lambda: list(Company.objects.all().order_by(Lower('name'))),
        3600
    )
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


@staff_required
def delete_all_companies_view(request):
    if request.method == 'POST':
        password = request.POST.get('password', '').strip()
        if request.user.check_password(password):
            count = Company.objects.all().count()
            Company.objects.all().delete()
            cache.delete('sorted_companies')
            messages.success(request, f"Successfully deleted all {count} companies from the database.")
        else:
            messages.error(request, "Incorrect confirmation password. Bulk deletion aborted.")
    return redirect('dashboard')


@staff_required
def company_bulk_add_view(request):
    if request.method == 'POST':
        bulk_data = request.POST.get('bulk_data', '').strip()
        if not bulk_data:
            messages.error(request, "No data provided. Please enter row and column data.")
            return redirect('company_bulk_add')
        
        import re
        import csv
        import io
        import os
        from django.conf import settings
        from django.db import transaction
        from django.db.models import Count
        
        # Support both comma-separated and tab-separated formats dynamically
        # Detect delimiter by checking the first line
        first_line = bulk_data.split('\n')[0] if bulk_data else ""
        delimiter = '\t' if '\t' in first_line else ','
        
        f = io.StringIO(bulk_data)
        reader = csv.reader(f, delimiter=delimiter)
        
        # Check if first line is a header
        header = next(reader, None)
        header_mapping = {}
        has_header = False
        if header:
            # Clean and lowercase the header values
            header_lower = [h.strip().lower() for h in header]
            first_col = header_lower[0]
            if 'name' in first_col or 'serial' in first_col or 'no' in first_col or 'title' in first_col or 'link' in first_col or 'question' in first_col:
                has_header = True
                # Map headers dynamically
                for idx, col in enumerate(header_lower):
                    if 'name' in col or 'title' in col:
                        header_mapping['name'] = idx
                    elif 'logo' in col:
                        header_mapping['logo_url'] = idx
                    elif 'link' in col or 'url' in col:
                        header_mapping['link'] = idx
                    elif any(q in col for q in ['question', 'count', 'no. of', 'no of', 'qty', 'questions', 'size']):
                        header_mapping['question_count'] = idx
            else:
                # Not a header, rewind StringIO
                f.seek(0)
                reader = csv.reader(io.StringIO(bulk_data), delimiter=delimiter)
        
        rows_imported = 0
        rows_updated = 0
        
        com_dir = os.path.join(settings.BASE_DIR.parent, 'com')
        folder_map = {
            'sap labs': 'sap',
            'hcltech': 'hcl',
            'razor pay': 'razorpay',
            'sales force': 'salesforce',
            'tech mahindra': 'tech-mahindra'
        }
        
        white_bg_folders = [
            'tcs', 'accenture', 'infosys', 'wipro', 'cognizant', 'capgemini', 'deloitte', 'hcl', 'sap'
        ]
        
        try:
            with transaction.atomic():
                for row_idx, row in enumerate(reader, start=1):
                    if not row or len(row) < 2:
                        continue
                    
                    if has_header and header_mapping:
                        name_idx = header_mapping.get('name')
                        link_idx = header_mapping.get('link')
                        logo_idx = header_mapping.get('logo_url')
                        q_count_idx = header_mapping.get('question_count')
                        
                        name = row[name_idx].strip() if (name_idx is not None and len(row) > name_idx) else ""
                        link = row[link_idx].strip() if (link_idx is not None and len(row) > link_idx) else ""
                        logo_url = row[logo_idx].strip() if (logo_idx is not None and len(row) > logo_idx) else ""
                        q_count_input = row[q_count_idx].strip() if (q_count_idx is not None and len(row) > q_count_idx) else ""
                    else:
                        # Determine column indices by positional logic
                        is_serial = False
                        try:
                            # Test if the first value is a serial number
                            int(row[0].strip())
                            is_serial = True
                        except ValueError:
                            pass
                        
                        if is_serial:
                            name_idx = 1
                            link_idx = 2
                            logo_idx = 3
                            q_count_idx = 4
                        else:
                            name_idx = 0
                            link_idx = 1
                            logo_idx = 2
                            q_count_idx = 3
                            
                        if len(row) <= name_idx:
                            continue
                            
                        name = row[name_idx].strip()
                        link = row[link_idx].strip() if len(row) > link_idx else ""
                        logo_url = row[logo_idx].strip() if len(row) > logo_idx else ""
                        q_count_input = row[q_count_idx].strip() if len(row) > q_count_idx else ""
                    
                    if not name or not link:
                        continue
                    
                    # Standardize repo_folder
                    name_lower = name.lower()
                    if name_lower in folder_map:
                        folder_lower = folder_map[name_lower]
                    else:
                        folder_lower = name_lower.replace(' ', '-')
                        folder_lower = re.sub(r'[^a-z0-9\-]', '', folder_lower)
                    
                    # Count local questions if com/ folder exists
                    questions_count = 0
                    local_csv = os.path.join(com_dir, folder_lower, 'all.csv')
                    if os.path.exists(local_csv):
                        try:
                            with open(local_csv, 'r', encoding='utf-8') as lf:
                                lreader = csv.reader(lf)
                                next(lreader, None)  # Skip header
                                questions_count = sum(1 for lrow in lreader if lrow)
                        except Exception:
                            pass
                    
                    # Fallback question count logic
                    if q_count_input:
                        # Standardize, e.g. "45" -> "45+ Questions"
                        val = q_count_input.lower().replace('questions', '').replace('question', '').replace('+', '').strip()
                        if val.isdigit():
                            question_count_str = f"{val}+ Questions"
                        else:
                            question_count_str = q_count_input
                    elif questions_count > 0:
                        question_count_str = f"{questions_count}+ Questions"
                    else:
                        # Check existing database company question count
                        existing_comp = Company.objects.filter(repo_folder=folder_lower).first()
                        if existing_comp and "0+" not in existing_comp.question_count:
                            question_count_str = existing_comp.question_count
                        else:
                            question_count_str = "100+ Questions" if folder_lower in ['accenture', 'capgemini', 'cognizant', 'deloitte', 'infosys', 'tcs', 'wipro'] else "50+ Questions"
                    
                    # Update or create database record
                    comp, created = Company.objects.update_or_create(
                        repo_folder=folder_lower,
                        defaults={
                            'name': name,
                            'link': link,
                            'logo_url': logo_url,
                            'question_count': question_count_str,
                            'needs_white_bg': folder_lower in white_bg_folders
                        }
                    )
                    
                    if created:
                        rows_imported += 1
                    else:
                        rows_updated += 1
                        
            # Clean duplicates after bulk import too!
            duplicates = (
                Company.objects.values('name')
                .annotate(name_count=Count('id'))
                .filter(name_count__gt=1)
            )
            count_deleted = 0
            for dup in duplicates:
                dup_name = dup['name']
                records = list(Company.objects.filter(name=dup_name))
                records.sort(
                    key=lambda c: (
                        1 if c.repo_folder else 0,
                        1 if c.link and c.link != '#' else 0,
                        c.id
                    ),
                    reverse=True
                )
                for c in records[1:]:
                    c.delete()
                    count_deleted += 1
            
            cache.delete('sorted_companies')
            msg = f"Bulk import complete! Created {rows_imported} new companies, updated {rows_updated} companies."
            if count_deleted > 0:
                msg += f" Purged {count_deleted} duplicate database records."
            messages.success(request, msg)
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f"Error parsing CSV/TSV data: {e}")
            return redirect('company_bulk_add')
            
    return render(request, 'core/company_bulk_form.html')