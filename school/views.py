from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import *
from .forms import *
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group

from django.shortcuts import render
from django.db.models import Avg, Count
from django.utils import timezone
from calendar import monthrange
from datetime import date
from .models import StudentProfile, FacultyProfile, Marks, Attendance
import json
import json
from datetime import date
from calendar import monthrange
from django.db.models import Avg
from django.utils import timezone
from django.shortcuts import render
from .models import StudentProfile, FacultyProfile, Attendance, Marks

import json
from datetime import date
from calendar import monthrange
from django.db.models import Avg
from django.utils import timezone
from django.shortcuts import render
from .models import StudentProfile, FacultyProfile, Attendance, Marks
from django.db.models import Avg
from django.utils import timezone
from calendar import monthrange
from datetime import date
import json
@login_required
def dashboard(request):
    # Count totals
    total_students = StudentProfile.objects.count()
    total_faculty = FacultyProfile.objects.count()

    # ✅ Class-wise average marks
    class_wise_marks = (
        Marks.objects.values('student__class_level')
        .annotate(avg_marks=Avg('marks'))
        .order_by('student__class_level')
    )

    class_labels = [f"Class {item['student__class_level']}" for item in class_wise_marks]
    avg_marks = [round(item['avg_marks'], 2) if item['avg_marks'] else 0 for item in class_wise_marks]

    # ✅ Attendance calculations (current month)
    today = timezone.now().date()
    first_day = date(today.year, today.month, 1)
    last_day = date(today.year, today.month, monthrange(today.year, today.month)[1])

    avg_attendance = []
    for item in class_wise_marks:
        class_level = item["student__class_level"]
        students = StudentProfile.objects.filter(class_level=class_level)

        total_present = 0
        total_days = 0

        for student in students:
            total = Attendance.objects.filter(student=student, date__range=(first_day, last_day)).count()
            present = Attendance.objects.filter(student=student, date__range=(first_day, last_day), status="Present").count()
            if total > 0:
                total_present += (present / total) * 100
                total_days += 1

        avg_attendance.append(round(total_present / total_days, 2) if total_days > 0 else 0)

    # ✅ Group low attendance students by class
    low_attendance_students = {}
    all_students = StudentProfile.objects.all()
    for student in all_students:
        total = Attendance.objects.filter(student=student, date__range=(first_day, last_day)).count()
        present = Attendance.objects.filter(student=student, date__range=(first_day, last_day), status="Present").count()
        if total > 0:
            attendance_percentage = round((present / total) * 100, 2)
            if attendance_percentage < 75:
                cls = student.class_level
                if cls not in low_attendance_students:
                    low_attendance_students[cls] = []
                low_attendance_students[cls].append({
                    "name": student.user.get_full_name(),
                    "attendance": attendance_percentage
                })

    # ✅ Group failed students by class -> exam type (based on %)
    failed_students = {}
    for student in all_students:
        student_marks = Marks.objects.filter(student=student)
        if student_marks.exists():
            exam_groups = student_marks.values("exam_type").distinct()
            for exam in exam_groups:
                exam_type = exam["exam_type"]
                exam_marks = student_marks.filter(exam_type=exam_type)

                # Calculate average percentage across subjects in this exam
                percentages = []
                for m in exam_marks:
                    if m.max_marks and m.marks is not None:
                        percent = (m.marks / m.max_marks) * 100
                        percentages.append(percent)

                if percentages:
                    avg_percent = sum(percentages) / len(percentages)
                    if avg_percent < 40:  # fail if avg% < 40
                        cls = student.class_level
                        if cls not in failed_students:
                            failed_students[cls] = {}
                        if exam_type not in failed_students[cls]:
                            failed_students[cls][exam_type] = []
                        failed_students[cls][exam_type].append({
                            "name": student.user.get_full_name(),
                            "avg_marks": round(avg_percent, 2)
                        })

    # ✅ Send data to template
    context = {
        'total_students': total_students,
        'total_faculty': total_faculty,
        'class_labels': json.dumps(class_labels),
        'avg_marks': json.dumps(avg_marks),
        'avg_attendance': json.dumps(avg_attendance),
        'low_attendance_students': low_attendance_students,
        'failed_students': failed_students,
    }
    return render(request, "dashboard.html", context)



def user_list(request):
    # Get all users
    all_users = User.objects.all()

    # Get groups
    groups = Group.objects.all()

    # Categorize users by group
    admins = User.objects.filter(groups__name="Admin")
    faculty = User.objects.filter(groups__name="Faculty")
    students = User.objects.filter(groups__name="Student")

    context = {
        'all_users': all_users,
        'admins': admins,
        'faculty': faculty,
        'students': students,
        'groups': groups,
    }
    return render(request, 'user_list.html', context)


def add_user_to_group(request, user_id):
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)
        group_id = request.POST.get("group_id")
        if group_id:
            group = get_object_or_404(Group, id=group_id)
            user.groups.add(group)
        return redirect('user_list')  # Make sure this matches your URL name



# Role Checkers
# --------------------------
def is_admin(user):
    return user.groups.filter(name='Admin').exists()

def is_faculty(user):
    return user.groups.filter(name='Faculty').exists()

def is_student(user):
    return user.groups.filter(name='Student').exists()

# --------------------------
# Home Page / Login Redirect
# --------------------------
def home(request):
    if request.user.is_authenticated:
        if is_admin(request.user):
            return redirect('admin_dashboard')
        elif is_faculty(request.user):
            return redirect('faculty_dashboard')
        elif is_student(request.user):
            return redirect('student_dashboard')
        
    faculty_list = FacultyProfile.objects.select_related('user').all()
    timetables = Timetable.objects.all()
    return render(request, "home.html", {
        "faculty_list": faculty_list,
        "timetables": timetables
    })
    

# --------------------------
# Login View
# --------------------------

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Redirect based on group
            if user.groups.filter(name='Admin').exists():
                return redirect('admin_dashboard')
            elif user.groups.filter(name='Faculty').exists():
                return redirect('faculty_dashboard')
            elif user.groups.filter(name='Student').exists():
                return redirect('student_dashboard')
            else:
                messages.error(request, "No role assigned. Contact admin.")
                return redirect('login')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})
# --------------------------
# Logout out
# --------------------------
def user_logout(request):
    logout(request)  
    return redirect('login') 

# --------------------------
# Admin Dashboard
# --------------------------
from .models import Marks 
@login_required
@user_passes_test(is_admin)

def admin_dashboard(request):
    students = StudentProfile.objects.all()
    faculty = FacultyProfile.objects.all()
    today = timezone.now().date()
    first_day = date(today.year, today.month, 1)
    last_day = date(today.year, today.month, monthrange(today.year, today.month)[1])

    # Attach attendance percentage directly to each student
    for student in students:
        total_days = Attendance.objects.filter(
            student=student, date__range=(first_day, last_day)
        ).count()
        present_days = Attendance.objects.filter(
            student=student, date__range=(first_day, last_day), status="Present"
        ).count()
        percentage = (present_days / total_days * 100) if total_days > 0 else 0

        # Add dynamic attributes for template use
        student.attendance_percentage = round(percentage, 2)
        student.total_days = total_days
        student.present_days = present_days
        student.absent_days = total_days - present_days
        student.low_attendance = percentage < 75

    marks = Marks.objects.all()

    return render(request, 'admin_dashbord.html', {
        'students': students,
        'faculty': faculty,
        'marks': marks,
    })
# --------------------------
# Faculty Dashboard
# --------------------------
from datetime import date
from calendar import monthrange
from django.utils import timezone
from django.shortcuts import render
from .models import StudentProfile, Attendance
from collections import defaultdict
from django.contrib.auth.decorators import login_required, user_passes_test

from collections import defaultdict
from calendar import monthrange
from datetime import date

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone

from .models import StudentProfile, FacultyProfile, Homework, Marks, Attendance
# from .utils import is_faculty  # keep your existing is_faculty import/def

from collections import defaultdict
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.utils import timezone

from .models import StudentProfile, FacultyProfile, Homework, Marks, Attendance
# from .utils import is_faculty


from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from collections import defaultdict
from .models import FacultyProfile, StudentProfile, Attendance, Homework, Marks


@login_required
@user_passes_test(is_faculty)
def faculty_dashboard(request):
    faculty = FacultyProfile.objects.get(user=request.user)

    # ---- Students ----
    students_qs = StudentProfile.objects.select_related("user").all()
    marks_by_student_exam = defaultdict(lambda: defaultdict(list))
   



    # ---- TODAY summary ----
    today = timezone.localdate()
    class_levels = (
        students_qs.values_list("class_level", flat=True)
        .distinct()
        .order_by("class_level")
    )

    today_attendance = {}
    for cl in class_levels:
        total = students_qs.filter(class_level=cl).count()
        present = (
            Attendance.objects.filter(
                date=today, status="Present", student__class_level=cl
            )
            .values("student_id")
            .distinct()
            .count()
        )
        absent = max(total - present, 0)
        percentage = (present / total * 100.0) if total else 0.0
        today_attendance[str(cl)] = {
            "total": total,
            "present": present,
            "absent": absent,
            "percentage": percentage,
        }

    # ---- Attendance records grouped class-wise ----
    attendance_by_class = defaultdict(list)
    attendance_qs = (
        Attendance.objects.select_related("student__user")
        .order_by("-date", "student__class_level")
        .all()
    )
    for rec in attendance_qs:
        attendance_by_class[str(rec.student.class_level)].append(rec)

    # ---- Homework ----
    homework_list = Homework.objects.filter(faculty=faculty).order_by("-due_date")

    # ---- Marks ----
    marks_list = Marks.objects.select_related("student__user").all().order_by(
        "student__class_level", "student__user__first_name", "subject"
    )

    # a) group marks by class
    marks_by_class = defaultdict(list)
    for mark in marks_list:
        marks_by_class[str(mark.student.class_level)].append(mark)


    # b) group marks by student and exam_type
    marks_by_student_exam = defaultdict(lambda: defaultdict(list))
    for m in marks_list:
        etype = m.exam_type if getattr(m, "exam_type", None) else "General"
        marks_by_student_exam[m.student_id][etype].append(m)

    # c) students grouped by class
    students_by_class = defaultdict(list)
    for s in students_qs:
        students_by_class[str(s.class_level)].append(s)

    
#21 add-----------




    context = {
        "faculty": faculty,
        "students": students_qs,
        "marks_list": marks_list,
        "marks_by_class": dict(marks_by_class),   # ✅ added
        "marks_by_student_exam": dict(marks_by_student_exam),
        "students_by_class": dict(students_by_class),
        "attendance_by_class": dict(attendance_by_class),
        "today_attendance": today_attendance,
        "homework_list": homework_list,
        "today": today,
    }
    return render(request, "faculty_dashboard.html", context)

# --------------------------
# Student Dashboard
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from collections import defaultdict
from .models import StudentProfile, Attendance, Marks

def is_faculty(user):
    return user.groups.filter(name='Faculty').exists()

@login_required
@user_passes_test(is_faculty)
def student_performance(request):
    # --- Students grouped by class ---
    students_qs = StudentProfile.objects.select_related('user').all()
    students_by_class = defaultdict(list)
    for s in students_qs:
        students_by_class[str(s.class_level)].append(s)

    selected_class = request.GET.get('class_level', '')
    student_id = request.GET.get('student_id', '')

    # Prepare the students list for the selected class
    students_in_class = students_by_class.get(selected_class, []) if selected_class else []

    # Prepare selected student if student_id is provided
    selected_student = get_object_or_404(StudentProfile, id=student_id) if student_id else None

    # Attendance summary
    attendance_summary = None
    if selected_student:
        attendance_qs = Attendance.objects.filter(student=selected_student)
        total_days = attendance_qs.count()
        present_count = attendance_qs.filter(status='Present').count()
        absent_count = attendance_qs.filter(status='Absent').count()
        percentage = (present_count / total_days * 100) if total_days else 0
        attendance_summary = {
            "total": total_days,
            "present": present_count,
            "absent": absent_count,
            "percentage": percentage,
        }

    # Marks summary
 
   
    #marke students 
    marks_summary = {}
    if selected_student:
        marks_qs = Marks.objects.filter(student=selected_student)
        marks_summary = {}
        for mark in marks_qs:
            exam_type = getattr(mark, 'exam_type', None) or "General"
            if exam_type not in marks_summary:
                marks_summary[exam_type] = []
            marks_summary[exam_type].append(mark)


    context = {
        "students_by_class": dict(students_by_class),
        "students_in_class": students_in_class,
        "selected_class": selected_class,
        "selected_student": selected_student,
        "attendance_summary": attendance_summary,
        "marks_summary": marks_summary,
    }

    return render(request, 'student_performance.html', context)


#---------------------------


@login_required
@user_passes_test(is_student)

@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    try:
        student = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.error(request, "⚠️ No Student Profile found for this account. Please contact Admin.")
        return redirect("home")

    # Attendance ordered from latest to oldest
    attendance = Attendance.objects.filter(student=student).order_by('-date')

    today = timezone.now().date()
    first_day = date(today.year, today.month, 1)
    last_day = date(today.year, today.month, monthrange(today.year, today.month)[1])

    total_days = Attendance.objects.filter(student=student, date__range=(first_day, last_day)).count()
    present_days = Attendance.objects.filter(student=student, date__range=(first_day, last_day), status="Present").count()
    percentage = (present_days / total_days * 100) if total_days > 0 else 0

    marks = Marks.objects.filter(student=student).order_by("exam_type", "subject")
    submissions = HomeworkSubmission.objects.filter(student=student)
    homework_list = Homework.objects.all().order_by('-due_date')

    marks_by_exam = {}
    for m in marks:
        marks_by_exam.setdefault(m.exam_type, []).append(m)

    return render(request, 'student_dashboard.html', {
        'student': student,
        'attendance': attendance,
        'marks': marks,
        'submissions': submissions,
        'marks_by_exam': marks_by_exam,
        'attendance_percentage': round(percentage, 2),
        'homework_list': homework_list
    })


# --------------------------
# Mark Attendance
# --------------------------
from django.contrib import messages
from django.utils import timezone

from datetime import datetime

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from .models import StudentProfile, Attendance, FacultyProfile
@login_required
@user_passes_test(is_faculty)
def mark_attendance(request):
    # Get the logged-in faculty
    faculty = FacultyProfile.objects.get(user=request.user)

    # Get distinct class levels for the dropdown
    classes = StudentProfile.objects.values_list('class_level', flat=True).distinct()
    selected_class = request.GET.get('class_level')
    students = []

    # Filter students by selected class
    if selected_class:
        students = StudentProfile.objects.filter(class_level=selected_class)
        today = timezone.now().date()

        # Pre-fill today's attendance
        for student in students:
            attendance_record = Attendance.objects.filter(student=student, date=today).first()
            student.attendance_today = attendance_record
    else:
        today = timezone.now().date()

    # Handle POST to save/update attendance
    if request.method == 'POST':
        date_str = request.POST.get('date')
        if date_str:
            try:
                attendance_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                attendance_date = timezone.now().date()
        else:
            attendance_date = timezone.now().date()

        for student in students:
            status = request.POST.get(f'status_{student.id}')
            if status in ['Present', 'Absent']:
                Attendance.objects.update_or_create(
                    student=student,
                    date=attendance_date,
                    defaults={'status': status}
                )
            else:
                messages.warning(request, f"Status not selected for {student.user.get_full_name()}")

        messages.success(request, "Attendance recorded successfully.")
        return redirect('faculty_dashboard')

    return render(request, 'mark_attendance.html', {
        'students': students,
        'classes': classes,
        'selected_class': selected_class,
        'today': today,
    })



# --------------------------
# Add Marks
# --------------------------

from django.contrib.auth.decorators import user_passes_test

def is_faculty(user):
    return hasattr(user, 'facultyprofile')

def is_admin(user):
    return user.is_superuser or user.is_staff
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import StudentProfile, Marks

@login_required
def add_marks(request):
    # Get all unique class levels for dropdown
    class_levels = StudentProfile.objects.values_list("class_level", flat=True).distinct().order_by("class_level")

    selected_class = request.GET.get("class_level")  # Get class from query string
    students = StudentProfile.objects.none()

    if selected_class:
        students = StudentProfile.objects.filter(class_level=selected_class).select_related("user").order_by("roll_number")

    if request.method == "POST":
        subject = request.POST.get("subject")
        exam_type = request.POST.get("exam_type")
        max_marks = request.POST.get("max_marks")
        selected_class = request.POST.get("class_level")  # POST also carries class

        # Validation
        if not subject or not exam_type or not max_marks or not selected_class:
            return render(request, "add_marks.html", {
                "students": students,
                "class_levels": class_levels,
                "selected_class": selected_class,
                "error": "⚠️ Please fill all required fields."
            })

        try:
            max_marks = float(max_marks)
        except ValueError:
            return render(request, "add_marks.html", {
                "students": students,
                "class_levels": class_levels,
                "selected_class": selected_class,
                "error": "⚠️ Maximum Marks must be a number."
            })

        with transaction.atomic():
            for student in students:
                marks_value = request.POST.get(f"marks_{student.id}")
                if marks_value:
                    try:
                        marks_value = float(marks_value)
                        Marks.objects.create(
                            student=student,
                            subject=subject,
                            marks=marks_value,
                            max_marks=max_marks,
                            exam_type=exam_type,
                        )
                    except ValueError:
                        continue

        # Redirect back
        if is_faculty(request.user):
            return redirect("faculty_dashboard")
        return redirect("admin_dashboard")

    return render(request, "add_marks.html", {
        "students": students,
        "class_levels": class_levels,
        "selected_class": selected_class,
    })



from django.shortcuts import get_object_or_404
from django.contrib import messages
from .models import Homework

@login_required
def delete_homework(request, homework_id):
    homework = get_object_or_404(Homework, id=homework_id)

    # Optional: restrict so only faculty/admin can delete
    if not (is_faculty(request.user) or is_admin(request.user)):
        messages.error(request, "You are not authorized to delete homework.")
        return redirect("faculty_dashboard")

    homework.delete()
    messages.success(request, "Homework deleted successfully.")
    return redirect("faculty_dashboard")

from django.shortcuts import render, get_object_or_404
from .models import FacultyProfile

def faculty_detail(request, faculty_id):
    faculty = get_object_or_404(FacultyProfile, id=faculty_id)
    return render(request, 'faculty_detail.html', {'faculty': faculty})

# --------------------------
# Assign Homework
# --------------------------
@login_required
@user_passes_test(is_faculty)
def upload_homework(request):
    faculty = FacultyProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = HomeworkForm(request.POST, request.FILES)  # include files
        if form.is_valid():
            homework = form.save(commit=False)
            homework.faculty = faculty
            homework.save()
            return redirect('faculty_dashboard')
        else:
            print(form.errors)  # debug errors
    else:
        form = HomeworkForm()

    return render(request, 'assign_homework.html', {'form': form})


# --------------------------
# View Homework (Student)
# --------------------------
@login_required
@user_passes_test(is_student)
@user_passes_test(is_admin)
def view_homework(request):
    student = StudentProfile.objects.get(user=request.user)
    homework_list = Homework.objects.filter(department=student.department)
    return render(request, 'view_homework.html', {'homework_list': homework_list})

# --------------------------
# Submit Homework


# --------------------------
@login_required
@user_passes_test(is_student)
@user_passes_test(is_admin)
def submit_homework(request, homework_id):
    student = StudentProfile.objects.get(user=request.user)
    homework = get_object_or_404(Homework, id=homework_id)

    if request.method == 'POST':
        form = HomeworkSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.student = student
            submission.homework = homework
            submission.save()
            return redirect('student_dashboard')
    else:
        form = HomeworkSubmissionForm()

    return render(request, 'submit_homework.html', {
        'form': form,
        'homework': homework
    })

# --------------------------
# View Attendance (Student)
# --------------------------
@login_required
@user_passes_test(is_student)
@user_passes_test(is_admin)
@user_passes_test(is_faculty)
def view_attendance(request):
    student = StudentProfile.objects.get(user=request.user)
    attendance_records = Attendance.objects.filter(student=student)
    return render(request, 'view_attendance.html', {'attendance': attendance_records})

# --------------------------
# View Marks (Student)
# --------------------------
@login_required
@user_passes_test(is_student)
@user_passes_test(is_admin)
def view_marks(request):
    student = StudentProfile.objects.get(user=request.user)
    
    marks = Marks.objects.filter(student=student)
    return render(request, 'view_marks.html', {'marks': marks})

# --------------------------
# Admin Add Student
# --------------------------

from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import StudentProfile
from django.shortcuts import render, redirect
from .models import Student
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import StudentProfile
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import StudentProfile
@login_required
@user_passes_test(is_admin)
def add_student(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        roll_number = request.POST.get('roll_number')
        class_level = request.POST.get('class_level')
        department = request.POST.get('department')

        # Create the User object
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
            
        )

        # Create the StudentProfile
        StudentProfile.objects.create(
            user=user,
            roll_number=roll_number,
            class_level=class_level,
            department=department
        )

        messages.success(request, 'Student created successfully.')
        return redirect('admin_dashboard')  # Change to your dashboard name

    return render(request, 'add_student.html')




# --------------------------
# Admin Add Faculty
# --------------------------
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from .forms import FacultyCreationForm
from .models import FacultyProfile

def is_admin(user):
    return user.is_superuser or user.groups.filter(name="Admin").exists()

@login_required
@user_passes_test(is_admin)
def add_faculty(request):
    if request.method == "POST":
        form = FacultyCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Group.objects.get(name="Faculty").user_set.add(user)
            return redirect("faculty_list")
    else:
        form = FacultyCreationForm()
    return render(request, "add_faculty.html", {"form": form})

@login_required
@user_passes_test(is_admin)
def faculty_list(request):
    faculties = FacultyProfile.objects.all()
    return render(request, "faculty_list.html", {"faculties": faculties})



# --------------------------
# Admin Login
# --------------------------
def admin_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.groups.filter(name='Admin').exists():
                login(request, user)
                return redirect('admin_dashboard')
            else:
                messages.error(request, "You are not authorized as Admin.")
        else:
            messages.error(request, "Invalid credentials.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form, 'role': 'Admin'})


# --------------------------
# Faculty Login
# --------------------------
def faculty_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.groups.filter(name='Faculty').exists():
                login(request, user)
                return redirect('faculty_dashboard')
            else:
                messages.error(request, "You are not authorized as Faculty.")
        else:
            messages.error(request, "Invalid credentials.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form, 'role': 'Faculty'})


# --------------------------
# Student Login
# --------------------------
def student_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.groups.filter(name='Student').exists():
                login(request, user)
                return redirect('student_dashboard')
            else:
                messages.error(request, "You are not authorized as Student.")
        else:
            messages.error(request, "Invalid credentials.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form, 'role': 'Student'})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import StudentProfile, FacultyProfile
from .forms import StudentCreationForm, FacultyCreationForm, StudentEditForm, FacultyEditForm

# ===========================
# STUDENT EDIT & DELETE
# ===========================

from django.shortcuts import render, redirect, get_object_or_404
from .models import Student

from .models import StudentProfile

def edit_student(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)
    if request.method == 'POST':
        student.user.username = request.POST['username']
        student.roll_number = request.POST['roll_number']
        student.class_level = request.POST['class_level']
        student.department = request.POST['department']
        student.user.save()
        student.save()
        return redirect('student_list')
    return render(request, 'edit_student.html', {'student': student})

from django.shortcuts import render, get_object_or_404, redirect
from .models import Marks
from django.shortcuts import render, get_object_or_404, redirect

from django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .models import Marks

@login_required
def edit_marks(request, mark_id):
    # Get the marks entry by ID
    marks = get_object_or_404(Marks, id=mark_id)
    student = marks.student  # Related student

    if request.method == "POST":
        marks.subject = request.POST.get("subject")

        # Convert safely to float
        if request.POST.get("marks"):
            marks.marks = float(request.POST.get("marks"))
        if request.POST.get("max_marks"):
            marks.max_marks = float(request.POST.get("max_marks"))

        # Calculate percentage
        percentage = (marks.marks / marks.max_marks * 100) if marks.max_marks > 0 else 0

        # Assign grade based on percentage
        if percentage >= 90:
            grade = "A"
        elif percentage >= 75:
            grade = "B"
        elif percentage >= 60:
            grade = "C"
        elif percentage >= 40:
            grade = "D"
        else:
            grade = "F"

        marks.grade = grade
        marks.save()

        # Redirect based on user group
        user_groups = request.user.groups.values_list('name', flat=True)
        if 'Admin' in user_groups:
            return redirect('admin_dashboard')
        elif 'Faculty' in user_groups:
            return redirect('faculty_dashboard')
        else:
            # Default fallback
            return redirect('home')

    # Pre-calculate percentage for display
    percentage = (marks.marks / marks.max_marks * 100) if marks.max_marks > 0 else 0

    return render(request, 'edit_marks.html', {
        'student': student,
        'marks': marks,
        'percentage': percentage
    })




def delete_student(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student deleted successfully.')
        return redirect('admin_dashboard')
    return render(request, 'confirm_delete.html', {'object': student, 'type': 'Student'})


# ===========================
# FACULTY EDIT & DELETE
# ===========================

def edit_faculty(request, faculty_id):
    faculty = get_object_or_404(FacultyProfile, id=faculty_id)
    if request.method == 'POST':
        form = FacultyEditForm(request.POST, instance=faculty)
        if form.is_valid():
            form.save()
            messages.success(request, 'Faculty updated successfully.')
            return redirect('admin_dashboard')
    else:
        form = FacultyEditForm(instance=faculty)
    return render(request, 'edit_faculty.html', {'form': form, 'faculty': faculty})


def delete_faculty(request, faculty_id):
    faculty = get_object_or_404(FacultyProfile, id=faculty_id)
    if request.method == 'POST':
        faculty.delete()
        messages.success(request, 'Faculty deleted successfully.')
        return redirect('admin_dashboard')
    return render(request, 'confirm_delete.html', {'object': faculty, 'type': 'Faculty'})
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import date
from calendar import monthrange
from .models import StudentProfile, FacultyProfile, Attendance, Marks

def is_admin(user):
    return user.is_superuser or user.groups.filter(name='Admin').exists()


@login_required
@user_passes_test(is_admin)
def faculty_list(request):
    faculties = FacultyProfile.objects.all()
    return render(request, 'faculty_list.html', {'faculties': faculties})

@login_required
@user_passes_test(is_admin)
def student_list(request):
    today = date.today()
    month_start = date(today.year, today.month, 1)
    month_end = date(today.year, today.month, monthrange(today.year, today.month)[1])

    students = StudentProfile.objects.all()
    student_attendance = []

    for student in students:
        total_days = Attendance.objects.filter(student=student, date__range=(month_start, month_end)).count()
        present_days = Attendance.objects.filter(student=student, date__range=(month_start, month_end), status='Present').count()
        
        percentage = round((present_days / total_days) * 100, 2) if total_days > 0 else 0
        student_attendance.append((student, percentage))

    return render(request, 'student_list.html', {'student_attendance': student_attendance})


from django.shortcuts import render, redirect, get_object_or_404
from .models import StudentProfile, Attendance
from django.utils import timezone
from datetime import date
from calendar import monthrange
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from datetime import date
from calendar import monthrange
from .models import StudentProfile, Attendance

from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from datetime import date
from calendar import monthrange
from .models import StudentProfile, Attendance
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from datetime import date
from calendar import monthrange
from .models import StudentProfile, Attendance

def manage_attendance(request, id):
    # Get all students
    students = StudentProfile.objects.all()

    if request.method == "POST":
        student_id = request.POST.get("student_id")
        date_str = request.POST.get("date")
        status = request.POST.get("status")

        if student_id and date_str and status:
            student = get_object_or_404(StudentProfile, id=student_id)
            attendance_date = date.fromisoformat(date_str)

            # Create or update attendance record
            Attendance.objects.update_or_create(
                student=student,
                date=attendance_date,
                defaults={'status': status}
            )

        return redirect('manage_attendance', id=id)

    # Calculate monthly attendance percentage
    today = timezone.now().date()
    first_day = date(today.year, today.month, 1)
    last_day = date(today.year, today.month, monthrange(today.year, today.month)[1])

    attendance_data = []
    for student in students:
        total_days = Attendance.objects.filter(
            student=student, date__range=(first_day, last_day)
        ).count()

        present_days = Attendance.objects.filter(
            student=student, date__range=(first_day, last_day), status="Present"
        ).count()

        percentage = (present_days / total_days * 100) if total_days > 0 else 0

        attendance_data.append({
            'student': student,
            'total_days': total_days,
            'present_days': present_days,
            'percentage': percentage,
            'low_attendance': percentage < 75
        })

    return render(request, "manage_attendance.html", {
        "attendance_data": attendance_data
    })


from django.shortcuts import render, get_object_or_404, redirect
from .models import StudentProfile, Marks




def delete_marks(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)
    Marks.objects.filter(student=student).delete()
    return redirect('faculty_dashboard')


from django.shortcuts import get_object_or_404, redirect
from .models import Marks  # adjust import if needed

@login_required
def delete_mark(request, mark_id):
    mark = get_object_or_404(Marks, id=mark_id)
    mark.delete()

    # Redirect based on role
    if request.user.groups.filter(name="Faculty").exists():
        return redirect('faculty_dashboard')
    elif request.user.groups.filter(name="Admin").exists():
        return redirect('admin_dashboard')
    else:
        return redirect('home')  # fallback
# redirect back to faculty dashboard



