import os
import uuid
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_from_directory, abort
from flask_login import login_required, current_user
from models import User, Course, Enrollment, Material, Assignment, Submission, Mark, Announcement

student_bp = Blueprint('student', __name__, url_prefix='/student')


def get_or_404(model, **kwargs):
    obj = model.objects(**kwargs).first()
    if obj is None:
        abort(404)
    return obj


def student_required(f):
    """Decorator to restrict access to student users."""
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != 'student':
            flash('Access denied. Student access required.', 'error')
            return redirect(url_for('auth.index'))
        return f(*args, **kwargs)
    return decorated


# ── Dashboard ──────────────────────────────────────────────

@student_bp.route('/dashboard')
@student_required
def dashboard():
    """Student dashboard."""
    my_enrollments = Enrollment.objects(student_id=current_user.id, status='active')
    course_ids = [e.course_id.id for e in my_enrollments if e.course_id] if my_enrollments else []

    enrolled_courses = Course.objects(id__in=course_ids) if course_ids else []

    # Stats
    total_assignments = Assignment.objects(course_id__in=course_ids).count() if course_ids else 0

    completed_assignments = 0
    if course_ids:
        assignments = Assignment.objects(course_id__in=course_ids)
        completed_assignments = Submission.objects(student_id=current_user.id, assignment_id__in=assignments).count()

    my_marks = Mark.objects(student_id=current_user.id)
    avg_marks = 0
    if my_marks:
        percentages = [m.percentage for m in my_marks]
        avg_marks = round(sum(percentages) / len(percentages), 1)

    pending_assignments = total_assignments - completed_assignments

    # Recent announcements
    announcements = Announcement.objects(course_id__in=course_ids + [None]).order_by('-created_at').limit(5) if course_ids else []

    # Upcoming assignments
    from datetime import datetime
    upcoming = Assignment.objects(course_id__in=course_ids, due_date__ne=None, due_date__gt=datetime.utcnow()).order_by('due_date').limit(5) if course_ids else []

    # Marks by course for chart
    marks_by_course = {}
    for mark in my_marks:
        course = mark.course_id
        if course:
            if course.name not in marks_by_course:
                marks_by_course[course.name] = []
            marks_by_course[course.name].append(mark.percentage)

    course_averages = {name: round(sum(percs) / len(percs), 1)
                       for name, percs in marks_by_course.items()}

    stats = {
        'enrolled_courses': enrolled_courses.count() if enrolled_courses else 0,
        'completed_assignments': completed_assignments,
        'avg_marks': avg_marks,
        'pending_assignments': max(0, pending_assignments),
    }

    # Enrollment map for progress
    enrollment_map = {e.course_id.id: e for e in my_enrollments if e.course_id} if my_enrollments else {}

    return render_template('student/dashboard.html', stats=stats, courses=enrolled_courses,
                           announcements=announcements, upcoming=upcoming,
                           course_averages=course_averages, enrollment_map=enrollment_map)


# ── Courses ────────────────────────────────────────────────

@student_bp.route('/courses')
@student_required
def courses():
    """View all available courses and enrolled courses."""
    my_enrollments = Enrollment.objects(student_id=current_user.id, status='active')
    enrolled_ids = [e.course_id.id for e in my_enrollments if e.course_id] if my_enrollments else []
    all_courses = Course.objects(status='active')
    return render_template('student/courses.html', courses=all_courses,
                           enrolled_ids=enrolled_ids)


@student_bp.route('/courses/<id>/enroll', methods=['POST'])
@student_required
def enroll(id):
    """Enroll in a course."""
    course = get_or_404(Course, id=id)
    existing = Enrollment.objects(student_id=current_user.id, course_id=course).first()
    if existing:
        flash('You are already enrolled in this course.', 'error')
        return redirect(url_for('student.courses'))
    
    enrollment = Enrollment(student_id=current_user._get_current_object(), course_id=course, status='active')
    enrollment.save()
    flash(f'Successfully enrolled in "{course.name}".', 'success')
    return redirect(url_for('student.courses'))


@student_bp.route('/courses/<id>/unenroll', methods=['POST'])
@student_required
def unenroll(id):
    """Unenroll from a course."""
    try:
        course = Course.objects.get(id=id)
        enrollment = Enrollment.objects(student_id=current_user.id, course_id=course).first()
        if enrollment:
            enrollment.delete()
            flash('Successfully unenrolled.', 'success')
    except Exception:
        pass
    return redirect(url_for('student.courses'))


# ── Materials ──────────────────────────────────────────────

@student_bp.route('/materials')
@student_required
def materials():
    """View and download course materials."""
    my_enrollments = Enrollment.objects(student_id=current_user.id, status='active')
    course_ids = [e.course_id.id for e in my_enrollments if e.course_id] if my_enrollments else []
    all_materials = Material.objects(course_id__in=course_ids).order_by('-created_at') if course_ids else []
    enrolled_courses = Course.objects(id__in=course_ids) if course_ids else []
    return render_template('student/materials.html', materials=all_materials,
                           courses=enrolled_courses)


@student_bp.route('/materials/<id>/download')
@student_required
def download_material(id):
    """Download a material file."""
    material = get_or_404(Material, id=id)
    # Verify student is enrolled in the course
    enrollment = Enrollment.objects(student_id=current_user.id, course_id=material.course_id, status='active').first()
    
    if not enrollment:
        flash('Access denied. You are not enrolled in this course.', 'error')
        return redirect(url_for('student.materials'))
        
    if material.filename:
        return send_from_directory(
            current_app.config['MATERIALS_FOLDER'],
            material.filename,
            as_attachment=True,
            download_name=material.original_filename
        )
    flash('No file attached to this material.', 'error')
    return redirect(url_for('student.materials'))


# ── Assignments ────────────────────────────────────────────

@student_bp.route('/assignments')
@student_required
def assignments():
    """View assignments for enrolled courses."""
    my_enrollments = Enrollment.objects(student_id=current_user.id, status='active')
    course_ids = [e.course_id.id for e in my_enrollments if e.course_id] if my_enrollments else []
    
    all_assignments = Assignment.objects(course_id__in=course_ids).order_by('due_date') if course_ids else []

    # Check which assignments have been submitted
    submitted_ids = [s.assignment_id.id for s in Submission.objects(student_id=current_user.id) if s.assignment_id]

    return render_template('student/assignments.html', assignments=all_assignments,
                           submitted_ids=submitted_ids)


@student_bp.route('/assignments/<id>/submit', methods=['POST'])
@student_required
def submit_assignment(id):
    """Submit an assignment."""
    assignment = get_or_404(Assignment, id=id)

    # Verify enrollment
    enrollment = Enrollment.objects(student_id=current_user.id, course_id=assignment.course_id, status='active').first()
    if not enrollment:
        flash('Access denied.', 'error')
        return redirect(url_for('student.assignments'))

    # Check for existing submission
    existing = Submission.objects(assignment_id=assignment, student_id=current_user.id).first()
    if existing:
        flash('You have already submitted this assignment.', 'error')
        return redirect(url_for('student.assignments'))

    text_content = request.form.get('text_content', '')
    file = request.files.get('file')
    filename = ''
    original_filename = ''
    if file and file.filename:
        original_filename = file.filename
        ext = os.path.splitext(file.filename)[1]
        filename = f'{uuid.uuid4().hex}{ext}'
        filepath = os.path.join(current_app.config['SUBMISSIONS_FOLDER'], filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)

    submission = Submission(
        assignment_id=assignment, student_id=current_user._get_current_object(),
        text_content=text_content, filename=filename,
        original_filename=original_filename, status='pending'
    )
    submission.save()
    flash(f'Assignment "{assignment.title}" submitted successfully.', 'success')
    return redirect(url_for('student.assignments'))


# ── Submissions ────────────────────────────────────────────

@student_bp.route('/submissions')
@student_required
def submissions():
    """View my submissions."""
    my_submissions = Submission.objects(student_id=current_user.id).order_by('-submitted_at')
    return render_template('student/submissions.html', submissions=my_submissions)


# ── Marks ──────────────────────────────────────────────────

@student_bp.route('/marks')
@student_required
def marks():
    """View my marks."""
    my_marks = Mark.objects(student_id=current_user.id).order_by('-graded_at')

    # Calculate averages by course
    course_marks = {}
    for mark in my_marks:
        course = mark.course_id
        if course:
            if course.name not in course_marks:
                course_marks[course.name] = []
            course_marks[course.name].append(mark.percentage)

    course_averages = {name: round(sum(percs) / len(percs), 1)
                       for name, percs in course_marks.items()}

    overall_avg = 0
    if course_averages:
        overall_avg = round(sum(course_averages.values()) / len(course_averages), 1)

    return render_template('student/marks.html', marks=my_marks,
                           course_averages=course_averages, overall_avg=overall_avg)


# ── Profile ────────────────────────────────────────────────

@student_bp.route('/profile', methods=['GET', 'POST'])
@student_required
def profile():
    """Student profile."""
    if request.method == 'POST':
        current_user.name = request.form.get('name', current_user.name)
        current_user.phone = request.form.get('phone', current_user.phone)
        if request.form.get('password'):
            current_user.set_password(request.form['password'])
        current_user.save()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('student.profile'))
    return render_template('student/profile.html')
