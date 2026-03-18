from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),

    path('signup/admin/', views.admin_signup, name='admin_signup'),
    path('signup/student/', views.student_signup, name='student_signup'),

    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('redirect-dashboard/', views.redirect_dashboard, name='redirect_dashboard'),

    # DASHBOARDS
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),

    # COURSES
    path("create-course/", views.create_course, name="create_course"),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('delete-course/<int:course_id>/', views.delete_course, name='delete_course'),
    path('upload-material/<int:course_id>/', views.upload_material, name='upload_material'),
    path('view-material/<int:material_id>/', views.view_material, name='view_material'),
    path("student-course/<int:course_id>/", views.student_course, name="student_course"),
    path("upload-video/<int:course_id>/", views.upload_video, name="upload_video"),


    # ATTENDANCE
    path('attendance/create/<int:course_id>/', views.create_attendance_session, name='create_attendance_session'),
    path('attendance/mark/<int:session_id>/', views.mark_attendance, name='mark_attendance'),
    path('my-attendance/', views.student_attendance, name='student_attendance'),

    # EXAMS
    path('exam/<int:exam_id>/', views.take_exam, name='take_exam'),
    path('exam/<int:exam_id>/add-question/', views.add_question, name='add_question'),

    # LIVE SESSIONS
    path('live/create/', views.create_live_session, name='create_live_class'),
    path('live/<int:session_id>/', views.live_session_room, name='live_room'),
    path('live/end/<int:session_id>/', views.end_live_session, name='end_live_session'),
    path('live/join/<int:session_id>/', views.join_live_class, name='join_live_class'),

    # PAYMENT
    path('payment/<int:subscription_id>/', views.make_payment, name='make_payment'),

    #MPESA
    path('pay/<int:course_id>/', views.initiate_payment, name='initiate_payment'),
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),

    #SUBSRIPTION
    path('subscription/', views.subscription_page, name='subscription_page'),
    path('subscribe/', views.subscribe, name='subscribe'),

    #CHECK PAYMENT
    path("check-payment/<int:subscription_id>/",views.check_payment,name="check_payment"),

]