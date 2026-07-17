from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add/', views.add_student, name='add_student'),
    path('edit/<int:id>/', views.edit_student, name='edit_student'),
    path('delete/<int:id>/', views.delete_student, name='delete_student'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('student/<int:id>/', views.student_detail, name='student_detail'),

    path('export-pdf/', views.export_pdf, name='export_pdf'),
    path('export-excel/', views.export_excel, name='export_excel'),
    path('id-card/<int:id>/', views.student_id_card, name='student_id_card'),
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/edit/<int:id>/', views.edit_attendance, name='edit_attendance'),
    path('attendance/delete/<int:id>/', views.delete_attendance, name='delete_attendance'),


    
    
]