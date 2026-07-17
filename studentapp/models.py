from django.db import models
from django.utils import timezone

class Course(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_no = models.CharField(max_length=20)
    email = models.EmailField()

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    photo = models.ImageField(
        upload_to='student_photos/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name
    

class Attendance(models.Model):
        STATUS_CHOICES = [
            ('Present', 'Present'),
            ('Absent', 'Absent'),
        ]

        student = models.ForeignKey(
            Student,
            on_delete=models.CASCADE
        )

        date = models.DateField(default=timezone.now)
        
        status = models.CharField(
            max_length=10,
            choices=STATUS_CHOICES,
        )

        def __str__(self):
            return f"{self.student.name} - {self.date} - {self.status}"
