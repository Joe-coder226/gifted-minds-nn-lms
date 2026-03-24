from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Avg, Max, Min, Count
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

import json
from datetime import timedelta

from .models import (
    Course, CourseMaterial, AttendanceSession, Attendance,
    Exam, StudentExam, Question, LiveSession,
    Payment, Video, Subscription, Level, Grade
)

# ======================================
# HOME
# ======================================
def home(request):
    return render(request, "core/home.html")


# ======================================
# AUTH
# ======================================
def student_signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username exists!")
            return render(request, "core/student_signup.html")

        User.objects.create_user(username=username, password=password)
        messages.success(request, "Account created!")
        return redirect("login")

    return render(request, "core/student_signup.html")


def admin_signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = User.objects.create_user(username=username, password=password)
        user.is_staff = True
        user.save()

        messages.success(request, "Admin created!")
        return redirect("login")

    return render(request, "core/admin_signup.html")


@login_required
def redirect_dashboard(request):
    return redirect("admin_dashboard") if request.user.is_staff else redirect("student_dashboard")


# ======================================
# DASHBOARDS
# ======================================
@login_required
def student_dashboard(request):
    courses = Course.objects.all()
    return render(request, "core/student_dashboard.html", {"courses": courses})


@login_required
def admin_dashboard(request):

    if not request.user.is_staff:
        return redirect("student_dashboard")

    courses = Course.objects.all()
    exams = Exam.objects.all()
    live_sessions = LiveSession.objects.all()

    levels = Level.objects.all()
    grades = Grade.objects.all()

    # student count per course
    courses_with_counts = []
    for course in courses:
        student_count = Subscription.objects.filter(
            grade=course.grade,
            is_active=True
        ).count()

        course.student_count = student_count
        courses_with_counts.append(course)

    total_students = User.objects.filter(is_staff=False).count()
    total_courses = courses.count()
    total_subscriptions = Subscription.objects.count()
    total_exams = exams.count()
    active_live_sessions = live_sessions.filter(is_active=True).count()

    exam_stats = exams.annotate(
        average_score=Avg("studentexam__score"),
        highest_score=Max("studentexam__score"),
        lowest_score=Min("studentexam__score"),
        total_attempts=Count("studentexam")
    )

    return render(request, "core/admin_dashboard.html", {
        "courses_with_counts": courses_with_counts,
        "exams": exams,
        "live_sessions": live_sessions,
        "levels": levels,
        "grades": grades,
        "total_students": total_students,
        "total_courses": total_courses,
        "total_subscriptions": total_subscriptions,
        "total_exams": total_exams,
        "active_live_sessions": active_live_sessions,
        "exam_stats": exam_stats
    })


# ======================================
# COURSE DETAIL (BOTH ADMIN & STUDENT)
# ======================================
@login_required
def course_detail(request, course_id):

    course = get_object_or_404(Course, id=course_id)

    videos = Video.objects.filter(course=course)
    materials = CourseMaterial.objects.filter(course=course)
    exams = Exam.objects.filter(course=course)
    live_sessions = LiveSession.objects.filter(course=course, is_active=True)
    attendance_session = AttendanceSession.objects.filter(course=course, is_active=True).first()

    return render(request, "core/course_detail.html", {
        "course": course,
        "videos": videos,
        "materials": materials,
        "exams": exams,
        "live_sessions": live_sessions,
        "attendance_session": attendance_session
    })


# ======================================
# CREATE COURSE
# ======================================
@login_required
def create_course(request):

    if not request.user.is_staff:
        return redirect("student_dashboard")

    levels = Level.objects.all()
    grades = Grade.objects.all()

    if request.method == "POST":
        Course.objects.create(
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            level_id=request.POST.get("level"),
            grade_id=request.POST.get("grade"),
            created_by=request.user
        )
        messages.success(request, "Course created!")
        return redirect("admin_dashboard")

    return render(request, "core/create_course.html", {"levels": levels, "grades": grades})

#=======================================
# DELETE COURSE
#=======================================
@login_required
def delete_course(request, course_id):

    if not request.user.is_staff:
        return redirect("student_dashboard")

    course = get_object_or_404(Course, id=course_id)

    course.delete()

    messages.success(request, "Course deleted successfully!")

    return redirect("admin_dashboard")
#=======================================
# STUDENT COURSE
#=======================================
@login_required
def student_course(request, course_id):

    course = get_object_or_404(Course, id=course_id)

    videos = Video.objects.filter(course=course)
    materials = CourseMaterial.objects.filter(course=course)
    exams = Exam.objects.filter(course=course)
    live_sessions = LiveSession.objects.filter(course=course, is_active=True)

    return render(request, "core/student_course.html", {
        "course": course,
        "videos": videos,
        "materials": materials,
        "exams": exams,
        "live_sessions": live_sessions
    })

# ======================================
# MATERIAL & VIDEO
# ======================================
@login_required
def upload_material(request, course_id):

    if not request.user.is_staff:
        return redirect("student_dashboard")

    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":
        CourseMaterial.objects.create(
            course=course,
            title=request.POST.get("title"),
            file=request.FILES.get("file")
        )
        return redirect("course_detail", course_id=course.id)

    return render(request, "core/upload_material.html", {"course": course})


@login_required
def upload_video(request, course_id):

    if not request.user.is_staff:
        return redirect("student_dashboard")

    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":
        Video.objects.create(
            course=course,
            title=request.POST.get("title"),
            video=request.FILES.get("video")
        )
        return redirect("course_detail", course_id=course.id)

    return render(request, "core/upload_video.html", {"course": course})


# ======================================
# LIVE CLASS
# ======================================
@login_required
def create_live_session(request, course_id):

    if not request.user.is_staff:
        return redirect("student_dashboard")

    course = get_object_or_404(Course, id=course_id)

    LiveSession.objects.filter(course=course, is_active=True).update(is_active=False)

    session = LiveSession.objects.create(
        course=course,
        title=f"{course.title} Live",
        room_name=f"room_{course.id}",
        created_by=request.user,
        is_active=True
    )

    return redirect("join_live_class", session_id=session.id)


@login_required
def join_live_class(request, session_id):
    session = get_object_or_404(LiveSession, id=session_id)
    return render(request, "core/live_class.html", {"session": session})
#=======================================
# LIVE SESSION ROOM
#=======================================
@login_required
def live_session_room(request, session_id):

    session = get_object_or_404(LiveSession, id=session_id)

    if not request.user.is_staff:

        if not Subscription.objects.filter(
            student=request.user,
            is_active=True
        ).exists():

            return redirect("subscribe")

    return render(request, "core/live_room.html", {
        "session": session
    })
#=======================================
# END LIVE SESSION
#=======================================
@login_required
def end_live_session(request, session_id):

    if not request.user.is_staff:
        return redirect("student_dashboard")

    session = get_object_or_404(LiveSession, id=session_id)

    session.is_active = False
    session.save()

    messages.success(request, "Live session ended.")

    return redirect("admin_dashboard")

# ======================================
# ATTENDANCE
# ======================================
@login_required
def create_attendance_session(request, course_id):

    if not request.user.is_staff:
        return redirect("student_dashboard")

    course = get_object_or_404(Course, id=course_id)

    AttendanceSession.objects.filter(course=course, is_active=True).update(is_active=False)

    AttendanceSession.objects.create(course=course, is_active=True)

    return redirect("course_detail", course_id=course.id)


@login_required
def mark_attendance(request, session_id):

    session = get_object_or_404(AttendanceSession, id=session_id)

    Attendance.objects.get_or_create(
        session=session,
        student=request.user
    )

    return redirect("course_detail", course_id=session.course.id)
#=======================================
# STUDENT ATTENDANCE
#=======================================
@login_required
def student_attendance(request):

    if request.user.is_staff:
        return redirect("admin_dashboard")

    attendance_records = Attendance.objects.filter(
        student=request.user
    ).select_related("session__course")

    return render(request, "core/student_attendance.html", {
        "attendance_records": attendance_records
    })


# ======================================
# EXAMS
# ======================================
@login_required
def take_exam(request, exam_id):

    exam = get_object_or_404(Exam, id=exam_id)
    questions = Question.objects.filter(exam=exam)

    if request.method == "POST":
        score = 0

        for q in questions:
            if request.POST.get(str(q.id)) == q.correct_answer:
                score += 1

        StudentExam.objects.create(
            student=request.user,
            exam=exam,
            score=score,
            completed=True
        )

        return render(request, "core/exam_result.html", {
            "score": score,
            "total": questions.count()
        })

    return render(request, "core/take_exam.html", {
        "exam": exam,
        "questions": questions
    })
#=======================================
# ADD QUESTIONS
#=======================================
@login_required
def add_question(request, exam_id):

    if not request.user.is_staff:
        return redirect("student_dashboard")

    exam = get_object_or_404(Exam, id=exam_id)

    if request.method == "POST":

        Question.objects.create(
            exam=exam,
            question_text=request.POST.get("question_text"),
            option_a=request.POST.get("option_a"),
            option_b=request.POST.get("option_b"),
            option_c=request.POST.get("option_c"),
            option_d=request.POST.get("option_d"),
            correct_answer=request.POST.get("correct_answer"),
        )

        messages.success(request, "Question added successfully.")
        return redirect("admin_dashboard")

    return render(request, "core/add_question.html", {
        "exam": exam
    })


# ======================================
# FILE VIEW
# ======================================
@login_required
def view_material(request, material_id):

    material = get_object_or_404(CourseMaterial, id=material_id)

    response = FileResponse(material.file.open("rb"))
    response["Content-Disposition"] = "inline"

    return response


# ======================================
# SUBSCRIPTION
# ======================================
@login_required
def subscribe(request):

    levels = Level.objects.all()
    grades = Grade.objects.all()

    if request.method == "POST":
        subscription = Subscription.objects.create(
            student=request.user,
            level_id=request.POST.get("level"),
            grade_id=request.POST.get("student_class"),
            amount=Level.objects.get(id=request.POST.get("level")).price
        )
        return redirect("student_dashboard")

    return render(request, "core/subscription.html", {
        "levels": levels,
        "grades": grades
    })
