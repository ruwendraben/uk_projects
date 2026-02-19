from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from .models import Organization, OrganizationUser, DataSource
import sqlalchemy


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint for ALB - no auth required."""
    return HttpResponse("OK", status=200)


def index(request):
    """Home page - redirect to signup if not authenticated."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('signup')


@require_http_methods(["GET", "POST"])
def signup(request):
    """Organization signup."""
    if request.method == 'POST':
        org_name = request.POST.get('org_name', '').strip()
        admin_email = request.POST.get('admin_email', '').strip()
        password = request.POST.get('password', '').strip()
        
        # Validation
        if not all([org_name, admin_email, password]):
            return render(request, 'signup.html', {'error': 'All fields are required'})
        
        if Organization.objects.filter(name=org_name).exists():
            return render(request, 'signup.html', {'error': 'Organization name already exists'})
        
        if User.objects.filter(email=admin_email).exists():
            return render(request, 'signup.html', {'error': 'Email already registered'})
        
        # Create organization
        org = Organization.objects.create(name=org_name, admin_email=admin_email)
        
        # Create user
        user = User.objects.create_user(
            username=admin_email,
            email=admin_email,
            password=password,
            first_name=admin_email.split('@')[0]
        )
        
        # Link user to org as admin
        OrganizationUser.objects.create(user=user, organization=org, role='admin')
        
        # Auto-login
        auth_login(request, user)
        return redirect('dashboard')
    
    return render(request, 'signup.html')


@login_required
def dashboard(request):
    """User dashboard showing their organizations."""
    user_orgs = OrganizationUser.objects.filter(user=request.user).select_related('organization')
    return render(request, 'dashboard.html', {'user_orgs': user_orgs})


@login_required
def org_detail(request, org_id):
    """Organization detail page with data sources."""
    try:
        org_user = OrganizationUser.objects.get(user=request.user, organization_id=org_id)
        org = org_user.organization
        data_sources = DataSource.objects.filter(organization=org)
        org_members = OrganizationUser.objects.filter(organization=org).select_related('user')
        return render(request, 'org_detail.html', {
            'org': org,
            'org_user': org_user,
            'data_sources': data_sources,
            'org_members': org_members
        })
    except OrganizationUser.DoesNotExist:
        return HttpResponse('Unauthorized', status=403)


@login_required
@require_http_methods(["GET", "POST"])
def add_datasource(request, org_id):
    """Add a data source to an organization."""
    try:
        org_user = OrganizationUser.objects.get(user=request.user, organization_id=org_id)
        
        # Only admins can add datasources
        if org_user.role != 'admin':
            return HttpResponse('Unauthorized', status=403)
        
        if request.method == 'POST':
            name = request.POST.get('name', '').strip()
            source_type = request.POST.get('source_type', '').strip()
            connection_string = request.POST.get('connection_string', '').strip()
            
            if not all([name, source_type, connection_string]):
                return render(request, 'org_detail.html', {
                    'org': org_user.organization,
                    'org_user': org_user,
                    'data_sources': DataSource.objects.filter(organization=org_user.organization),
                    'error': 'All fields are required'
                })
            
            # Check for duplicate name
            if DataSource.objects.filter(organization=org_user.organization, name=name).exists():
                return render(request, 'org_detail.html', {
                    'org': org_user.organization,
                    'org_user': org_user,
                    'data_sources': DataSource.objects.filter(organization=org_user.organization),
                    'error': f'Data source "{name}" already exists for this organization'
                })
            
            DataSource.objects.create(
                organization=org_user.organization,
                name=name,
                source_type=source_type,
                connection_string=connection_string
            )
            return redirect('org_detail', org_id=org_id)
        
        return redirect('org_detail', org_id=org_id)
    except OrganizationUser.DoesNotExist:
        return HttpResponse('Unauthorized', status=403)


@login_required
@require_http_methods(["POST"])
def delete_datasource(request, datasource_id):
    """Delete a data source."""
    try:
        ds = DataSource.objects.get(id=datasource_id)
        org_user = OrganizationUser.objects.get(user=request.user, organization=ds.organization)
        
        # Only admins can delete
        if org_user.role != 'admin':
            return HttpResponse('Unauthorized', status=403)
        
        org_id = ds.organization.id
        ds.delete()
        return redirect('org_detail', org_id=org_id)
    except (DataSource.DoesNotExist, OrganizationUser.DoesNotExist):
        return HttpResponse('Not found', status=404)


@login_required
@require_http_methods(["POST"])
def invite_user(request, org_id):
    """Invite a user to an organization."""
    try:
        org_user = OrganizationUser.objects.get(user=request.user, organization_id=org_id)
        
        # Only admins can invite
        if org_user.role != 'admin':
            return HttpResponse('Unauthorized', status=403)
        
        email = request.POST.get('email', '').strip().lower()
        role = request.POST.get('role', 'viewer').strip()
        
        if not email:
            return redirect('org_detail', org_id=org_id)
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Create a new user with a temporary password
            user = User.objects.create_user(
                username=email,
                email=email,
                password=User.objects.make_random_password()
            )
        
        # Check if already in organization
        if OrganizationUser.objects.filter(user=user, organization_id=org_id).exists():
            return redirect('org_detail', org_id=org_id)
        
        # Add user to organization
        OrganizationUser.objects.create(
            user=user,
            organization_id=org_id,
            role=role
        )
        
        return redirect('org_detail', org_id=org_id)
    except OrganizationUser.DoesNotExist:
        return HttpResponse('Unauthorized', status=403)


@login_required
def explore_datasource(request, datasource_id):
    """Explore datasource schema (tables, columns, types)."""
    try:
        ds = DataSource.objects.get(id=datasource_id)
        OrganizationUser.objects.get(user=request.user, organization=ds.organization)
        
        try:
            if ds.source_type in ['postgresql', 'mysql']:
                engine = sqlalchemy.create_engine(ds.connection_string, connect_args={'connect_timeout': 5})
                inspector = sqlalchemy.inspect(engine)
                
                tables_info = []
                for table_name in inspector.get_table_names():
                    columns = inspector.get_columns(table_name)
                    columns_info = [
                        {
                            'name': col['name'],
                            'type': str(col['type']),
                            'nullable': col['nullable']
                        }
                        for col in columns
                    ]
                    tables_info.append({
                        'name': table_name,
                        'columns': columns_info
                    })
                
                return render(request, 'explore.html', {
                    'datasource': ds,
                    'tables': tables_info
                })
            else:
                return HttpResponse('Unsupported datasource type', status=400)
        except Exception as e:
            return render(request, 'explore.html', {
                'datasource': ds,
                'error': str(e),
                'tables': []
            })
    except (DataSource.DoesNotExist, OrganizationUser.DoesNotExist):
        return HttpResponse('Unauthorized', status=403)


@login_required
def preview_table(request, datasource_id, table_name):
    """Preview sample data from a table."""
    try:
        ds = DataSource.objects.get(id=datasource_id)
        OrganizationUser.objects.get(user=request.user, organization=ds.organization)
        
        try:
            if ds.source_type in ['postgresql', 'mysql']:
                engine = sqlalchemy.create_engine(ds.connection_string, connect_args={'connect_timeout': 5})
                query = sqlalchemy.text(f"SELECT * FROM {table_name} LIMIT 10")
                
                with engine.connect() as conn:
                    result = conn.execute(query)
                    columns = list(result.keys())
                    rows = [dict(row._mapping) for row in result.fetchall()]
                    
                    return JsonResponse({
                        'status': 'success',
                        'table': table_name,
                        'columns': columns,
                        'rows': rows
                    })
            else:
                return JsonResponse({'status': 'error', 'message': 'Unsupported source type'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    except (DataSource.DoesNotExist, OrganizationUser.DoesNotExist):
        return HttpResponse('Unauthorized', status=403)


@login_required
def test_connection(request, datasource_id):
    """Test data source connection."""
    try:
        ds = DataSource.objects.get(id=datasource_id)
        OrganizationUser.objects.get(user=request.user, organization=ds.organization)
        
        try:
            if ds.source_type in ['postgresql', 'mysql']:
                engine = sqlalchemy.create_engine(ds.connection_string, connect_args={'connect_timeout': 5})
                with engine.connect() as conn:
                    result = conn.execute(sqlalchemy.text("SELECT 1"))
                    return JsonResponse({'status': 'success', 'message': 'Connection successful!'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Unsupported source type'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    except (DataSource.DoesNotExist, OrganizationUser.DoesNotExist):
        return HttpResponse('Not found', status=404)
