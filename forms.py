from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SelectField, TextAreaField,
                     IntegerField, DateTimeLocalField, FileField, HiddenField, FloatField)
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange


class LoginForm(FlaskForm):
    """Login form."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


class RegisterForm(FlaskForm):
    """Student registration form."""
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])


class UserForm(FlaskForm):
    """Form for creating/editing users (admin)."""
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    role = SelectField('Role', choices=[('student', 'Student'), ('teacher', 'Teacher'),
                                        ('admin', 'Admin')])
    status = SelectField('Status', choices=[('active', 'Active'), ('inactive', 'Inactive')])
    password = PasswordField('Password', validators=[Optional(), Length(min=6)])


class CourseForm(FlaskForm):
    """Form for creating/editing courses."""
    name = StringField('Course Name', validators=[DataRequired(), Length(min=2, max=150)])
    code = StringField('Course Code', validators=[DataRequired(), Length(min=2, max=20)])
    description = TextAreaField('Description', validators=[Optional()])
    teacher_id = SelectField('Assigned Teacher', coerce=int, validators=[Optional()])
    credits = IntegerField('Credits', validators=[Optional(), NumberRange(min=1, max=10)],
                           default=3)
    status = SelectField('Status', choices=[('active', 'Active'), ('inactive', 'Inactive')])


class MaterialForm(FlaskForm):
    """Form for uploading course materials."""
    course_id = SelectField('Course', coerce=int, validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=200)])
    description = TextAreaField('Description', validators=[Optional()])
    file = FileField('File')


class AssignmentForm(FlaskForm):
    """Form for creating assignments."""
    course_id = SelectField('Course', coerce=int, validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=200)])
    description = TextAreaField('Description', validators=[Optional()])
    due_date = DateTimeLocalField('Due Date', format='%Y-%m-%dT%H:%M',
                                  validators=[Optional()])
    max_marks = IntegerField('Maximum Marks', validators=[Optional(), NumberRange(min=1)],
                             default=100)


class SubmissionForm(FlaskForm):
    """Form for student assignment submissions."""
    text_content = TextAreaField('Your Answer', validators=[Optional()])
    file = FileField('Upload File')


class MarkForm(FlaskForm):
    """Form for giving marks."""
    marks = FloatField('Marks', validators=[DataRequired(), NumberRange(min=0)])
    feedback = TextAreaField('Feedback', validators=[Optional()])


class ProfileForm(FlaskForm):
    """Form for updating user profile."""
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    password = PasswordField('New Password', validators=[Optional(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password',
                                     validators=[EqualTo('password')])


class EnrollmentForm(FlaskForm):
    """Form for managing enrollments."""
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    course_id = SelectField('Course', coerce=int, validators=[DataRequired()])


class AnnouncementForm(FlaskForm):
    """Form for creating announcements."""
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=200)])
    message = TextAreaField('Message', validators=[DataRequired()])
    course_id = SelectField('Course', coerce=int, validators=[Optional()])
