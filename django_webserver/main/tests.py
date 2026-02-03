from django.test import TestCase, Client
from django.contrib.auth.models import User
from main.models import Organization, OrganizationUser, DataSource


class OrganizationModelTest(TestCase):
    """Test Organization model"""
    
    def test_create_organization(self):
        org = Organization.objects.create(
            name='Test Org',
            admin_email='admin@test.com'
        )
        self.assertEqual(org.name, 'Test Org')
        self.assertEqual(org.admin_email, 'admin@test.com')
    
    def test_organization_unique_name(self):
        Organization.objects.create(name='Unique Org', admin_email='admin@test.com')
        with self.assertRaises(Exception):
            Organization.objects.create(name='Unique Org', admin_email='other@test.com')


class OrganizationUserModelTest(TestCase):
    """Test OrganizationUser model"""
    
    def setUp(self):
        self.org = Organization.objects.create(name='Test Org', admin_email='admin@test.com')
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='pass123')
    
    def test_create_organization_user(self):
        org_user = OrganizationUser.objects.create(
            user=self.user,
            organization=self.org,
            role='admin'
        )
        self.assertEqual(org_user.role, 'admin')
        self.assertEqual(org_user.user, self.user)
        self.assertEqual(org_user.organization, self.org)
    
    def test_organization_user_unique_together(self):
        OrganizationUser.objects.create(user=self.user, organization=self.org, role='admin')
        with self.assertRaises(Exception):
            OrganizationUser.objects.create(user=self.user, organization=self.org, role='viewer')


class DataSourceModelTest(TestCase):
    """Test DataSource model"""
    
    def setUp(self):
        self.org = Organization.objects.create(name='Test Org', admin_email='admin@test.com')
    
    def test_create_datasource(self):
        ds = DataSource.objects.create(
            organization=self.org,
            name='Test DB',
            source_type='postgresql',
            connection_string='postgresql://user:pass@host/db'
        )
        self.assertEqual(ds.name, 'Test DB')
        self.assertEqual(ds.source_type, 'postgresql')
    
    def test_datasource_unique_together(self):
        DataSource.objects.create(
            organization=self.org,
            name='Unique DS',
            source_type='postgresql',
            connection_string='postgresql://user:pass@host/db'
        )
        with self.assertRaises(Exception):
            DataSource.objects.create(
                organization=self.org,
                name='Unique DS',
                source_type='mysql',
                connection_string='mysql://user:pass@host/db'
            )


class SignupViewTest(TestCase):
    """Test signup functionality"""
    
    def setUp(self):
        self.client = Client()
    
    def test_signup_get(self):
        response = self.client.get('/signup/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup.html')
    
    def test_signup_post_success(self):
        response = self.client.post('/signup/', {
            'org_name': 'New Org',
            'admin_email': 'admin@neworg.com',
            'password': 'SecurePass123!'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to dashboard
        self.assertTrue(Organization.objects.filter(name='New Org').exists())
        self.assertTrue(User.objects.filter(email='admin@neworg.com').exists())
    
    def test_signup_duplicate_org(self):
        Organization.objects.create(name='Existing Org', admin_email='admin@test.com')
        response = self.client.post('/signup/', {
            'org_name': 'Existing Org',
            'admin_email': 'new@test.com',
            'password': 'SecurePass123!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already exists')
    
    def test_signup_missing_fields(self):
        response = self.client.post('/signup/', {
            'org_name': 'New Org',
            'admin_email': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'required')


class DashboardViewTest(TestCase):
    """Test dashboard view"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='pass123')
        self.org = Organization.objects.create(name='Test Org', admin_email='admin@test.com')
        OrganizationUser.objects.create(user=self.user, organization=self.org, role='admin')
    
    def test_dashboard_authenticated(self):
        self.client.login(username='testuser', password='pass123')
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertContains(response, 'Test Org')
    
    def test_dashboard_unauthenticated(self):
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 302)  # Redirect to login


class DataSourceViewTest(TestCase):
    """Test datasource views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', email='admin@test.com', password='pass123')
        self.viewer = User.objects.create_user(username='viewer', email='viewer@test.com', password='pass123')
        self.org = Organization.objects.create(name='Test Org', admin_email='admin@test.com')
        OrganizationUser.objects.create(user=self.user, organization=self.org, role='admin')
        OrganizationUser.objects.create(user=self.viewer, organization=self.org, role='viewer')
    
    def test_add_datasource_admin(self):
        self.client.login(username='admin', password='pass123')
        response = self.client.post(f'/org/{self.org.id}/add-datasource/', {
            'name': 'Test DB',
            'source_type': 'postgresql',
            'connection_string': 'postgresql://user:pass@host/db'
        })
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(DataSource.objects.filter(name='Test DB').exists())
    
    def test_add_datasource_viewer_unauthorized(self):
        self.client.login(username='viewer', password='pass123')
        response = self.client.post(f'/org/{self.org.id}/add-datasource/', {
            'name': 'Test DB',
            'source_type': 'postgresql',
            'connection_string': 'postgresql://user:pass@host/db'
        })
        self.assertEqual(response.status_code, 403)  # Unauthorized
    
    def test_delete_datasource_admin(self):
        self.client.login(username='admin', password='pass123')
        ds = DataSource.objects.create(
            organization=self.org,
            name='Test DB',
            source_type='postgresql',
            connection_string='postgresql://user:pass@host/db'
        )
        response = self.client.post(f'/datasource/{ds.id}/delete/')
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertFalse(DataSource.objects.filter(id=ds.id).exists())


class InviteUserViewTest(TestCase):
    """Test user invitation"""
    
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username='admin', email='admin@test.com', password='pass123')
        self.org = Organization.objects.create(name='Test Org', admin_email='admin@test.com')
        OrganizationUser.objects.create(user=self.admin, organization=self.org, role='admin')
    
    def test_invite_new_user(self):
        self.client.login(username='admin', password='pass123')
        response = self.client.post(f'/org/{self.org.id}/invite-user/', {
            'email': 'newuser@test.com',
            'role': 'viewer'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='newuser@test.com').exists())
        self.assertTrue(OrganizationUser.objects.filter(
            user__email='newuser@test.com',
            organization=self.org,
            role='viewer'
        ).exists())
