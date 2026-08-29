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
*   **Deployment:** Vercel (Serverless Python Functions)

---

## 🚀 Deploying to Vercel

Deploying EduManage to Vercel requires just a MongoDB Atlas database (free tier) and connecting your GitHub repository.

### Step 1: Set up MongoDB Atlas (Free)
1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/atlas).
2. Create a free shared cluster (M0).
3. Under **Security > Database Access**, create a user with read/write privileges and set a password.
4. Under **Security > Network Access**, click **Add IP Address** and select **Allow Access From Anywhere (`0.0.0.0/0`)** (required because Vercel functions use dynamic IP addresses).
5. Click **Connect > Drivers** and copy the connection string. Replace `<password>` with your database password:
   ```
   mongodb+srv://<username>:<password>@cluster0.xxx.mongodb.net/edumanage?retryWrites=true&w=majority
   ```

### Step 2: Deploy on Vercel
1. Push this repository to GitHub.
2. Go to [Vercel](https://vercel.com/) and click **Add New Project**, then import your repository.
3. In the project setup, expand **Environment Variables** and add:
   *   `MONGO_URI`: `your_mongodb_atlas_connection_string`
   *   `SECRET_KEY`: `any_random_secret_string_for_sessions`
4. Click **Deploy**.
5. Once deployed, the app will automatically seed default demo data on first launch!

---

## Local Installation & Setup

### Prerequisites
*   [Python 3.8+](https://www.python.org/downloads/)
*   [MongoDB](https://www.mongodb.com/try/download/community) (running locally on port `27017` or Atlas URI)

### Steps
1.  **Clone the repository**:
    ```bash
    git clone https://github.com/YourUsername/edu-manage.git
    cd edu-manage
    ```

2.  **Create and activate a Virtual Environment**:
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Application**:
    ```bash
    flask run
    ```
    The application will start on `http://127.0.0.1:5000/`.

---

## Demo Credentials

The database seeder automatically creates sample accounts on the first run:

*   **Admin:** `admin@edumanage.com` / `admin123`
*   **Teacher:** `sarah@edumanage.com` / `teacher123`
*   **Student:** `john@student.com` / `student123`

---

## Project Structure

```
edu-manage/
│
├── api/
│   └── index.py           # Vercel Serverless Function entry point
├── app.py                 # Application factory and initialization
├── config.py              # Configuration variables
├── models.py              # MongoEngine database schemas
├── forms.py               # WTForms for validation and CSRF
├── seed.py                # Database seeder for initial data
├── vercel.json            # Vercel routing and rewrite configuration
├── .env.example           # Environment variable template
├── routes/                # Blueprint routes for different roles
│   ├── auth.py            # Login/Logout routes
│   ├── admin.py           # Administrator routes
│   ├── teacher.py         # Teacher routes
│   └── student.py         # Student routes
├── static/                # Static assets (CSS, JS, uploads)
├── templates/             # Jinja2 HTML templates
└── requirements.txt       # Python dependencies
```

## License

This project is licensed under the MIT License.
