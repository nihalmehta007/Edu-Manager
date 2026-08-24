import os
import uuid
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_from_directory, abort
from flask_login import login_required, current_user
from models import db, User, Course, Enrollment, Material, Assignment, Submission, Mark, Announcement
from forms import UserForm, CourseForm, MaterialForm, EnrollmentForm
from mongoengine.errors import DoesNotExist

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

import math

class Pagination:
    def __init__(self, query, page, per_page):
        self.query = query
        self.page = page
        self.per_page = per_page
        self.total = query.count()
        self.items = list(query.skip((page - 1) * per_page).limit(per_page))
        self.pages = int(math.ceil(self.total / float(per_page)))
        self.prev_num = page - 1 if page > 1 else None
        self.next_num = page + 1 if page < self.pages else None
        self.has_prev = self.prev_num is not None
        self.has_next = self.next_num is not None

    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


def admin_required(f):
    """Decorator to restrict access to admin users."""
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('auth.index'))
        return f(*args, **kwargs)
    return decorated


def get_or_404(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except DoesNotExist:
        abort(404)


# ── Dashboard ──────────────────────────────────────────────

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with stats and overview."""
    stats = {
        'students': User.objects(role='student').count(),
        'teachers': User.objects(role='teacher').count(),
        'courses': Course.objects.count(),
        'enrollments': Enrollment.objects(status='active').count(),
    }
    recent_enrollments = Enrollment.objects().order_by('-enrolled_at').limit(5)
    return render_template('admin/dashboard.html', stats=stats,
                           recent_enrollments=recent_enrollments)


# ── Students ───────────────────────────────────────────────

@admin_bp.route('/students')
@admin_required
def students():
    """List all students."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    query = User.objects(role='student')
    if search:
        query = query.filter(name__icontains=search)
    pagination = Pagination(query.order_by('-created_at'), page, 10)
    return render_template('admin/students.html', pagination=pagination, search=search)


@admin_bp.route('/students/add', methods=['GET', 'POST'])
@admin_required
def add_student():
    """Add a new student."""
    form = UserForm()
    form.role.data = 'student'
    if form.validate_on_submit():
        if User.objects(email=form.email.data).first():
            flash('A user with this email already exists.', 'error')
            pagination = Pagination(User.objects(role='student'), 1, 10)
            return render_template('admin/students.html', form=form, adding=True,
                                   pagination=pagination, search='')
        user = User(name=form.name.data, email=form.email.data, phone=form.phone.data or '',
                    role='student', status=form.status.data)
        user.set_password(form.password.data or 'student123')
        user.save()
        flash(f'Student "{user.name}" added successfully.', 'success')
        return redirect(url_for('admin.students'))
    return redirect(url_for('admin.students'))


@admin_bp.route('/students/<id>/edit', methods=['POST'])
@admin_required
def edit_student(id):
    """Edit a student."""
    user = get_or_404(User, id=id)
    user.name = request.form.get('name', user.name)
    user.email = request.form.get('email', user.email)
    user.phone = request.form.get('phone', user.phone)
    user.status = request.form.get('status', user.status)
    if request.form.get('password'):
        user.set_password(request.form['password'])
    user.save()
    flash(f'Student "{user.name}" updated successfully.', 'success')
    return redirect(url_for('admin.students'))


@admin_bp.route('/students/<id>/delete', methods=['POST'])
@admin_required
def delete_student(id):
    """Delete a student."""
    user = get_or_404(User, id=id)
    user.delete()
    flash(f'Student "{user.name}" deleted.', 'success')
    return redirect(url_for('admin.students'))


# ── Teachers ───────────────────────────────────────────────

@admin_bp.route('/teachers')
@admin_required
def teachers():
    """List all teachers."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    query = User.objects(role='teacher')
    if search:
        query = query.filter(name__icontains=search)
    pagination = Pagination(query.order_by('-created_at'), page, 10)
    return render_template('admin/teachers.html', pagination=pagination, search=search)


@admin_bp.route('/teachers/add', methods=['POST'])
@admin_required
def add_teacher():
    """Add a new teacher."""
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone', '')
    password = request.form.get('password', 'teacher123')
    if User.objects(email=email).first():
        flash('A user with this email already exists.', 'error')
        return redirect(url_for('admin.teachers'))
    user = User(name=name, email=email, phone=phone, role='teacher', status='active')
    user.set_password(password)
    user.save()
    flash(f'Teacher "{user.name}" added successfully.', 'success')
    return redirect(url_for('admin.teachers'))


@admin_bp.route('/teachers/<id>/edit', methods=['POST'])
@admin_required
def edit_teacher(id):
    """Edit a teacher."""
    user = get_or_404(User, id=id)
    user.name = request.form.get('name', user.name)
    user.email = request.form.get('email', user.email)
    user.phone = request.form.get('phone', user.phone)
    user.status = request.form.get('status', user.status)
    if request.form.get('password'):
        user.set_password(request.form['password'])
    user.save()
    flash(f'Teacher "{user.name}" updated.', 'success')
    return redirect(url_for('admin.teachers'))


@admin_bp.route('/teachers/<id>/delete', methods=['POST'])
@admin_required
def delete_teacher(id):
    """Delete a teacher."""
    user = get_or_404(User, id=id)
    user.delete()
    flash(f'Teacher "{user.name}" deleted.', 'success')
    return redirect(url_for('admin.teachers'))


# ── Courses ────────────────────────────────────────────────

@admin_bp.route('/courses')
@admin_required
def courses():
    """List all courses."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    query = Course.objects()
    if search:
        query = query.filter(name__icontains=search)
    pagination = Pagination(query.order_by('-created_at'), page, 10)
    all_teachers = User.objects(role='teacher', status='active')
    return render_template('admin/courses.html', pagination=pagination, search=search,
                           teachers=all_teachers)


@admin_bp.route('/courses/add', methods=['POST'])
@admin_required
def add_course():
    """Add a new course."""
    name = request.form.get('name')
    code = request.form.get('code')
    description = request.form.get('description', '')
    teacher_id = request.form.get('teacher_id')
    credits = request.form.get('credits', 3, type=int)
    if Course.objects(code=code).first():
        flash('A course with this code already exists.', 'error')
        return redirect(url_for('admin.courses'))
    
    teacher = get_or_404(User, id=teacher_id) if teacher_id else None
    course = Course(name=name, code=code, description=description,
                    teacher_id=teacher, credits=credits, status='active')
    course.save()
    flash(f'Course "{course.name}" created.', 'success')
    return redirect(url_for('admin.courses'))


@admin_bp.route('/courses/<id>/edit', methods=['POST'])
@admin_required
def edit_course(id):
    """Edit a course."""
    course = get_or_404(Course, id=id)
    course.name = request.form.get('name', course.name)
    course.code = request.form.get('code', course.code)
    course.description = request.form.get('description', course.description)
    teacher_id = request.form.get('teacher_id')
    if teacher_id:
        course.teacher_id = get_or_404(User, id=teacher_id)
    course.credits = request.form.get('credits', course.credits, type=int)
    course.status = request.form.get('status', course.status)
    course.save()
    flash(f'Course "{course.name}" updated.', 'success')
    return redirect(url_for('admin.courses'))


@admin_bp.route('/courses/<id>/delete', methods=['POST'])
@admin_required
def delete_course(id):
    """Delete a course."""
    course = get_or_404(Course, id=id)
    course.delete()
    flash(f'Course "{course.name}" deleted.', 'success')
    return redirect(url_for('admin.courses'))


# ── Enrollments ────────────────────────────────────────────

@admin_bp.route('/enrollments')
@admin_required
def enrollments():
    """List all enrollments."""
    page = request.args.get('page', 1, type=int)
    pagination = Pagination(Enrollment.objects().order_by('-enrolled_at'), page, 10)
    all_students = User.objects(role='student', status='active')
    all_courses = Course.objects(status='active')
    return render_template('admin/enrollments.html', pagination=pagination,
                           students=all_students, courses=all_courses)


@admin_bp.route('/enrollments/add', methods=['POST'])
@admin_required
def add_enrollment():
    """Add a new enrollment."""
    student_id = request.form.get('student_id')
    course_id = request.form.get('course_id')
    
    student = get_or_404(User, id=student_id)
    course = get_or_404(Course, id=course_id)
    
    existing = Enrollment.objects(student_id=student, course_id=course).first()
    if existing:
        flash('Student is already enrolled in this course.', 'error')
        return redirect(url_for('admin.enrollments'))
        
    enrollment = Enrollment(student_id=student, course_id=course, status='active')
    enrollment.save()
    flash('Enrollment added successfully.', 'success')
    return redirect(url_for('admin.enrollments'))


@admin_bp.route('/enrollments/<id>/delete', methods=['POST'])
@admin_required
def delete_enrollment(id):
    """Delete an enrollment."""
    enrollment = get_or_404(Enrollment, id=id)
    enrollment.delete()
    flash('Enrollment removed.', 'success')
    return redirect(url_for('admin.enrollments'))


# ── Materials ──────────────────────────────────────────────

@admin_bp.route('/materials')
@admin_required
def materials():
    """List all materials."""
    page = request.args.get('page', 1, type=int)
    all_courses = Course.objects(status='active')
    pagination = Pagination(Material.objects().order_by('-created_at'), page, 10)
    return render_template('admin/materials.html', pagination=pagination, courses=all_courses)


@admin_bp.route('/materials/upload', methods=['POST'])
@admin_required
def upload_material():
    """Upload a course material."""
    course_id = request.form.get('course_id')
    title = request.form.get('title')
    description = request.form.get('description', '')
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

    course = get_or_404(Course, id=course_id)
    material = Material(course_id=course, title=title, description=description,
                        filename=filename, original_filename=original_filename,
                        uploaded_by=current_user._get_current_object())
    material.save()
    flash(f'Material "{title}" uploaded.', 'success')
    return redirect(url_for('admin.materials'))


@admin_bp.route('/materials/<id>/delete', methods=['POST'])
@admin_required
def delete_material(id):
    """Delete a material."""
    material = get_or_404(Material, id=id)
    if material.filename:
        filepath = os.path.join(current_app.config['MATERIALS_FOLDER'], material.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
    material.delete()
    flash('Material deleted.', 'success')
    return redirect(url_for('admin.materials'))


# ── Roles ──────────────────────────────────────────────────

@admin_bp.route('/roles')
@admin_required
def roles():
    """Manage roles and view permissions."""
    roles_data = [
        {'role': 'Admin', 'description': 'Full access to all modules', 'count': User.objects(role='admin').count()},
        {'role': 'Teacher', 'description': 'Access to assigned courses', 'count': User.objects(role='teacher').count()},
        {'role': 'Student', 'description': 'Access to enrolled courses only', 'count': User.objects(role='student').count()},
    ]
    return render_template('admin/roles.html', roles=roles_data)


# ── Settings ───────────────────────────────────────────────

@admin_bp.route('/settings')
@admin_required
def settings():
    """System settings."""
    total_users = User.objects().count()
    total_courses = Course.objects().count()
    return render_template('admin/settings.html', total_users=total_users,
                           total_courses=total_courses)
