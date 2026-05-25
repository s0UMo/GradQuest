from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image
from .models import Company

def generate_valid_image_file(filename='test.png'):
    """Helper to generate a valid image file using Pillow."""
    file = BytesIO()
    image = Image.new('RGB', size=(10, 10), color=(255, 0, 0))
    image.save(file, 'png')
    file.seek(0)
    return SimpleUploadedFile(
        name=filename,
        content=file.read(),
        content_type='image/png'
    )

class CompanyAdminTestCase(TestCase):
    def setUp(self):
        # Create a standard admin user (staff)
        self.admin_user = User.objects.create_user(
            username='staffadmin', 
            email='staff@example.com', 
            password='staffpassword123',
            is_staff=True
        )
        # Create a regular user (non-staff)
        self.regular_user = User.objects.create_user(
            username='regularuser', 
            email='user@example.com', 
            password='userpassword123',
            is_staff=False
        )
        
        # Create a company with a valid generated logo
        self.company = Company.objects.create(
            name='Test Company',
            logo=generate_valid_image_file('initial_logo.png'),
            link='https://leetcode.com/',
            question_count='50+ Questions',
            needs_white_bg=True
        )

    def test_index_view(self):
        """Home page should render successfully and list companies."""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Company')
        self.assertContains(response, 'Admin Login')

    def test_login_view_get(self):
        """Login page should load successfully."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign In')

    def test_login_success(self):
        """Admin should be able to log in and be redirected to dashboard."""
        response = self.client.post(reverse('login'), {
            'username': 'staffadmin',
            'password': 'staffpassword123'
        })
        self.assertRedirects(response, reverse('dashboard'))

    def test_login_denied_for_non_staff(self):
        """Non-staff user should log in but access should be denied."""
        response = self.client.post(reverse('login'), {
            'username': 'regularuser',
            'password': 'userpassword123'
        })
        # Stays on login page with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Access denied')

    def test_dashboard_unauthorized_redirect(self):
        """Anonymous user should be redirected to login page when trying to access dashboard."""
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")

    def test_dashboard_regular_user_denied(self):
        """Non-staff logged-in user should get 403 Forbidden on dashboard."""
        self.client.login(username='regularuser', password='userpassword123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_dashboard_authorized(self):
        """Staff user should access dashboard successfully."""
        self.client.login(username='staffadmin', password='staffpassword123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Company')
        self.assertContains(response, 'Manage Companies')

    def test_create_company(self):
        """Staff user can create a new company record."""
        self.client.login(username='staffadmin', password='staffpassword123')
        new_logo = generate_valid_image_file('new_logo.png')
        response = self.client.post(reverse('company_create'), {
            'name': 'Created Company',
            'logo': new_logo,
            'link': 'https://leetcode.com/problem-list/example/',
            'question_count': '10+ Questions',
            'needs_white_bg': False
        })
        if response.status_code == 200:
            print("Create company errors:", response.context['form'].errors)
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(Company.objects.filter(name='Created Company').exists())

    def test_edit_company(self):
        """Staff user can edit an existing company record without changing the logo."""
        self.client.login(username='staffadmin', password='staffpassword123')
        # We omit the logo field to simulate keeping the original logo
        response = self.client.post(reverse('company_edit', args=[self.company.pk]), {
            'name': 'Updated Company Name',
            'link': 'https://leetcode.com/problem-list/updated/',
            'question_count': '99+ Questions',
            'needs_white_bg': False
        })
        if response.status_code == 200:
            print("Edit company errors:", response.context['form'].errors)
        self.assertRedirects(response, reverse('dashboard'))
        self.company.refresh_from_db()
        self.assertEqual(self.company.name, 'Updated Company Name')
        self.assertEqual(self.company.question_count, '99+ Questions')

    def test_delete_company(self):
        """Staff user can delete a company record."""
        self.client.login(username='staffadmin', password='staffpassword123')
        response = self.client.post(reverse('company_delete', args=[self.company.pk]))
        self.assertRedirects(response, reverse('dashboard'))
        self.assertFalse(Company.objects.filter(pk=self.company.pk).exists())

    def test_pyq_redirect_default(self):
        """PYQ redirect view uses default URL when no SiteSetting is saved."""
        response = self.client.get(reverse('pyq'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'https://drive.google.com/drive/folders/1VT_6K9Q1zfIdbDLjf96YrsyEk3hfbMvX?usp=sharing')

    def test_pyq_update_link_success(self):
        """Staff user can successfully update the PYQ link and it updates the database."""
        self.client.login(username='staffadmin', password='staffpassword123')
        test_url = 'https://example.com/custom-pyq-link/'
        response = self.client.post(reverse('update_pyq_link'), {'pyq_link': test_url})
        self.assertRedirects(response, reverse('dashboard'))
        
        # Verify it updated in DB
        from .models import SiteSetting
        setting = SiteSetting.objects.first()
        self.assertIsNotNone(setting)
        self.assertEqual(setting.pyq_link, test_url)
        
        # Verify the redirect template now uses this link
        response_pyq = self.client.get(reverse('pyq'))
        self.assertEqual(response_pyq.status_code, 200)
        self.assertContains(response_pyq, test_url)

    def test_pyq_update_link_unauthorized(self):
        """Non-staff and anonymous users cannot update the PYQ link."""
        test_url = 'https://example.com/hacked-link/'
        
        # Anonymous user
        response = self.client.post(reverse('update_pyq_link'), {'pyq_link': test_url})
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('update_pyq_link')}")
        
        # Non-staff user
        self.client.login(username='regularuser', password='userpassword123')
        response = self.client.post(reverse('update_pyq_link'), {'pyq_link': test_url})
        self.assertEqual(response.status_code, 403)

    def test_pyq_update_link_empty(self):
        """Staff user can successfully clear the PYQ link (set to empty string)."""
        self.client.login(username='staffadmin', password='staffpassword123')
        response = self.client.post(reverse('update_pyq_link'), {'pyq_link': ''})
        self.assertRedirects(response, reverse('dashboard'))
        
        # Verify it updated in DB to empty
        from .models import SiteSetting
        setting = SiteSetting.objects.first()
        self.assertIsNotNone(setting)
        self.assertEqual(setting.pyq_link, '')
        
        # Verify the redirect view redirects to home with coming_soon=true
        response_pyq = self.client.get(reverse('pyq'))
        self.assertRedirects(response_pyq, '/?coming_soon=true')


    def test_create_company_with_logo_url(self):
        """Staff user can create a new company using only a logo_url link instead of uploading a file."""
        self.client.login(username='staffadmin', password='staffpassword123')
        response = self.client.post(reverse('company_create'), {
            'name': 'Imgur Logo Company',
            'logo_url': 'https://i.imgur.com/example.png',
            'link': 'https://leetcode.com/problem-list/example-2/',
            'question_count': '15+ Questions',
            'needs_white_bg': True
        })
        self.assertRedirects(response, reverse('dashboard'))
        company = Company.objects.get(name='Imgur Logo Company')
        self.assertEqual(company.logo_url, 'https://i.imgur.com/example.png')
        self.assertEqual(company.get_logo_url, 'https://i.imgur.com/example.png')
        self.assertFalse(company.logo)

    def test_create_company_requires_at_least_one_logo(self):
        """Creating a company fails validation if both logo file and logo_url are omitted."""
        self.client.login(username='staffadmin', password='staffpassword123')
        response = self.client.post(reverse('company_create'), {
            'name': 'No Logo Company',
            'link': 'https://leetcode.com/problem-list/example-3/',
            'question_count': '5+ Questions',
            'needs_white_bg': True
        })
        self.assertEqual(response.status_code, 200) # Form returns errors
        form = response.context['form']
        self.assertIn("Please provide either a logo file upload or a direct logo image URL.", form.non_field_errors())
        self.assertFalse(Company.objects.filter(name='No Logo Company').exists())

    def test_change_credentials_unauthorized(self):
        """Anonymous and non-staff users cannot change credentials."""
        url = reverse('change_credentials')
        # Anonymous
        response = self.client.post(url, {
            'current_password': 'staffpassword123',
            'new_username': 'newadmin'
        })
        self.assertRedirects(response, f"{reverse('login')}?next={url}")

        # Non-staff
        self.client.login(username='regularuser', password='userpassword123')
        response = self.client.post(url, {
            'current_password': 'staffpassword123',
            'new_username': 'newadmin'
        })
        self.assertEqual(response.status_code, 403)

    def test_change_credentials_incorrect_current_password(self):
        """Fails to change credentials when current password is incorrect."""
        self.client.login(username='staffadmin', password='staffpassword123')
        response = self.client.post(reverse('change_credentials'), {
            'current_password': 'wrongpassword',
            'new_username': 'newadmin'
        })
        self.assertRedirects(response, reverse('dashboard'))
        # Check that user username didn't change
        self.admin_user.refresh_from_db()
        self.assertEqual(self.admin_user.username, 'staffadmin')

    def test_change_credentials_success_username_only(self):
        """Successfully updates the username only."""
        self.client.login(username='staffadmin', password='staffpassword123')
        response = self.client.post(reverse('change_credentials'), {
            'current_password': 'staffpassword123',
            'new_username': 'newstaffadmin'
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.admin_user.refresh_from_db()
        self.assertEqual(self.admin_user.username, 'newstaffadmin')

    def test_change_credentials_success_password_only(self):
        """Successfully updates the password only."""
        self.client.login(username='staffadmin', password='staffpassword123')
        response = self.client.post(reverse('change_credentials'), {
            'current_password': 'staffpassword123',
            'new_password': 'newpassword123',
            'confirm_new_password': 'newpassword123'
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.admin_user.refresh_from_db()
        self.assertTrue(self.admin_user.check_password('newpassword123'))

    def test_change_credentials_mismatch_passwords(self):
        """Fails when new password and confirmation do not match."""
        self.client.login(username='staffadmin', password='staffpassword123')
        response = self.client.post(reverse('change_credentials'), {
            'current_password': 'staffpassword123',
            'new_password': 'newpassword123',
            'confirm_new_password': 'differentpassword'
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.admin_user.refresh_from_db()
        self.assertFalse(self.admin_user.check_password('newpassword123'))

    def test_change_credentials_username_taken(self):
        """Fails when the requested new username is already taken by another user."""
        self.client.login(username='staffadmin', password='staffpassword123')
        response = self.client.post(reverse('change_credentials'), {
            'current_password': 'staffpassword123',
            'new_username': 'regularuser' # Already exists
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.admin_user.refresh_from_db()
        self.assertEqual(self.admin_user.username, 'staffadmin')

    def test_companies_sorted_alphabetically(self):
        """Verify that companies are sorted alphabetically by name on the index page and dashboard."""
        # Create additional companies out of order
        Company.objects.create(
            name='Zebra Corp',
            link='https://leetcode.com/zebra',
            question_count='10+ Questions',
            logo_url='https://example.com/logo.png'
        )
        Company.objects.create(
            name='Alpha Solutions',
            link='https://leetcode.com/alpha',
            question_count='20+ Questions',
            logo_url='https://example.com/logo.png'
        )
        
        # Test index view ordering
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        companies_in_context = list(response.context['companies'])
        names = [c.name for c in companies_in_context]
        # Should be sorted: 'Alpha Solutions', 'Test Company', 'Zebra Corp'
        self.assertEqual(names, sorted(names, key=str.lower))

        # Test dashboard view ordering (staff user required)
        self.client.login(username='staffadmin', password='staffpassword123')
        response_dash = self.client.get(reverse('dashboard'))
        self.assertEqual(response_dash.status_code, 200)
        companies_dash = list(response_dash.context['companies'])
        names_dash = [c.name for c in companies_dash]
        self.assertEqual(names_dash, sorted(names_dash, key=str.lower))


from django.core.cache import cache

class CompanyCacheTestCase(TestCase):
    def setUp(self):
        # Clear cache before each test
        cache.clear()
        self.company = Company.objects.create(
            name='Cached Company',
            link='https://leetcode.com/',
            question_count='50+ Questions',
            logo_url='https://example.com/logo.png'
        )

    def test_cache_is_created_on_index_view(self):
        """Home page hit should generate the 'sorted_companies' cache key."""
        self.assertIsNone(cache.get('sorted_companies'))
        
        # Hit homepage
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        
        # Verify cache contains the company
        cached_data = cache.get('sorted_companies')
        self.assertIsNotNone(cached_data)
        self.assertEqual(len(cached_data), 1)
        self.assertEqual(cached_data[0].name, 'Cached Company')

    def test_cache_invalidated_on_save(self):
        """Saving a company (new or update) must clear the 'sorted_companies' cache."""
        # Warm up the cache
        self.client.get(reverse('index'))
        self.assertIsNotNone(cache.get('sorted_companies'))
        
        # Update the company
        self.company.name = 'Updated Cached Company'
        self.company.save()
        
        # Verify cache is cleared
        self.assertIsNone(cache.get('sorted_companies'))

    def test_cache_invalidated_on_delete(self):
        """Deleting a company must clear the 'sorted_companies' cache."""
        # Warm up the cache
        self.client.get(reverse('index'))
        self.assertIsNotNone(cache.get('sorted_companies'))
        
        # Delete the company
        self.company.delete()
        
        # Verify cache is cleared
        self.assertIsNone(cache.get('sorted_companies'))


class BulkOperationsTestCase(TestCase):
    def setUp(self):
        # Create standard admin user (staff)
        self.admin_user = User.objects.create_user(
            username='staffadmin', 
            email='staff@example.com', 
            password='staffpassword123',
            is_staff=True
        )
        # Create regular user (non-staff)
        self.regular_user = User.objects.create_user(
            username='regularuser', 
            email='user@example.com', 
            password='userpassword123',
            is_staff=False
        )
        
        # Seed 3 companies
        Company.objects.create(name='Apple', repo_folder='apple', link='https://leetcode.com/apple')
        Company.objects.create(name='Amazon', repo_folder='amazon', link='https://leetcode.com/amazon')
        Company.objects.create(name='Google', repo_folder='google', link='https://leetcode.com/google')

    def test_delete_all_companies_unauthorized(self):
        """Anonymous or regular users cannot delete all companies."""
        url = reverse('delete_all_companies')
        
        # Anonymous
        response = self.client.post(url, {'password': 'staffpassword123'})
        self.assertRedirects(response, f"{reverse('login')}?next={url}")
        self.assertEqual(Company.objects.count(), 3)
        
        # Regular user
        self.client.login(username='regularuser', password='userpassword123')
        response = self.client.post(url, {'password': 'staffpassword123'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Company.objects.count(), 3)

    def test_delete_all_companies_incorrect_password(self):
        """Deleting all companies fails when re-entering an incorrect password."""
        self.client.login(username='staffadmin', password='staffpassword123')
        url = reverse('delete_all_companies')
        
        response = self.client.post(url, {'password': 'wrongpassword'})
        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(Company.objects.count(), 3)

    def test_delete_all_companies_success(self):
        """Deleting all companies succeeds when re-entering the correct password."""
        self.client.login(username='staffadmin', password='staffpassword123')
        url = reverse('delete_all_companies')
        
        response = self.client.post(url, {'password': 'staffpassword123'})
        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(Company.objects.count(), 0)

    def test_bulk_add_companies_unauthorized(self):
        """Anonymous or regular users cannot access bulk add views."""
        url = reverse('company_bulk_add')
        
        # Anonymous
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('login')}?next={url}")
        
        # Regular user
        self.client.login(username='regularuser', password='userpassword123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_bulk_add_companies_success_csv(self):
        """Staff user can successfully bulk add companies using CSV data."""
        self.client.login(username='staffadmin', password='staffpassword123')
        url = reverse('company_bulk_add')
        
        csv_data = (
            "Name,Link,Logo URL\n"
            "Meta,https://leetcode.com/meta,https://img.logo.dev/meta.com\n"
            "Netflix,https://leetcode.com/netflix,https://img.logo.dev/netflix.com\n"
        )
        
        response = self.client.post(url, {'bulk_data': csv_data})
        self.assertRedirects(response, reverse('dashboard'))
        
        # Verify both Netflix and Meta were created
        self.assertTrue(Company.objects.filter(name='Meta').exists())
        self.assertTrue(Company.objects.filter(name='Netflix').exists())
        
        meta = Company.objects.get(name='Meta')
        self.assertEqual(meta.link, 'https://leetcode.com/meta')
        self.assertEqual(meta.logo_url, 'https://img.logo.dev/meta.com')

    def test_bulk_add_companies_success_tsv(self):
        """Staff user can successfully bulk add companies using tab-separated data."""
        self.client.login(username='staffadmin', password='staffpassword123')
        url = reverse('company_bulk_add')
        
        tsv_data = (
            "Name\tLink\tLogo URL\n"
            "Microsoft\thttps://leetcode.com/microsoft\thttps://img.logo.dev/microsoft.com\n"
        )
        
        response = self.client.post(url, {'bulk_data': tsv_data})
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(Company.objects.filter(name='Microsoft').exists())

    def test_bulk_add_companies_with_question_count(self):
        """Staff user can successfully bulk add companies specifying question counts explicitly."""
        self.client.login(username='staffadmin', password='staffpassword123')
        url = reverse('company_bulk_add')
        
        csv_data = (
            "Name,Link,Logo URL,Question Count\n"
            "Meta,https://leetcode.com/meta,https://img.logo.dev/meta.com,125\n"
            "Netflix,https://leetcode.com/netflix,https://img.logo.dev/netflix.com,45+ Questions\n"
            "Adobe,https://leetcode.com/adobe,https://img.logo.dev/adobe.com,90+\n"
        )
        
        response = self.client.post(url, {'bulk_data': csv_data})
        self.assertRedirects(response, reverse('dashboard'))
        
        # Verify Meta question count got standardized
        meta = Company.objects.get(name='Meta')
        self.assertEqual(meta.question_count, '125+ Questions')
        
        # Verify Netflix kept its string representation
        netflix = Company.objects.get(name='Netflix')
        self.assertEqual(netflix.question_count, '45+ Questions')
        
        # Verify Adobe kept its string representation
        adobe = Company.objects.get(name='Adobe')
        self.assertEqual(adobe.question_count, '90+ Questions')



