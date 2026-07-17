import json
import base64
import qrcode

from io import BytesIO

from django.utils import timezone

from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.shortcuts import render, redirect, get_object_or_404

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from openpyxl import Workbook

from .models import Student, Course, Attendance
from .forms import StudentForm, AttendanceForm



@login_required(login_url='login')
def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES) 

        if form.is_valid():
            form.save()
            messages.success(request, "Student added successfully!")
            return redirect('home')

    form = StudentForm()
    return render(request, 'add_student.html', {'form': form})

@login_required(login_url='login')
def edit_student(request, id):
    student = get_object_or_404(Student, id=id)

    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)

        if form.is_valid():
            form.save()
            messages.success(request, "Student updated successfully!")
            return redirect('home')
    else:
        form = StudentForm(instance=student)

    return render(request, 'edit_student.html', {'form': form})   

@login_required(login_url='login')
def delete_student(request, id):
    student = get_object_or_404(Student, id=id)
    student.delete()
    messages.success(request, "Student deleted successfully!")
    return redirect('home')

@login_required(login_url='login')
def home(request):
    


    query =request.GET.get('q')
    course_id = request.GET.get('course')

    if query:
        students = Student.objects.filter(
            Q(name__icontains=query) |
            Q(roll_no__icontains=query) |
            Q(email__icontains=query) |
            Q(course__name__icontains=query)
        )
    else:
        students = Student.objects.all.order_by("-id")

    if course_id:
        students = students.filter(course_id=course_id)    

    #Pagination
    paginator = Paginator(students, 5)
    page_number = request.GET.get('page')
    students = paginator.get_page(page_number)    

    total_students = Student.objects.count()   
    total_courses = Course.objects.count()
    search_results = students.paginator.count

    course_counts = Course.objects.annotate(student_count=Count('student'))

    course_labels = []
    course_students = []

    for course in course_counts:
        course_labels.append(course.name)
        course_students.append(course.student_count)


    course_labels = json.dumps(course_labels)  
    course_students = json.dumps(course_students)  

    

    return render(request, 'home.html', {
        'students': students,
        'query' : query,
        'selected_course': course_id,
        'total_students': total_students,
        'total_courses': total_courses,
        'search_results': search_results,
        'course_counts': course_counts,
        'course_labels': course_labels,
        'course_students': course_students,
    })

def login_view(request):
    #if request.user.is_authenticated:
        #return redirect('home')

    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')

def student_detail(request, id):
    student = get_object_or_404(Student, id=id)

    return render(request, 'student_detail.html', {
        'student': student
    })

@login_required(login_url='login')
def export_pdf(request):



    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="students.pdf"'

    doc = SimpleDocTemplate(response)

    data = [['Roll No', 'Name', 'Email', 'Course']]

    
    students = Student.objects.all()

    for student in students:
        data.append([
            student.roll_no,
            student.name,
            student.email,
            student.course.name
        ])

    table = Table(data)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))

    doc.build([table])

    return response

@login_required(login_url='login')
def export_excel(request):

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response['Content-Disposition'] = 'attachment; filename="students.xlsx"'

    wb = Workbook()
    ws = wb.active
    ws.title = "Students"

    ws.append(["Roll No", "Name", "Email", "Course"])

    students = Student.objects.all()

    for student in students:
        ws.append([
            student.roll_no,
            student.name,
            student.email,
            student.course.name
        ])

    wb.save(response)

    return response

@login_required(login_url='login')
def student_id_card(request, id):
    student = get_object_or_404(Student, id=id)

    qr = qrcode.make(
        request.build_absolute_uri(f"/student/{student.id}/")
    )

    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    qr_code = base64.b64encode(buffer.getvalue()).decode()

    return render(request, "student_id_card.html", {
        "student": student,
        "qr_code": qr_code
    })

@login_required(login_url='login')
def attendance_list(request):

    form = AttendanceForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Attendance added successfully!")
            return redirect("attendance_list")

    selected_date = request.GET.get("date")

    attendances = Attendance.objects.all().order_by("-date")

    if selected_date:
        attendances = attendances.filter(date=selected_date)

    today = timezone.now().date()

    present_today = Attendance.objects.filter(
        date=today,
        status="Present"
    ).count()

    absent_today = Attendance.objects.filter(
        date=today,
        status="Absent"
    ).count()

    student_reports = []
    students = Student.objects.all()

    for student in students:
        present = Attendance.objects.filter(
            student=student,
            status="Present"
        ).count()

        absent = Attendance.objects.filter(
            student=student,
            status="Absent"
        ).count()

        total = present + absent

        percentage = 0
        if total > 0:
            percentage = round((present / total) * 100,2)

        student_reports.append({
            "student": student,
            "present": present,
            "absent": absent,
            "percentage": percentage,
        })    

       

    total_today = Attendance.objects.filter(
        date=today
    ).count()

    
            

  

    return render(request, 'attendance.html', {
        "form": form,
        "attendances": attendances,
        "present_today": present_today,
        "absent_today": absent_today,
        "total_today": total_today,
        "selected_date": selected_date,
        "student_reports": student_reports,

    })


@login_required(login_url='login')
def edit_attendance(request, id):
    attendance = get_object_or_404(Attendance, id=id)

    form = AttendanceForm(request.POST or None, instance=attendance)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Attendance updated successfully!")
            return redirect("attendance_list")
            
    return render(request, "edit_attendance.html", {
        "form": form
    })    
    
@login_required(login_url='login')
def delete_attendance(request, id):
    attendance = get_object_or_404(Attendance, id=id)
    attendance.delete()

    messages.success(request, "Attendance deleted successfully!")

    return redirect("attendance_list")


