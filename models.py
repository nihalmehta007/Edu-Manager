import mongoengine as db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(UserMixin, db.Document):
    """User model for Admin, Teacher, and Student roles."""
    meta = {'collection': 'users'}

    name = db.StringField(max_length=100, required=True)
    email = db.StringField(max_length=120, unique=True, required=True)
    password_hash = db.StringField(max_length=256, required=True)
    role = db.StringField(max_length=20, required=True, default='student')
    phone = db.StringField(max_length=20, default='')
    status = db.StringField(max_length=20, default='active')
    created_at = db.DateTimeField(default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def initials(self):
        parts = self.name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        return self.name[0:2].upper()
    
    @property
    def taught_courses(self):
        if self.role == 'teacher':
            return Course.objects(teacher_id=self)
        return []

    def __repr__(self):
        return f'<User {self.name} ({self.role})>'


class Course(db.Document):
    """Course model."""
    meta = {'collection': 'courses'}

    name = db.StringField(max_length=150, required=True)
    code = db.StringField(max_length=20, unique=True, required=True)
    description = db.StringField(default='')
    teacher_id = db.ReferenceField(User, null=True, reverse_delete_rule=db.NULLIFY)
    credits = db.IntField(default=3)
    status = db.StringField(max_length=20, default='active')
    created_at = db.DateTimeField(default=datetime.utcnow)

    @property
    def teacher(self):
        return self.teacher_id

    @property
    def enrolled_count(self):
        return Enrollment.objects(course_id=self, status='active').count()

    def __repr__(self):
        return f'<Course {self.code}: {self.name}>'


class Enrollment(db.Document):
    """Enrollment linking students to courses."""
    meta = {
        'collection': 'enrollments',
        'indexes': [
            {'fields': ('student_id', 'course_id'), 'unique': True}
        ]
    }

    student_id = db.ReferenceField(User, required=True, reverse_delete_rule=db.CASCADE)
    course_id = db.ReferenceField(Course, required=True, reverse_delete_rule=db.CASCADE)
    enrolled_at = db.DateTimeField(default=datetime.utcnow)
    status = db.StringField(max_length=20, default='active')
    progress = db.IntField(default=0)

    @property
    def student(self):
        return self.student_id

    @property
    def course(self):
        return self.course_id

    def __repr__(self):
        return f'<Enrollment student={self.student_id.id} course={self.course_id.id}>'


class Material(db.Document):
    """Course material (uploaded files)."""
    meta = {'collection': 'materials'}

    course_id = db.ReferenceField(Course, required=True, reverse_delete_rule=db.CASCADE)
    title = db.StringField(max_length=200, required=True)
    description = db.StringField(default='')
    filename = db.StringField(max_length=300, default='')
    original_filename = db.StringField(max_length=300, default='')
    uploaded_by = db.ReferenceField(User, reverse_delete_rule=db.NULLIFY)
    created_at = db.DateTimeField(default=datetime.utcnow)

    @property
    def course(self):
        return self.course_id

    @property
    def uploader(self):
        return self.uploaded_by

    def __repr__(self):
        return f'<Material {self.title}>'


class Assignment(db.Document):
    """Assignment created by teachers."""
    meta = {'collection': 'assignments'}

    course_id = db.ReferenceField(Course, required=True, reverse_delete_rule=db.CASCADE)
    title = db.StringField(max_length=200, required=True)
    description = db.StringField(default='')
    due_date = db.DateTimeField(null=True)
    max_marks = db.IntField(default=100)
    created_by = db.ReferenceField(User, reverse_delete_rule=db.NULLIFY)
    created_at = db.DateTimeField(default=datetime.utcnow)

    @property
    def course(self):
        return self.course_id

    @property
    def creator(self):
        return self.created_by

    @property
    def submissions(self):
        return Submission.objects(assignment_id=self)

    @property
    def is_overdue(self):
        if self.due_date:
            return datetime.utcnow() > self.due_date
        return False

    def __repr__(self):
        return f'<Assignment {self.title}>'


class Submission(db.Document):
    """Student submission for an assignment."""
    meta = {'collection': 'submissions'}

    assignment_id = db.ReferenceField(Assignment, required=True, reverse_delete_rule=db.CASCADE)
    student_id = db.ReferenceField(User, required=True, reverse_delete_rule=db.CASCADE)
    filename = db.StringField(max_length=300, default='')
    original_filename = db.StringField(max_length=300, default='')
    text_content = db.StringField(default='')
    submitted_at = db.DateTimeField(default=datetime.utcnow)
    status = db.StringField(max_length=20, default='pending')

    @property
    def assignment(self):
        return self.assignment_id

    @property
    def student(self):
        return self.student_id

    def __repr__(self):
        return f'<Submission assignment={self.assignment_id.id} student={self.student_id.id}>'


class Mark(db.Document):
    """Marks/grades given to students."""
    meta = {'collection': 'marks'}

    student_id = db.ReferenceField(User, required=True, reverse_delete_rule=db.CASCADE)
    course_id = db.ReferenceField(Course, required=True, reverse_delete_rule=db.CASCADE)
    assignment_id = db.ReferenceField(Assignment, required=True, reverse_delete_rule=db.CASCADE)
    marks = db.FloatField(required=True)
    max_marks = db.FloatField(required=True, default=100)
    feedback = db.StringField(default='')
    graded_by = db.ReferenceField(User, reverse_delete_rule=db.NULLIFY)
    graded_at = db.DateTimeField(default=datetime.utcnow)

    @property
    def student(self):
        return self.student_id
        
    @property
    def course(self):
        return self.course_id
        
    @property
    def assignment(self):
        return self.assignment_id
        
    @property
    def grader(self):
        return self.graded_by

    @property
    def percentage(self):
        if self.max_marks > 0:
            return round((self.marks / self.max_marks) * 100, 1)
        return 0

    def __repr__(self):
        return f'<Mark student={self.student_id.id} marks={self.marks}/{self.max_marks}>'


class Announcement(db.Document):
    """Announcements for courses."""
    meta = {'collection': 'announcements'}

    title = db.StringField(max_length=200, required=True)
    message = db.StringField(default='')
    course_id = db.ReferenceField(Course, null=True, reverse_delete_rule=db.CASCADE)
    created_by = db.ReferenceField(User, reverse_delete_rule=db.NULLIFY)
    created_at = db.DateTimeField(default=datetime.utcnow)

    @property
    def course(self):
        return self.course_id
        
    @property
    def author(self):
        return self.created_by

    def __repr__(self):
        return f'<Announcement {self.title}>'
