# EduManage

EduManage is a modern, responsive, and robust Educational Management System built with Python (Flask) and MongoDB. It streamlines the educational workflow by providing distinct portals for Administrators, Teachers, and Students, allowing for seamless course management, assignment tracking, and grading.

## Features

*   **Role-Based Access Control:** Secure portals with customized dashboards for Admins, Teachers, and Students.
*   **Admin Dashboard:**
    *   Manage user accounts (Teachers and Students).
    *   Create and manage Courses.
    *   Enroll students in courses.
    *   Upload and manage course materials globally.
*   **Teacher Dashboard:**
    *   View assigned courses and enrolled students.
    *   Create and publish assignments with due dates.
    *   Review student submissions and assign grades/marks.
*   **Student Dashboard:**
    *   View enrolled courses and course progress.
    *   Access course materials and study resources.
    *   Submit assignments and view graded marks.
*   **Modern UI:** A clean, responsive, and beautiful user interface built with custom CSS (no heavy CSS frameworks required), featuring avatars, progress bars, and intuitive data tables.

## Tech Stack

*   **Backend:** Python 3, Flask
*   **Database:** MongoDB, MongoEngine (ODM)
*   **Frontend:** HTML5, Vanilla CSS, Jinja2 Templating
*   **Authentication:** Flask-Login
*   **Security:** Flask-WTF (CSRF Protection)

## Prerequisites

Before running the application, ensure you have the following installed:
*   [Python 3.8+](https://www.python.org/downloads/)
*   [MongoDB](https://www.mongodb.com/try/download/community) (running locally on default port `27017`)

## Installation & Setup

1.  **Clone the repository** (if you haven't already):
    ```bash
    git clone https://github.com/YourUsername/edu-manage.git
    cd edu-manage
    ```

2.  **Create a Virtual Environment:**
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ensure MongoDB is running:**
    Make sure your local MongoDB instance is active. The application will automatically connect to `mongodb://localhost:27017/edumanage`.

5.  **Run the Application:**
    ```bash
    flask run
    ```
    The application will start on `http://127.0.0.1:5000/`.

## Demo Credentials

The application includes a database seeder that automatically creates dummy data on the first run. You can use the "Demo Credentials" buttons on the login page or log in with the following:

*   **Admin:** `admin@edumanage.com` / `password123`
*   **Teacher:** `teacher1@edumanage.com` / `password123`
*   **Student:** `student1@edumanage.com` / `password123`

## Project Structure

```
edu-manage/
│
├── app.py                 # Application factory and initialization
├── config.py              # Configuration variables
├── models.py              # MongoEngine database schemas
├── forms.py               # WTForms for validation and CSRF
├── seed.py                # Database seeder for initial data
├── routes/                # Blueprint routes for different roles
│   ├── auth.py            # Login/Logout routes
│   ├── admin.py           # Administrator routes
│   ├── teacher.py         # Teacher routes
│   └── student.py         # Student routes
├── static/                # Static assets
│   ├── css/               # Custom stylesheets
│   └── js/                # Client-side JavaScript
├── templates/             # Jinja2 HTML templates
│   ├── admin/
│   ├── teacher/
│   ├── student/
│   ├── auth/
│   └── components/        # Reusable UI components (modals, pagination, sidebars)
└── requirements.txt       # Python dependencies
```

## License

This project is licensed under the MIT License.
