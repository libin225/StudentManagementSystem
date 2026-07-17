from django import forms
from .models import Student 
from .models import Attendance

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'roll_no', 'email', 'course', 'photo']
        


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'date', 'status']

        widgets = {
            'date' : forms.DateInput(attrs={'type': 'date'}),
        }
