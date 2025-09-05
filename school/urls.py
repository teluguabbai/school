from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),

    # Authentication
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('login/', views.user_login, name='user_login'),


    

    # Dashboards
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('faculty-dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('faculty/upload-homework/', views.upload_homework, name='upload_homework'),


    # Attendance
    path('faculty/mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('student/view-attendance/', views.view_attendance, name='view_attendance'),

    # Marks
    path('faculty/add-marks/', views.add_marks, name='add_marks'),
    path('student/view-marks/', views.view_marks, name='view_marks'),

    # Homework
    path('faculty/upload-homework/', views.upload_homework, name='upload_homework'),
    path('student/view-homework/', views.view_homework, name='view_homework'),
    path('student/submit-homework/<int:homework_id>/', views.submit_homework, name='submit_homework'),

    # Admin

    path('faculty/<int:faculty_id>/', views.faculty_detail, name='faculty_detail'),
    path('user-list/', views.user_list, name='user_list'),
    path('add-user-to-group/<int:user_id>/', views.add_user_to_group, name='add_user_to_group'),




    path("add-faculty/", views.add_faculty, name="add_faculty"),
    path("admin/add-faculty/", views.add_faculty, name="add_faculty"),
    path("admin/faculty-list/", views.faculty_list, name="faculty_list"),
    path('admin/add-student/', views.add_student, name='add_student'),
    path('admin/add-faculty/', views.add_faculty, name='add_faculty'),
    path('logout/', views.user_logout, name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),

    path('admin/login/', views.admin_login_view, name='admin_login'),
    path('faculty/login/', views.faculty_login_view, name='faculty_login'),
    path('student/login/', views.student_login_view, name='student_login'),

    path('students/edit/<int:student_id>/', views.edit_student, name='edit_student'),
    path('students/delete/<int:student_id>/', views.delete_student, name='delete_student'),
    path('faculty/edit/<int:faculty_id>/', views.edit_faculty, name='edit_faculty'),
    path('faculty/delete/<int:faculty_id>/', views.delete_faculty, name='delete_faculty'),
    path('faculty-list/', views.faculty_list, name='faculty_list'),
    path('student-list/', views.student_list, name='student_list'),
    path('edit-marks/<int:mark_id>/', views.edit_marks, name='edit_marks'),
    
    path('edit-marks/<int:student_id>/', views.edit_marks, name='edit_marks'),
    path('delete-marks/<int:student_id>/', views.delete_marks, name='delete_marks'),
    path('marks/delete/<int:mark_id>/', views.delete_mark, name='delete_marks'),
    path('add-student/', views.add_student, name='add_student'),
    path('manage-attendance/', views.manage_attendance, name='manage_attendance'),
   
    path('manage-attendance/<int:id>/', views.manage_attendance, name='manage_attendance'),

    path('dashboard/', views.dashboard, name="dashboard"),
    path('student-performance/', views.student_performance, name='student_performance'),
    path("homework/delete/<int:homework_id>/", views.delete_homework, name="delete_homework"),









   
]
