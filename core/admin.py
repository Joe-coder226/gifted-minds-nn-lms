from django.contrib import admin
from .models import Exam, Question, StudentExam, LiveSession, Level, Grade, CourseMaterial
from .models import *

admin.site.register(Level)
admin.site.register(Grade)
admin.site.register(Course)
admin.site.register(CourseMaterial)
admin.site.register(AttendanceSession)
admin.site.register(Attendance)
admin.site.register(Subscription)
admin.site.register(Exam)
admin.site.register(Question)
admin.site.register(StudentExam)
admin.site.register(LiveSession)
admin.site.register(Payment)
admin.site.register(Video)
