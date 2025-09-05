from django import forms
from django.contrib.auth.models import User
from .models import *

# User Registration Forms


class StudentCreationForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['user', 'roll_number', 'class_level', 'department']

from django import forms
from django.contrib.auth.models import User
from .models import FacultyProfile

class FacultyCreationForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    full_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    contact_no = forms.CharField(max_length=20)
    address = forms.CharField(widget=forms.Textarea)
    department = forms.CharField(max_length=100)
    employee_id = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ["username", "full_name", "email", "password", 
                  "contact_no", "address", "department", "employee_id"]

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            first_name=self.cleaned_data["full_name"].split(" ")[0],
            last_name=" ".join(self.cleaned_data["full_name"].split(" ")[1:]) if len(self.cleaned_data["full_name"].split(" ")) > 1 else ""
        )

        faculty = FacultyProfile.objects.create(
            user=user,
            contact_no=self.cleaned_data["contact_no"],
            address=self.cleaned_data["address"],
            department=self.cleaned_data["department"],
            employee_id=self.cleaned_data["employee_id"]
        )
        return user


# Homework Upload by Faculty


class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        exclude = ['faculty']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'})  # HTML5 date picker
        }


# Homework Submission by Student


class HomeworkSubmissionForm(forms.ModelForm):
    class Meta:
        model = HomeworkSubmission
        fields = ['file']
from django import forms
from .models import StudentProfile, FacultyProfile


class StudentEditForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['department', 'roll_number', 'class_level']


class FacultyEditForm(forms.ModelForm):
    class Meta:
        model = FacultyProfile
        fields = ['department', 'employee_id']



from django import forms
from .models import Marks

class MarksForm(forms.ModelForm):
    class Meta:
        model = Marks
        fields = ['subject', 'marks', 'max_marks']




