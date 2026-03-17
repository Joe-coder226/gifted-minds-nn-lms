"""
URL configuration for elearning project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core.views import home
from core.views import student_signup, admin_signup
from django.contrib.auth import views as auth_views
from core.views import home, student_signup, admin_signup, student_dashboard, admin_dashboard
from core.views import redirect_dashboard
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('', home),
    path('signup/student/', student_signup, name='student_signup'),
    path('signup/admin/', admin_signup, name='admin_signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('student-dashboard/', student_dashboard, name='student_dashboard'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('redirect-dashboard/', redirect_dashboard, name='redirect_dashboard'),

]
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

