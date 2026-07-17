from django.contrib import admin
from .models import Attendance, Student, Course

admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Attendance)
