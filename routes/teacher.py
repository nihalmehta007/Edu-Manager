import os
import uuid
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from models import User, Course, Enrollment, Material, Assignment, Submission, Mark, Announcement
from forms import MaterialForm, AssignmentForm, MarkForm, ProfileForm, AnnouncementForm

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')


def get_or_404(model, **kwargs):
    obj = model.objects(**kwargs).first()
    if obj is None:
        abort(404)
    return obj


def teacher_required(f):
    """Decorator to restrict access to teacher users."""
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != 'teacher':
            flash('Access denied. Teacher privileges required.', 'error')
            return redirect(url_for('auth.index'))
        return f(*args, **kwargs)
    return decorated


# ── Dashboard ──────────────────────────────────────────────

@teacher_bp.route('/dashboard')
@teacher_required
def dashboard():
    """Teacher dashboard."""
    my_courses = Course.objects(teacher_id=current_user.id, status='active')
    
    total_students = 0
    total_assignments = 0
    pending_submissions = 0
    recent_submissions = []
    upcoming_assignments = []
    
    if my_courses:
        total_students = Enrollment.objects(course_id__in=my_courses, status='active').count()
        total_assignments = Assignment.objects(course_id__in=my_courses).count()
        
        assignments = Assignment.objects(course_id__in=my_courses)
        if assignments:
            pending_submissions = Submission.objects(assignment_id__in=assignments, status='pending').count()
            recent_submissions = Submission.objects(assignment_id__in=assignments).order_by('-submitted_at').limit(5)
            
        upcoming_assignments = Assignment.objects(course_id__in=my_courses, due_date__ne=None).order_by('due_date').limit(5)

    stats = {
        'courses': my_courses.count(),
        'students': total_students,
        'assignments': total_assignments,
        'pending_submissions': pending_submissions,
    }
    return render_template('teacher/dashboard.html', stats=stats, courses=my_courses,
                           recent_submissions=recent_submissions,
                           upcoming_assignments=upcoming_assignments)


# ── Courses ────────────────────────────────────────────────

@teacher_bp.route('/courses')
@teacher_required
def courses():
    """View assigned courses."""
    my_courses = Course.objects(teacher_id=current_user.id)
    return render_template('teacher/courses.html', courses=my_courses)


# ── Students ───────────────────────────────────────────────

@teacher_bp.route('/students')
@teacher_required
def students():
    """View enrolled students across teacher's courses."""
    course_id = request.args.get('course_id')
    my_courses = Course.objects(teacher_id=current_user.id, status='active')

    selected_course = None
    enrolled_students = []
    if course_id:
        try:
            selected_course = Course.objects.get(id=course_id)
            if selected_course.teacher_id.id == current_user.id:
                enrolled_students = Enrollment.objects(course_id=selected_course, status='active')
        except Exception:
            pass

    return render_template('teacher/students.html', courses=my_courses,
                           selected_course=selected_course,
                           enrolled_students=enrolled_students,
                           current_course_id=course_id)


# ── Materials ──────────────────────────────────────────────

@teacher_bp.route('/materials')
@teacher_required
def materials():
    """View and upload materials for assigned courses."""
    my_courses = Course.objects(teacher_id=current_user.id, status='active')
    all_materials = []
    if my_courses:
        all_materials = Material.objects(course_id__in=my_courses).order_by('-created_at')
    return render_template('teacher/materials.html', courses=my_courses,
                           materials=all_materials)


@teacher_bp.route('/materials/upload', methods=['POST'])
@teacher_required
def upload_material():
    """Upload study material."""
    course_id = request.form.get('course_id')
    title = request.form.get('title')
    description = request.form.get('description', '')

    try:
        course = Course.objects.get(id=course_id)
        if course.teacher_id.id != current_user.id:
            flash('Access denied.', 'error')
            return redirect(url_for('teacher.materials'))
    except Exception:
        flash('Invalid course.', 'error')
        return redirect(url_for('teacher.materials'))

    file = request.files.get('file')
    filename = ''
    original_filename = ''
    if file and file.filename:
        original_filename = file.filename
        ext = os.path.splitext(file.filename)[1]
        filename = f'{uuid.uuid4().hex}{ext}'
        filepath = os.path.join(current_app.config['MATERIALS_FOLDER'], filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)

    material = Material(course_id=course, title=title, description=description,
                        filename=filename, original_filename=original_filename,
                        uploaded_by=current_user._get_current_object())
    material.save()
    flash(f'Material "{title}" uploaded successfully.', 'success')
    return redirect(url_for('teacher.materials'))


@teacher_bp.route('/materials/<id>/delete', methods=['POST'])
@teacher_required
def delete_material(id):
    """Delete a material."""
    material = get_or_404(Material, id=id)
    if not material.course_id or not material.course_id.teacher_id or material.course_id.teacher_id.id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('teacher.materials'))
        
    if material.filename:
        filepath = os.path.join(current_app.config['MATERIALS_FOLDER'], material.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
    material.delete()
    flash('Material deleted.', 'success')
    return redirect(url_for('teacher.materials'))


# ── Assignments ────────────────────────────────────────────

@teacher_bp.route('/assignments')
@teacher_required
def assignments():
    """View and create assignments."""
    my_courses = Course.objects(teacher_id=current_user.id, status='active')
    all_assignments = []
    if my_courses:
        all_assignments = Assignment.objects(course_id__in=my_courses).order_by('-created_at')
    return render_template('teacher/assignments.html', courses=my_courses,
                           assignments=all_assignments)


@teacher_bp.route('/assignments/create', methods=['POST'])
@teacher_required
def create_assignment():
    """Create a new assignment."""
    course_id = request.form.get('course_id')
    title = request.form.get('title')
    description = request.form.get('description', '')
    due_date_str = request.form.get('due_date')
    max_marks = request.form.get('max_marks', 100, type=int)

    try:
        course = Course.objects.get(id=course_id)
        if course.teacher_id.id != current_user.id:
            flash('Access denied.', 'error')
            return redirect(url_for('teacher.assignments'))
    except Exception:
        flash('Invalid course.', 'error')
        return redirect(url_for('teacher.assignments'))

    from datetime import datetime
    due_date = None
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            pass

    assignment = Assignment(course_id=course, title=title, description=description,
                            due_date=due_date, max_marks=max_marks,
                            created_by=current_user._get_current_object())
    assignment.save()
    flash(f'Assignment "{title}" created.', 'success')
    return redirect(url_for('teacher.assignments'))


@teacher_bp.route('/assignments/<id>/delete', methods=['POST'])
@teacher_required
def delete_assignment(id):
    """Delete an assignment."""
    assignment = get_or_404(Assignment, id=id)
    if not assignment.course_id or not assignment.course_id.teacher_id or assignment.course_id.teacher_id.id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('teacher.assignments'))
    assignment.delete()
    flash('Assignment deleted.', 'success')
    return redirect(url_for('teacher.assignments'))


# ── Submissions ────────────────────────────────────────────

@teacher_bp.route('/submissions')
@teacher_required
def submissions():
    """View student submissions."""
    my_courses = Course.objects(teacher_id=current_user.id, status='active')
    
    assignment_id = request.args.get('assignment_id')
    course_filter = request.args.get('course_id')
    
    all_submissions = []
    all_assignments = []
    
    if my_courses:
        all_assignments = Assignment.objects(course_id__in=my_courses)
        
        query_kwargs = {}
        if assignment_id:
            query_kwargs['assignment_id'] = assignment_id
        elif course_filter:
            assignments_in_course = Assignment.objects(course_id=course_filter)
            query_kwargs['assignment_id__in'] = assignments_in_course
        else:
            query_kwargs['assignment_id__in'] = all_assignments
            
        all_submissions = Submission.objects(**query_kwargs).order_by('-submitted_at')

    return render_template('teacher/submissions.html', submissions=all_submissions,
                           courses=my_courses, assignments=all_assignments,
                           current_assignment_id=assignment_id,
                           current_course_id=course_filter)


# ── Marks ──────────────────────────────────────────────────

@teacher_bp.route('/marks')
@teacher_required
def marks():
    """View and give marks."""
    my_courses = Course.objects(teacher_id=current_user.id, status='active')
    
    all_marks = []
    ungraded = []
    
    if my_courses:
        all_marks = Mark.objects(course_id__in=my_courses).order_by('-graded_at')
        
        assignments = Assignment.objects(course_id__in=my_courses)
        ungraded = Submission.objects(assignment_id__in=assignments, status='pending').order_by('-submitted_at')

    return render_template('teacher/marks.html', marks=all_marks, ungraded=ungraded,
                           courses=my_courses)


@teacher_bp.route('/marks/give', methods=['POST'])
@teacher_required
def give_marks():
    """Give marks for a submission."""
    submission_id = request.form.get('submission_id')
    marks_value = request.form.get('marks', type=float)
    feedback = request.form.get('feedback', '')

    submission = get_or_404(Submission, id=submission_id)
    assignment = submission.assignment_id
    course = assignment.course_id

    if not course or not course.teacher_id or course.teacher_id.id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('teacher.marks'))

    existing = Mark.objects(student_id=submission.student_id, assignment_id=assignment).first()

    if existing:
        existing.marks = marks_value
        existing.feedback = feedback
        from datetime import datetime
        existing.graded_at = datetime.utcnow()
        existing.save()
    else:
        mark = Mark(
            student_id=submission.student_id,
            course_id=course,
            assignment_id=assignment,
            marks=marks_value,
            max_marks=assignment.max_marks,
            feedback=feedback,
            graded_by=current_user._get_current_object()
        )
        mark.save()

    submission.status = 'graded'
    submission.save()
    flash('Marks submitted successfully.', 'success')
    return redirect(url_for('teacher.marks'))


# ── Profile ────────────────────────────────────────────────

@teacher_bp.route('/profile', methods=['GET', 'POST'])
@teacher_required
def profile():
    """Teacher profile."""
    if request.method == 'POST':
        current_user.name = request.form.get('name', current_user.name)
        current_user.phone = request.form.get('phone', current_user.phone)
        if request.form.get('password'):
            current_user.set_password(request.form['password'])
        current_user.save()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('teacher.profile'))
    return render_template('teacher/profile.html')
