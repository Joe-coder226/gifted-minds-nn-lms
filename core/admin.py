from django.contrib import admin
from .models import Exam, Question, StudentExam, LiveSession, Level, Grade

admin.site.register(Exam)
admin.site.register(Question)
admin.site.register(StudentExam)
admin.site.register(LiveSession)
admin.site.register(Level)
admin.site.register(Grade)