from models import db, User, Course, Enrollment, Material, Assignment, Submission, Mark, Announcement
from datetime import datetime, timedelta
import random

def seed_database():
    """Seed the database with demo data."""

    # Clear existing data
    Mark.objects.delete()
    Submission.objects.delete()
    Assignment.objects.delete()
    Material.objects.delete()
    Enrollment.objects.delete()
    Announcement.objects.delete()
    Course.objects.delete()
    User.objects.delete()

    # ── Users ──────────────────────────────────────────────
    admin = User(name='Admin User', email='admin@edumanage.com', role='admin',
                 phone='555-0100', status='active')
    admin.set_password('admin123')
    admin.save()

    teachers = []
    teacher_data = [
        ('Dr. Sarah Johnson', 'sarah@edumanage.com', '555-0201'),
        ('Prof. Michael Chen', 'michael@edumanage.com', '555-0202'),
        ('Dr. Emily Rodriguez', 'emily@edumanage.com', '555-0203'),
        ('Prof. David Kim', 'david@edumanage.com', '555-0204'),
        ('Dr. Lisa Wang', 'lisa@edumanage.com', '555-0205'),
    ]
    for name, email, phone in teacher_data:
        t = User(name=name, email=email, role='teacher', phone=phone, status='active')
        t.set_password('teacher123')
        t.save()
        teachers.append(t)

    students = []
    student_data = [
        ('John Doe', 'john@student.com', '555-0301'),
        ('Jane Smith', 'jane@student.com', '555-0302'),
        ('Michael Brown', 'michael.b@student.com', '555-0303'),
        ('Emily Davis', 'emily.d@student.com', '555-0304'),
        ('David Wilson', 'david.w@student.com', '555-0305'),
        ('Sarah Taylor', 'sarah.t@student.com', '555-0306'),
        ('James Anderson', 'james@student.com', '555-0307'),
        ('Maria Garcia', 'maria@student.com', '555-0308'),
        ('Robert Martinez', 'robert@student.com', '555-0309'),
        ('Jennifer Lopez', 'jennifer@student.com', '555-0310'),
        ('William Thomas', 'william@student.com', '555-0311'),
        ('Linda Jackson', 'linda@student.com', '555-0312'),
        ('Richard White', 'richard@student.com', '555-0313'),
        ('Patricia Harris', 'patricia@student.com', '555-0314'),
        ('Charles Martin', 'charles@student.com', '555-0315'),
    ]
    for name, email, phone in student_data:
        s = User(name=name, email=email, role='student', phone=phone, status='active')
        s.set_password('student123')
        s.save()
        students.append(s)

    # Set a couple students as inactive for variety
    students[3].status = 'inactive'
    students[3].save()

    # ── Courses ────────────────────────────────────────────
    courses_data = [
        ('Web Development', 'CS101', 'Modern web development with HTML, CSS, and JavaScript', teachers[0], 4),
        ('Data Structures', 'CS201', 'Fundamental data structures and algorithms', teachers[1], 3),
        ('Database Systems', 'CS301', 'Relational databases, SQL, and NoSQL systems', teachers[2], 3),
        ('Operating Systems', 'CS401', 'OS concepts: processes, memory, file systems', teachers[3], 4),
        ('Machine Learning', 'CS501', 'Introduction to ML algorithms and applications', teachers[0], 3),
        ('Computer Networks', 'CS601', 'Network protocols, architecture, and security', teachers[4], 3),
        ('Software Engineering', 'CS701', 'Software development lifecycle and best practices', teachers[1], 3),
        ('UX/UI Design', 'DS101', 'User experience and interface design principles', teachers[2], 2),
    ]
    courses = []
    for name, code, desc, teacher, credits in courses_data:
        c = Course(name=name, code=code, description=desc, teacher_id=teacher,
                   credits=credits, status='active')
        c.save()
        courses.append(c)

    # ── Enrollments ────────────────────────────────────────
    enrollments = []
    for student in students:
        if student.status == 'inactive':
            continue
        # Each student enrolls in 2-4 random courses
        num_courses = random.randint(2, 4)
        selected = random.sample(courses, min(num_courses, len(courses)))
        for course in selected:
            e = Enrollment(
                student_id=student,
                course_id=course,
                status='active',
                progress=random.randint(10, 95),
                enrolled_at=datetime.utcnow() - timedelta(days=random.randint(1, 90))
            )
            e.save()
            enrollments.append(e)

    # ── Materials ──────────────────────────────────────────
    materials_data = [
        (courses[0], 'HTML & CSS Basics', 'Introduction to HTML5 and CSS3', teachers[0]),
        (courses[0], 'JavaScript Fundamentals', 'Variables, functions, and DOM', teachers[0]),
        (courses[1], 'Arrays and Linked Lists', 'Linear data structures overview', teachers[1]),
        (courses[1], 'Trees and Graphs', 'Non-linear data structures', teachers[1]),
        (courses[2], 'SQL Fundamentals', 'SELECT, JOIN, and aggregation queries', teachers[2]),
        (courses[2], 'Database Normalization', '1NF through BCNF explained', teachers[2]),
        (courses[3], 'Process Management', 'Scheduling algorithms and IPC', teachers[3]),
        (courses[4], 'Linear Regression', 'Supervised learning basics', teachers[0]),
    ]
    materials = []
    for course, title, desc, teacher in materials_data:
        m = Material(course_id=course, title=title, description=desc, uploaded_by=teacher,
                     original_filename=f'{title.lower().replace(" ", "_")}.pdf',
                     created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)))
        m.save()
        materials.append(m)

    # ── Assignments ────────────────────────────────────────
    assignments_data = [
        (courses[0], 'Assignment 1', 'Build a responsive landing page', 14, 100, teachers[0]),
        (courses[0], 'Project 1', 'Create a portfolio website', 28, 150, teachers[0]),
        (courses[1], 'Assignment 1', 'Implement a linked list in Python', 10, 100, teachers[1]),
        (courses[1], 'Assignment 2', 'Binary search tree operations', 21, 100, teachers[1]),
        (courses[2], 'Assignment 1', 'Design an ER diagram for a library system', 14, 80, teachers[2]),
        (courses[2], 'Quiz 1', 'SQL query writing quiz', 7, 50, teachers[2]),
        (courses[3], 'Quiz 1', 'Process scheduling problems', 10, 50, teachers[3]),
        (courses[4], 'Assignment 1', 'Linear regression implementation', 21, 100, teachers[0]),
    ]
    assignments = []
    for course, title, desc, days_until_due, max_marks, teacher in assignments_data:
        a = Assignment(
            course_id=course, title=title, description=desc,
            due_date=datetime.utcnow() + timedelta(days=days_until_due),
            max_marks=max_marks, created_by=teacher,
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 15))
        )
        a.save()
        assignments.append(a)

    # ── Submissions ────────────────────────────────────────
    submissions = []
    for assignment in assignments[:4]:
        course_enrollments = [e for e in enrollments if e.course_id == assignment.course_id]
        for enrollment in course_enrollments[:random.randint(2, min(5, len(course_enrollments)))]:
            sub = Submission(
                assignment_id=assignment,
                student_id=enrollment.student_id,
                text_content=f'My submission for {assignment.title}',
                original_filename=f'{assignment.title.lower().replace(" ", "_")}_submission.pdf',
                submitted_at=datetime.utcnow() - timedelta(hours=random.randint(1, 72)),
                status='pending'
            )
            sub.save()
            submissions.append(sub)

    # ── Marks ──────────────────────────────────────────────
    for sub in submissions[:len(submissions) // 2]:
        assignment = sub.assignment_id
        course = assignment.course_id
        m = Mark(
            student_id=sub.student_id,
            course_id=course,
            assignment_id=assignment,
            marks=round(random.uniform(50, assignment.max_marks), 1),
            max_marks=assignment.max_marks,
            feedback='Good work! Keep it up.',
            graded_by=course.teacher_id,
            graded_at=datetime.utcnow() - timedelta(hours=random.randint(1, 24))
        )
        m.save()
        sub.status = 'graded'
        sub.save()

    # ── Announcements ──────────────────────────────────────
    announcements_data = [
        ('New Material Uploaded', 'New study material has been uploaded for review.', courses[0], teachers[0]),
        ('Assignment 1 Released', 'Please check the assignments section for details.', courses[1], teachers[1]),
        ('Quiz Scheduled', 'SQL quiz will be held next week.', courses[2], teachers[2]),
        ('Office Hours Update', 'Office hours moved to Thursdays 2-4 PM.', courses[0], teachers[0]),
        ('Midterm Reminder', 'Midterm exam preparations should begin.', None, admin),
    ]
    for title, msg, course, creator in announcements_data:
        a = Announcement(
            title=title, message=msg, course_id=course, created_by=creator,
            created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 72))
        )
        a.save()

    print('Database seeded successfully!')
    print(f'  Admin:    admin@edumanage.com / admin123')
    print(f'  Teacher:  sarah@edumanage.com / teacher123')
    print(f'  Student:  john@student.com / student123')

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        seed_database()
