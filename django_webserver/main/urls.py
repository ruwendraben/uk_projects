from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('org/<int:org_id>/', views.org_detail, name='org_detail'),
    path('org/<int:org_id>/add-datasource/', views.add_datasource, name='add_datasource'),
    path('org/<int:org_id>/invite-user/', views.invite_user, name='invite_user'),
    path('datasource/<int:datasource_id>/delete/', views.delete_datasource, name='delete_datasource'),
    path('datasource/<int:datasource_id>/test/', views.test_connection, name='test_connection'),
    path('datasource/<int:datasource_id>/explore/', views.explore_datasource, name='explore_datasource'),
    path('datasource/<int:datasource_id>/preview/<str:table_name>/', views.preview_table, name='preview_table'),
]
