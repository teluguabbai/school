from django.db import models
from django.contrib.auth.models import User



# STUDENT PROFILE
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20) 
    class_level = models.CharField(max_length=50)  

    def __str__(self):
        return self.user.username

# FACULTY PROFILE



class FacultyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact_no = models.CharField(max_length=20)
    address = models.TextField()
    department = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=50) 

    def __str__(self):
        return self.user.username
    def __str__(self):
        return f"{self.user.username} - {self.department}"


# ATTENDANCE MODEL
class Attendance(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    date = models.DateField()
    status_choices = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Leave', 'Leave'),
    ]
    status = models.CharField(max_length=10, choices=status_choices)

    def __str__(self):
        return f"{self.student.user.username} - {self.date} - {self.status}"

# MARKS MODEL
class Marks(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    marks = models.FloatField()
    max_marks = models.FloatField(default=100.0)
    grade = models.CharField(max_length=2, blank=True)
    exam_type = models.CharField(max_length=100) 

    def save(self, *args, **kwargs):
        # Auto-generate grade based on percentage
        percentage = (self.marks / self.max_marks) * 100
        if percentage >= 90:
            self.grade = 'A+'
        elif percentage >= 80:
            self.grade = 'A'
        elif percentage >= 70:
            self.grade = 'B+'
        elif percentage >= 60:
            self.grade = 'B'
        elif percentage >= 50:
            self.grade = 'C'
        else:
            self.grade = 'F'
        super(Marks, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.user.username} - {self.subject} - {self.marks}/{self.max_marks} ({self.grade})"



# HOMEWORK MODEL 

class Homework(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    faculty = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE)
    assigned_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    

    def __str__(self):
        return f"{self.title} - {self.faculty.user.username}"


class HomeworkSubmission(models.Model):
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    submitted_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='homework_submissions/')

    def __str__(self):
        return f"{self.student.user.username} - {self.homework.title} Submission"
from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=20, unique=True)
    class_level = models.CharField(max_length=20)
    department = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.username} - {self.roll_number}"

from django.db import models

class Timetable(models.Model):
    class_name = models.CharField(max_length=50)  # e.g. "10th A"
    monday = models.CharField(max_length=100, blank=True, null=True)
    tuesday = models.CharField(max_length=100, blank=True, null=True)
    wednesday = models.CharField(max_length=100, blank=True, null=True)
    thursday = models.CharField(max_length=100, blank=True, null=True)
    friday = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.class_name
