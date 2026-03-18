from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Avg, Max, Min, Count
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

import json
import uuid
from datetime import timedelta

from .models import (
    Course, CourseMaterial, AttendanceSession, Attendance,
    Exam, StudentExam, Question, LiveSession,
    Payment, Video, Subscription, Level, Grade
)

from .mpesa import initiate_stk_push

def initiate_stk_push(phone, amount):

    print("Initiating STK Push")
    print("Phone:", phone)
    print("Amount:", amount)

    return {"status": "success"}

# ======================================
# SUBSCRIPTION CHECK
# ======================================

def has_active_subscription(user):
    return Subscription.objects.filter(
        student=user,
        is_active=True
    ).exists()


def subscription_required(view_func):

    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

        if request.user.is_staff:
            return view_func(request, *args, **kwargs)

        subscription = Subscription.objects.filter(
            student=request.user,
            is_active=True
        ).first()

        if not subscription:
            return redirect("subscribe")

        return view_func(request, *args, **kwargs)

    return wrapper



# ======================================
# HOME
# ======================================

def home(request):
    return render(request, "core/home.html")


# ======================================
# STUDENT SIGNUP
# ======================================

def student_signup(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return render(request, "core/student_signup.html")

        User.objects.create_user(
            username=username,
            password=password
        )

        messages.success(request, "Student account created successfully!")
        return redirect("login")

    return render(request, "core/student_signup.html")


# ======================================
# ADMIN SIGNUP
# ======================================

def admin_signup(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return render(request, "core/admin_signup.html")

        user = User.objects.create_user(
            username=username,
            password=password
        )

        user.is_staff = True
        user.save()

        messages.success(request, "Admin account created successfully!")
        return redirect("login")

    return render(request, "core/admin_signup.html")


# ======================================
# DASHBOARD REDIRECT
# ======================================

@login_required
def redirect_dashboard(request):

    if request.user.is_staff:
        return redirect("admin_dashboard")

    return redirect("student_dashboard")


# ======================================
# STUDENT DASHBOARD
# ======================================
@login_required
def student_dashboard(request):

    courses = Course.objects.all()

    return render(request, "core/student_dashboard.html", {
        "courses": courses
    })






# ======================================
# ADMIN DASHBOARD
# ======================================

@login_required
def admin_dashboard(request):

    if not request.user.is_staff:
        return redirect("student_dashboard")

    courses = Course.objects.all()
    exams = Exam.objects.all()
    live_sessions = LiveSession.objects.all()

    courses_with_counts = []
    for course in courses:
        student_count = Subscription.objects.filter(
            grade=course.grade,
            is_active=True
        ).count()

        course.student_count = student_count
        courses_with_counts.append(course)
    # ADD THESE TWO LINES
    levels = Level.objects.all()
    grades = Grade.objects.all()

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

    if request.method == "POST" and "create_exam" in request.POST:

        course_id = request.POST.get("course_id")
        title = request.POST.get("exam_title")
        duration = request.POST.get("duration")

        course = Course.objects.get(id=course_id)

        Exam.objects.create(
            course=course,
            title=title,
            duration=duration
    )

        messages.success(request, "Exam created successfully.")
        return redirect("admin_dashboard")

    return render(request, "core/admin_dashboard.html", {
        "courses_with_counts": courses_with_counts,
        "exams": exams,
        "live_sessions": live_sessions,
        "levels": levels,   # now defined
        "grades": grades,   # now defined
        "total_students": total_students,
        "total_courses": total_courses,
        "total_subscriptions": total_subscriptions,
        "total_exams": total_exams,
        "active_live_sessions": active_live_sessions,
        "exam_stats": exam_stats
    })

#=======================================
# CREATE COURSE
#=======================================
@login_required
def create_course(request):

    if not request.user.is_staff:
        return redirect("student_dashboard")

    levels = Level.objects.all()
    grades = Grade.objects.all()

    if request.method == "POST":
        print("FORM DATA:", request.POST)

        title = request.POST.get("title")
        description = request.POST.get("description")
        level_id = request.POST.get("level")
        grade_id = request.POST.get("grade")

        if not title or not description or not level_id or not grade_id:
            messages.error(request, "All fields are required.")
            return redirect("create_course")

        level = get_object_or_404(Level, id=level_id)
        grade = get_object_or_404(Grade, id=grade_id)

        Course.objects.create(
            title=title,
            description=description,
            level=level,
            grade=grade,
            created_by=request.user
        )

        messages.success(request, "Course created successfully!")

        return redirect("admin_dashboard")

    return render(request, "core/create_course.html", {
        "levels": levels,
        "grades": grades
    })


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


# ======================================
# COURSE DETAIL
# ======================================
# ======================================
# COURSE DETAIL (ADMIN / INSTRUCTOR)
# ======================================

@login_required
def course_detail(request, course_id):

    if not request.user.is_staff:
        return redirect("student_dashboard")

    course = get_object_or_404(Course, id=course_id)

    videos = Video.objects.filter(course=course)
    materials = CourseMaterial.objects.filter(course=course)
    exams = Exam.objects.filter(course=course)

    # Upload Video
    if request.method == "POST" and "upload_video" in request.POST:

        title = request.POST.get("title")
        video_file = request.FILES.get("video")

        Video.objects.create(
            course=course,
            title=title,
            video=video_file
        )

        return redirect("course_detail", course_id=course.id)
    
    # CREATE LIVE CLASS
    if request.method == "POST" and "create_live" in request.POST:

        title = request.POST.get("live_title")
        link = request.POST.get("meeting_link")

        LiveSession.objects.create(
            course=course,
            title=title,
            meeting_link=link,
            is_active=True
    )

        return redirect("course_detail", course_id=course.id)

    # Upload Material
    if request.method == "POST" and "upload_material" in request.POST:

        title = request.POST.get("title")
        file = request.FILES.get("file")

        CourseMaterial.objects.create(
            course=course,
            title=title,
            file=file
        )

        return redirect("course_detail", course_id=course.id)

    return render(request, "core/course_detail.html", {
        "course": course,
        "videos": videos,
        "materials": materials,
        "exams": exams
    })
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



#=======================================
# UPLOAD MATERIAL
#=======================================
@login_required
def upload_material(request, course_id):

    if not request.user.is_staff:
        return redirect("student_dashboard")

    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":

        title = request.POST.get("title")
        file = request.FILES.get("file")

        CourseMaterial.objects.create(
            course=course,
            title=title,
            file=file
        )

        return redirect("course_detail", course_id=course.id)

    return render(request, "core/upload_material.html", {
        "course": course
    })
#=======================================
# CREATE ATTENDANCE
#=======================================
@login_required
def create_attendance_session(request, course_id):

    if not request.user.is_staff:
        return redirect("student_dashboard")

    courses = Course.objects.all()

    if request.method == "POST":

        course_id = request.POST.get("course")
        date = request.POST.get("date")

        course = Course.objects.get(id=course_id)

        AttendanceSession.objects.create(
            course=course,
            date=date
        )

        messages.success(request, "Attendance session created.")
        return redirect("admin_dashboard")

    return render(request, "core/create_attendance.html", {
        "courses": courses
    })
#=======================================
# MARK ATTENDANCE
#=======================================
@login_required
def mark_attendance(request, session_id):

    if not request.user.is_staff:
        return redirect("student_dashboard")

    session = get_object_or_404(AttendanceSession, id=session_id)

    students = User.objects.filter(is_staff=False)

    if request.method == "POST":

        for student in students:

            present = request.POST.get(f"student_{student.id}")

            Attendance.objects.update_or_create(
                session=session,
                student=student,
                defaults={
                    "present": True if present == "on" else False
                }
            )

        messages.success(request, "Attendance recorded successfully.")
        return redirect("student_dashboard")

    return render(request, "core/mark_attendance.html", {
        "session": session,
        "students": students
    })
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
# VIEW MATERIAL
# ======================================
@login_required
def view_material(request, material_id):

    material = get_object_or_404(CourseMaterial, id=material_id)

    response = FileResponse(
        material.file.open("rb"),
        content_type="application/pdf"
    )

    response["Content-Disposition"] = "inline"

    return response

#=======================================
# UPLOAD VIDEO
#=======================================
@login_required
def upload_video(request, course_id):

    if not request.user.is_staff:
        return redirect("student_dashboard")

    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":

        title = request.POST.get("title")
        video = request.FILES.get("video")

        Video.objects.create(
            course=course,
            title=title,
            video=video,
        )

        return redirect("course_detail", course_id=course.id)

    return render(request, "core/upload_video.html", {
        "course": course
    })


# ======================================
# WATCH VIDEO
# ======================================
@login_required
@subscription_required
def watch_video(request, video_id):

    video = get_object_or_404(Video, id=video_id)

    return render(request, "core/watch_video.html", {
        "video": video
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
# TAKE EXAM
# ======================================

@login_required
@subscription_required
def take_exam(request, exam_id):

    exam = get_object_or_404(Exam, id=exam_id)
    questions = Question.objects.filter(exam=exam)

    if request.method == "POST":

        score = 0

        for question in questions:

            selected = request.POST.get(str(question.id))

            if selected == question.correct_answer:
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
# CREATE LIVE CLASS
#=======================================
from django.shortcuts import get_object_or_404, redirect, render

@login_required
def create_live_session(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Generate room name automatically
    room_name = f"GiftedMinds-{course.title}-{course.id}"

    # Delete previous active sessions (optional)
    LiveSession.objects.filter(course=course, is_active=True).update(is_active=False)

    # Create new session
    session = LiveSession.objects.create(
        course=course,
        room_name=room_name
    )

    return redirect("join_live_class", session_id=session.id)


# ======================================
# LIVE CLASS
# ======================================

@login_required
def join_live_class(request, session_id):


    session = get_object_or_404(LiveSession, id=session_id)

    return render(request, "core/live_class.html", {
        "session": session
    })
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
# SUBSCRIPTION PAGE
# ======================================

@login_required
def subscription_page(request):

    levels = Level.objects.all()
    grades = Grade.objects.all()

    return render(request, "core/subscription.html", {
        "levels": levels,
        "grades": grades
    })
#=======================================
# MAKE PAYMENT
#=======================================
@login_required
def make_payment(request, subscription_id):

    subscription = get_object_or_404(
        Subscription,
        id=subscription_id,
        student=request.user
    )

    if subscription.is_active:
        return redirect("student_dashboard")

    if request.method == "POST":

        phone = request.POST.get("phone")

        response = initiate_stk_push(phone, subscription.amount)

        return render(request, "core/payment_wait.html", {
            "subscription": subscription
        })

    return render(request, "core/payment.html", {
        "subscription": subscription
    })

#=======================================
# INITIATE PAYMENT
#=======================================
@login_required
def initiate_payment(request):

    if request.method == "POST":

        phone = request.POST.get("phone")
        amount = request.POST.get("amount")

        response = initiate_stk_push(phone, amount)

        return JsonResponse(response)


# ======================================
# SUBSCRIBE
# ======================================
@login_required
def subscribe(request):

    levels = Level.objects.all()
    grades = Grade.objects.all()

    if request.method == "POST":

        level_id = request.POST.get("level")
        grade_id = request.POST.get("student_class")

        level = Level.objects.get(id=level_id)
        grade = Grade.objects.get(id=grade_id)

        subscription, created = Subscription.objects.get_or_create(
            student=request.user,
            is_active=False,
            defaults={
                "level": level,
                "grade": grade,
                "amount": level.price
    }
)


        return redirect("make_payment", subscription.id)

    return render(request, "core/subscription.html", {
        "levels": levels,
        "grades": grades
    })



#=============================================
# MPESA CALLBACK
#=============================================
@csrf_exempt
def mpesa_callback(request):

    data = json.loads(request.body)

    try:

        callback = data["Body"]["stkCallback"]
        result_code = callback["ResultCode"]

        if result_code == 0:

            metadata = callback["CallbackMetadata"]["Item"]

            phone = None
            amount = None
            account_reference = None

            for item in metadata:

                if item["Name"] == "PhoneNumber":
                    phone = item["Value"]

                if item["Name"] == "Amount":
                    amount = item["Value"]

                if item["Name"] == "AccountReference":
                    account_reference = item["Value"]

            user = User.objects.get(username=account_reference)

            subscription = Subscription.objects.filter(
                student=user,
                is_active=False
            ).last()


            subscription.start_date = timezone.now()
            subscription.end_date = timezone.now() + timedelta(days=30)
            subscription.is_active = True

            subscription.save()

    except Exception as e:
        print("MPESA CALLBACK ERROR:", e)

    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

#==================================
# CHECK PAYMENT
#==================================
def check_payment(request, subscription_id):

    subscription = Subscription.objects.get(id=subscription_id)

    return JsonResponse({
        "active": subscription.is_active
    })

