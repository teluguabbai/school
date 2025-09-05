from django.contrib import admin

# Register your models here.
# school/admin.py
from django.contrib import admin
from .models import FacultyProfile, StudentProfile, Homework, HomeworkSubmission,Attendance,Marks

admin.site.register(FacultyProfile)
admin.site.register(StudentProfile)
admin.site.register(Homework)
admin.site.register(HomeworkSubmission)
admin.site.register(Attendance)
admin.site.register(Marks)

