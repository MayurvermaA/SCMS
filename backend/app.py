from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from psycopg2.extras import RealDictCursor
from database import get_connection
import os

# =========================================================
# SCMS - Software Company Management System
# Company  : Mayur Tech
# Location : Dadiyapura, Jhansi
# =========================================================

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")


# =========================================================
# HELPER
# =========================================================

def close_db(connection, cursor=None):
    try:
        if cursor:
            cursor.close()
    except Exception:
        pass

    try:
        if connection:
            connection.close()
    except Exception:
        pass

@app.route("/forgot-password")
def forgot_password_page():
    return send_from_directory(
        FRONTEND_DIR,
        "forgot-password.html"
    )

@app.route("/employee-dashboard")
def employee_dashboard_page():
    return send_from_directory(
        FRONTEND_DIR,
        "employee-dashboard.html"
    )

@app.route("/employee-profile")
def employee_profile_page():
    return send_from_directory(
        FRONTEND_DIR,
        "employee-profile.html"
    )

@app.route("/api/employees/user/<int:user_id>")
def employee_by_user(user_id):

    connection = get_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:

        cursor = connection.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT
                id,
                name,
                user_id,
                employee_code,
                department,
                designation,
                phone,
                joining_date,
                status
            FROM employees
            WHERE user_id = %s
            LIMIT 1
        """, (user_id,))

        employee = cursor.fetchone()

        if not employee:
            return jsonify({
                "success": False,
                "message": "Employee profile not found"
            }), 404

        return jsonify({
            "success": True,
            "employee": employee
        })

    except Exception as e:

        print("EMPLOYEE PROFILE ERROR:", e)

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()

@app.route("/employee-projects")
def employee_projects_page():
    return send_from_directory(
        FRONTEND_DIR,
        "employee-projects.html"
    )


@app.route("/employee-tasks")
def employee_tasks_page():
    return send_from_directory(
        FRONTEND_DIR,
        "employee-tasks.html"
    )

@app.route("/api/employee/projects/<int:user_id>", methods=["GET"])
def employee_projects(user_id):

    connection = get_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:

        cursor = connection.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT
                p.id,
                p.project_name,
                p.description,
                p.client_name,
                p.start_date,
                p.deadline,
                p.status,
                p.created_at
            FROM projects p
            INNER JOIN tasks t
                ON t.project_id = p.id
            INNER JOIN employees e
                ON t.employee_id = e.id
            WHERE e.user_id = %s
            GROUP BY
                p.id,
                p.project_name,
                p.description,
                p.client_name,
                p.start_date,
                p.deadline,
                p.status,
                p.created_at
            ORDER BY p.id DESC
        """, (user_id,))

        projects = cursor.fetchall()

        for project in projects:

            if project.get("start_date"):
                project["start_date"] = str(
                    project["start_date"]
                )

            if project.get("deadline"):
                project["deadline"] = str(
                    project["deadline"]
                )

            if project.get("created_at"):
                project["created_at"] = str(
                    project["created_at"]
                )

        return jsonify({
            "success": True,
            "projects": projects
        })

    except Exception as e:

        print("EMPLOYEE PROJECT ERROR:", e)

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()        

# =========================================================
# BASIC PAGES
# =========================================================

@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "login.html")


@app.route("/login")
def login_page():
    return send_from_directory(FRONTEND_DIR, "login.html")


@app.route("/dashboard")
def dashboard_page():
    return send_from_directory(FRONTEND_DIR, "dashboard.html")


@app.route("/employees")
def employees_page():
    return send_from_directory(FRONTEND_DIR, "employees.html")

@app.route("/projects")
def projects_page():
    file_path = os.path.join(FRONTEND_DIR, "projects.html")

    if os.path.exists(file_path):
        return send_from_directory(FRONTEND_DIR, "projects.html")

    return "projects.html not found", 404


@app.route("/tasks")
def tasks_page():
    file_path = os.path.join(FRONTEND_DIR, "tasks.html")

    if os.path.exists(file_path):
        return send_from_directory(FRONTEND_DIR, "tasks.html")

    return "tasks.html not found", 404

@app.route("/profile")
def profile_page():
    return send_from_directory(FRONTEND_DIR, "profile.html")

@app.route("/settings")
def settings_page():
    file_path = os.path.join(FRONTEND_DIR, "settings.html")

    if os.path.exists(file_path):
        return send_from_directory(FRONTEND_DIR, "settings.html")

    return "settings.html not found", 404


@app.route("/about")
def about_page():
    file_path = os.path.join(FRONTEND_DIR, "about.html")

    if os.path.exists(file_path):
        return send_from_directory(FRONTEND_DIR, "about.html")

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>About - Mayur Tech</title>
        <style>
            body {
                margin: 0;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                background: #080b16;
                color: white;
                font-family: Arial;
            }

            .box {
                width: 500px;
                max-width: 90%;
                text-align: center;
                padding: 40px;
                background: #111628;
                border: 1px solid #20263a;
                border-radius: 18px;
            }

            a {
                color: #00d4ff;
                text-decoration: none;
            }
        </style>
    </head>

    <body>
        <div class="box">
            <h1>Mayur Tech</h1>
            <h2>Software Company Management System</h2>
            <p>📍 Dadiyapura, Jhansi</p>
            <br>
            <a href="/dashboard">← Back to Dashboard</a>
        </div>
    </body>
    </html>
    """


# =========================================================
# DATABASE TEST
# =========================================================

@app.route("/api/test-db")
def test_database():

    connection = get_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute("SELECT current_database()")

        result = cursor.fetchone()

        database_name = result[0]

        close_db(connection, cursor)

        return jsonify({
            "success": True,
            "message": "PostgreSQL connected successfully",
            "database": database_name
        })

    except Exception as e:

        close_db(connection, cursor)

        return jsonify({
            "success": False,
            "message": "Database query failed",
            "error": str(e)
        }), 500


# =========================================================
# LOGIN API
# =========================================================

# =========================================================
# DASHBOARD API
# =========================================================

@app.route("/api/dashboard")
def dashboard():

    connection = get_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:

        cursor = connection.cursor(cursor_factory=RealDictCursor)

        # Employees
        cursor.execute(
            "SELECT COUNT(*) AS total FROM employees"
        )
        employees = cursor.fetchone()["total"]

        # Projects
        cursor.execute(
            "SELECT COUNT(*) AS total FROM projects"
        )
        projects = cursor.fetchone()["total"]

        # Tasks
        cursor.execute(
            "SELECT COUNT(*) AS total FROM tasks"
        )
        tasks = cursor.fetchone()["total"]

        # Active projects
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM projects
            WHERE status = 'Active'
            """
        )
        active_projects = cursor.fetchone()["total"]

        # Recent projects
        cursor.execute(
            """
            SELECT
                id,
                project_name,
                description,
                client_name,
                start_date,
                deadline,
                status,
                created_at
            FROM projects
            ORDER BY id DESC
            LIMIT 5
            """
        )

        recent_projects = cursor.fetchall()

        for project in recent_projects:

            if project.get("start_date"):
                project["start_date"] = str(project["start_date"])

            if project.get("deadline"):
                project["deadline"] = str(project["deadline"])

            if project.get("created_at"):
                project["created_at"] = str(project["created_at"])

        close_db(connection, cursor)

        return jsonify({
            "success": True,

            "company": {
                "name": "Mayur Tech",
                "location": "Dadiyapura, Jhansi"
            },

            "stats": {
                "employees": employees,
                "projects": projects,
                "tasks": tasks,
                "active_projects": active_projects
            },

            "recent_projects": recent_projects
        })

    except Exception as e:

        close_db(connection, cursor)

        return jsonify({
            "success": False,
            "message": "Unable to load dashboard",
            "error": str(e)
        }), 500

# =========================================================
# CREATE LOGIN ACCOUNT FOR EXISTING EMPLOYEE
# =========================================================

@app.route(
    "/api/employees/<int:employee_id>/create-login",
    methods=["POST"]
)
def create_employee_login(employee_id):

    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email and password are required"
        }), 400

    connection = get_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:

        cursor = connection.cursor(cursor_factory=RealDictCursor)

        # Employee
        cursor.execute("""
            SELECT *
            FROM employees
            WHERE id = %s
        """, (employee_id,))

        employee = cursor.fetchone()

        if not employee:
            return jsonify({
                "success": False,
                "message": "Employee not found"
            }), 404

        # Already linked?
        if employee.get("user_id"):

            return jsonify({
                "success": False,
                "message": "Employee already has a login"
            }), 409

        # Email check
        cursor.execute("""
            SELECT id
            FROM users
            WHERE email = %s
            LIMIT 1
        """, (email,))

        existing_user = cursor.fetchone()

        if existing_user:

            return jsonify({
                "success": False,
                "message": "Email already exists"
            }), 409

        # Create user
        cursor.execute("""
            INSERT INTO users
                (name, email, password, role)
            VALUES
                (%s, %s, %s, 'employee')
            RETURNING id
        """, (
            employee["name"],
            email,
            password
        ))

        user_id = cursor.fetchone()["id"]

        # Automatically link employee
        cursor.execute("""
            UPDATE employees
            SET user_id = %s
            WHERE id = %s
        """, (
            user_id,
            employee_id
        ))

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Employee login created successfully",
            "user_id": user_id,
            "employee_id": employee_id
        })

    except Exception as e:

        connection.rollback()

        print("CREATE LOGIN ERROR:", e)

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()

# =========================================================
# LOGIN API - ADMIN + EMPLOYEE
# =========================================================

@app.route("/api/login", methods=["POST"])
def login_api():

    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:

        return jsonify({
            "success": False,
            "message": "Email and password are required"
        }), 400

    connection = get_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:

        cursor = connection.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT
                id,
                name,
                email,
                password,
                role
            FROM users
            WHERE email = %s
            LIMIT 1
        """, (email,))

        user = cursor.fetchone()

        if not user:

            return jsonify({
                "success": False,
                "message": "Invalid email or password"
            }), 401

        # Current SCMS project uses plain-text passwords.
        # Keep this matching your existing database.
        if user["password"] != password:

            return jsonify({
                "success": False,
                "message": "Invalid email or password"
            }), 401


        # -------------------------------------------------
        # ADMIN LOGIN
        # -------------------------------------------------

        if str(user["role"]).lower() == "admin":

            return jsonify({
                "success": True,
                "message": "Admin login successful",

                "user": {
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"],
                    "role": "admin"
                },

                "redirect": "/dashboard"
            })


        # -------------------------------------------------
        # EMPLOYEE LOGIN
        # -------------------------------------------------

        if str(user["role"]).lower() == "employee":

            cursor.execute("""
                SELECT
                    id,
                    name,
                    user_id,
                    employee_code,
                    department,
                    designation,
                    phone,
                    joining_date,
                    status
                FROM employees
                WHERE user_id = %s
                LIMIT 1
            """, (user["id"],))

            employee = cursor.fetchone()

            if not employee:

                return jsonify({
                    "success": False,
                    "message": "Employee profile not found"
                }), 404


            return jsonify({
                "success": True,
                "message": "Employee login successful",

                "user": {
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"],
                    "role": "employee",

                    "employee": employee
                },

                "redirect": "/employee-dashboard"
            })


        # -------------------------------------------------
        # UNKNOWN ROLE
        # -------------------------------------------------

        return jsonify({
            "success": False,
            "message": "Invalid user role"
        }), 403


    except Exception as e:

        print("LOGIN ERROR:", e)

        return jsonify({
            "success": False,
            "message": "Login failed",
            "error": str(e)
        }), 500


    finally:

        if cursor:
            cursor.close()

        connection.close()

# =========================================================
# EMPLOYEE MANAGEMENT APIs
# =========================================================

@app.route("/api/employees", methods=["GET"])
def get_employees():
    connection = get_connection()
    if connection is None:
        return jsonify({"success": False, "message": "Database connection failed"}), 500

    cursor = None
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT e.id, e.name, e.user_id, e.employee_code,
                   e.department, e.designation, e.phone,
                   e.joining_date, e.status, u.email
            FROM employees e
            LEFT JOIN users u ON e.user_id = u.id
            ORDER BY e.id DESC
        """)
        employees = cursor.fetchall()
        for employee in employees:
            if employee.get("joining_date"):
                employee["joining_date"] = str(employee["joining_date"])
        close_db(connection, cursor)
        return jsonify({"success": True, "employees": employees})
    except Exception as e:
        close_db(connection, cursor)
        return jsonify({"success": False, "message": "Unable to fetch employees", "error": str(e)}), 500


@app.route("/api/employees", methods=["POST"])
def add_employee():
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    password = str(data.get("password", "")).strip()
    employee_code = str(data.get("employee_code", "")).strip()
    department = str(data.get("department", "")).strip()
    designation = str(data.get("designation", "")).strip()
    phone = str(data.get("phone", "")).strip()
    joining_date = data.get("joining_date") or None
    status = data.get("status", "Active")

    if not name:
        return jsonify({"success": False, "message": "Employee name is required"}), 400
    if not email:
        return jsonify({"success": False, "message": "Employee email is required"}), 400
    if not password:
        return jsonify({"success": False, "message": "Employee password is required"}), 400
    if not employee_code:
        return jsonify({"success": False, "message": "Employee code is required"}), 400
    if status not in ["Active", "Inactive"]:
        status = "Active"

    connection = get_connection()
    if connection is None:
        return jsonify({"success": False, "message": "Database connection failed"}), 500

    cursor = None
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            close_db(connection, cursor)
            return jsonify({"success": False, "message": "Email already exists"}), 409

        cursor.execute("SELECT id FROM employees WHERE employee_code = %s", (employee_code,))
        if cursor.fetchone():
            close_db(connection, cursor)
            return jsonify({"success": False, "message": "Employee code already exists"}), 409

        cursor.execute("""
            INSERT INTO users (name, email, password, role)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (name, email, password, "employee"))
        user_id = cursor.fetchone()["id"]

        cursor.execute("""
            INSERT INTO employees
            (name, user_id, employee_code, department, designation,
             phone, joining_date, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            name, user_id, employee_code, department, designation,
            phone, joining_date, status
        ))
        employee_id = cursor.fetchone()["id"]

        connection.commit()
        close_db(connection, cursor)

        return jsonify({
            "success": True,
            "message": "Employee added successfully",
            "employee": {
                "id": employee_id,
                "user_id": user_id,
                "name": name,
                "email": email,
                "employee_code": employee_code,
                "department": department,
                "designation": designation,
                "phone": phone,
                "joining_date": str(joining_date) if joining_date else None,
                "status": status
            }
        }), 201

    except Exception as e:
        try:
            connection.rollback()
        except Exception:
            pass
        close_db(connection, cursor)
        return jsonify({
            "success": False,
            "message": "Unable to add employee",
            "error": str(e)
        }), 500


@app.route("/api/employees/<int:employee_id>", methods=["PUT"])
def update_employee(employee_id):
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    employee_code = str(data.get("employee_code", "")).strip()
    department = str(data.get("department", "")).strip()
    designation = str(data.get("designation", "")).strip()
    phone = str(data.get("phone", "")).strip()
    joining_date = data.get("joining_date") or None
    status = data.get("status", "Active")

    if not name or not email or not employee_code:
        return jsonify({
            "success": False,
            "message": "Name, email and employee code are required"
        }), 400

    connection = get_connection()
    if connection is None:
        return jsonify({"success": False, "message": "Database connection failed"}), 500

    cursor = None
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        cursor.execute(
            "SELECT user_id FROM employees WHERE id = %s",
            (employee_id,)
        )
        employee = cursor.fetchone()

        if not employee:
            close_db(connection, cursor)
            return jsonify({"success": False, "message": "Employee not found"}), 404

        user_id = employee.get("user_id")

        cursor.execute("""
            SELECT id FROM employees
            WHERE employee_code = %s AND id != %s
        """, (employee_code, employee_id))
        if cursor.fetchone():
            close_db(connection, cursor)
            return jsonify({"success": False, "message": "Employee code already exists"}), 409

        if user_id:
            cursor.execute("""
                SELECT id FROM users
                WHERE email = %s AND id != %s
            """, (email, user_id))
            if cursor.fetchone():
                close_db(connection, cursor)
                return jsonify({"success": False, "message": "Email already exists"}), 409

        cursor.execute("""
            UPDATE employees
            SET name=%s, employee_code=%s, department=%s,
                designation=%s, phone=%s, joining_date=%s, status=%s
            WHERE id=%s
        """, (
            name, employee_code, department, designation,
            phone, joining_date, status, employee_id
        ))

        if user_id:
            cursor.execute("""
                UPDATE users
                SET name=%s, email=%s
                WHERE id=%s
            """, (name, email, user_id))

        connection.commit()
        close_db(connection, cursor)

        return jsonify({
            "success": True,
            "message": "Employee updated successfully"
        })

    except Exception as e:
        try:
            connection.rollback()
        except Exception:
            pass
        close_db(connection, cursor)
        return jsonify({
            "success": False,
            "message": "Unable to update employee",
            "error": str(e)
        }), 500


@app.route("/api/employees/<int:employee_id>", methods=["DELETE"])
def delete_employee(employee_id):
    connection = get_connection()
    if connection is None:
        return jsonify({"success": False, "message": "Database connection failed"}), 500

    cursor = None
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        cursor.execute(
            "SELECT user_id FROM employees WHERE id = %s",
            (employee_id,)
        )
        employee = cursor.fetchone()

        if not employee:
            close_db(connection, cursor)
            return jsonify({"success": False, "message": "Employee not found"}), 404

        user_id = employee.get("user_id")

        cursor.execute(
            "DELETE FROM employees WHERE id = %s",
            (employee_id,)
        )

        if user_id:
            cursor.execute(
                "DELETE FROM users WHERE id = %s AND role = 'employee'",
                (user_id,)
            )

        connection.commit()
        close_db(connection, cursor)

        return jsonify({
            "success": True,
            "message": "Employee deleted successfully"
        })

    except Exception as e:
        try:
            connection.rollback()
        except Exception:
            pass
        close_db(connection, cursor)
        return jsonify({
            "success": False,
            "message": "Unable to delete employee",
            "error": str(e)
        }), 500


# =========================================================
# PROJECTS - GET
# =========================================================

@app.route("/api/projects", methods=["GET"])
def get_projects():

    connection = get_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:

        cursor = connection.cursor(cursor_factory=RealDictCursor)

        cursor.execute(
            """
            SELECT
                id,
                project_name,
                description,
                client_name,
                start_date,
                deadline,
                status,
                created_at
            FROM projects
            ORDER BY id DESC
            """
        )

        projects = cursor.fetchall()

        for project in projects:

            if project.get("start_date"):
                project["start_date"] = str(
                    project["start_date"]
                )

            if project.get("deadline"):
                project["deadline"] = str(
                    project["deadline"]
                )

            if project.get("created_at"):
                project["created_at"] = str(
                    project["created_at"]
                )

        close_db(connection, cursor)

        return jsonify({
            "success": True,
            "projects": projects
        })

    except Exception as e:

        close_db(connection, cursor)

        return jsonify({
            "success": False,
            "message": "Unable to fetch projects",
            "error": str(e)
        }), 500


# =========================================================
# PROJECTS - ADD
# =========================================================

@app.route("/api/projects", methods=["POST"])
def add_project():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "Project data is required"
        }), 400

    project_name = data.get("project_name")

    if not project_name:
        return jsonify({
            "success": False,
            "message": "Project name is required"
        }), 400

    connection = get_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO projects
            (
                project_name,
                description,
                client_name,
                start_date,
                deadline,
                status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            RETURNING id
            """,
            (
                project_name,
                data.get("description"),
                data.get("client_name"),
                data.get("start_date") or None,
                data.get("deadline") or None,
                data.get("status", "Pending")
            )
        )

        project_id = cursor.fetchone()["id"]
        connection.commit()

        close_db(connection, cursor)

        return jsonify({
            "success": True,
            "message": "Project added successfully",
            "project_id": project_id
        }), 201

    except Exception as e:

        try:
            connection.rollback()
        except Exception:
            pass

        close_db(connection, cursor)

        return jsonify({
            "success": False,
            "message": "Unable to add project",
            "error": str(e)
        }), 500


# =========================================================
# PROJECTS - UPDATE
# =========================================================

@app.route("/api/projects/<int:project_id>", methods=["PUT"])
def update_project(project_id):

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "Project data is required"
        }), 400

    connection = get_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE projects
            SET
                project_name = %s,
                description = %s,
                client_name = %s,
                start_date = %s,
                deadline = %s,
                status = %s
            WHERE id = %s
            """,
            (
                data.get("project_name"),
                data.get("description"),
                data.get("client_name"),
                data.get("start_date") or None,
                data.get("deadline") or None,
                data.get("status", "Pending"),
                project_id
            )
        )

        if cursor.rowcount == 0:

            close_db(connection, cursor)

            return jsonify({
                "success": False,
                "message": "Project not found"
            }), 404

        connection.commit()

        close_db(connection, cursor)

        return jsonify({
            "success": True,
            "message": "Project updated successfully"
        })

    except Exception as e:

        try:
            connection.rollback()
        except Exception:
            pass

        close_db(connection, cursor)

        return jsonify({
            "success": False,
            "message": "Unable to update project",
            "error": str(e)
        }), 500


# =========================================================
# PROJECTS - DELETE
# =========================================================

@app.route("/api/projects/<int:project_id>", methods=["DELETE"])
def delete_project(project_id):

    connection = get_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:

        cursor = connection.cursor()

        # Check tasks first
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM tasks
            WHERE project_id = %s
            """,
            (project_id,)
        )

        task_count = cursor.fetchone()[0]

        if task_count > 0:

            close_db(connection, cursor)

            return jsonify({
                "success": False,
                "message": "This project has tasks. Delete or move the tasks first."
            }), 400

        cursor.execute(
            """
            DELETE FROM projects
            WHERE id = %s
            """,
            (project_id,)
        )

        if cursor.rowcount == 0:

            close_db(connection, cursor)

            return jsonify({
                "success": False,
                "message": "Project not found"
            }), 404

        connection.commit()

        close_db(connection, cursor)

        return jsonify({
            "success": True,
            "message": "Project deleted successfully"
        })

    except Exception as e:

        try:
            connection.rollback()
        except Exception:
            pass

        close_db(connection, cursor)

        return jsonify({
            "success": False,
            "message": "Unable to delete project",
            "error": str(e)
        }), 500


# =========================================================
# TASKS - GET
# =========================================================

@app.route("/api/tasks", methods=["GET"])
def get_tasks():

    connection = get_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:

        cursor = connection.cursor(cursor_factory=RealDictCursor)

        cursor.execute(
            """
            SELECT
                t.id,
                t.project_id,
                t.employee_id,
                t.title,
                t.description,
                t.priority,
                t.status,
                t.deadline,
                t.created_at,

                p.project_name,

                e.name AS employee_name

            FROM tasks t

            LEFT JOIN projects p
                ON t.project_id = p.id

            LEFT JOIN employees e
                ON t.employee_id = e.id

            ORDER BY t.id DESC
            """
        )

        tasks = cursor.fetchall()

        for task in tasks:

            if task.get("deadline"):
                task["deadline"] = str(
                    task["deadline"]
                )

            if task.get("created_at"):
                task["created_at"] = str(
                    task["created_at"]
                )

        close_db(connection, cursor)

        return jsonify({
            "success": True,
            "tasks": tasks
        })

    except Exception as e:

        close_db(connection, cursor)

        return jsonify({
            "success": False,
            "message": "Unable to fetch tasks",
            "error": str(e)
        }), 500


# =========================================================
# TASKS - ADD
# =========================================================

@app.route("/api/tasks", methods=["POST"])
def add_task():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "Task data is required"
        }), 400

    title = data.get("title")

    if not title:
        return jsonify({
            "success": False,
            "message": "Task title is required"
        }), 400

    connection = get_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO tasks
            (
                project_id,
                employee_id,
                title,
                description,
                priority,
                status,
                deadline
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            RETURNING id
            """,
            (
                data.get("project_id") or None,
                data.get("employee_id") or None,
                title,
                data.get("description"),
                data.get("priority", "Medium"),
                data.get("status", "Pending"),
                data.get("deadline") or None
            )
        )

        task_id = cursor.fetchone()["id"]
        connection.commit()

        close_db(connection, cursor)

        return jsonify({
            "success": True,
            "message": "Task added successfully",
            "task_id": task_id
        }), 201

    except Exception as e:

        try:
            connection.rollback()
        except Exception:
            pass

        close_db(connection, cursor)

        return jsonify({
            "success": False,
            "message": "Unable to add task",
            "error": str(e)
        }), 500


# =========================================================
# TASKS - UPDATE
# =========================================================

@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "Task data is required"
        }), 400

    connection = get_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE tasks
            SET
                project_id = %s,
                employee_id = %s,
                title = %s,
                description = %s,
                priority = %s,
                status = %s,
                deadline = %s
            WHERE id = %s
            """,
            (
                data.get("project_id") or None,
                data.get("employee_id") or None,
                data.get("title"),
                data.get("description"),
                data.get("priority", "Medium"),
                data.get("status", "Pending"),
                data.get("deadline") or None,
                task_id
            )
        )

        if cursor.rowcount == 0:

            close_db(connection, cursor)

            return jsonify({
                "success": False,
                "message": "Task not found"
            }), 404

        connection.commit()

        close_db(connection, cursor)

        return jsonify({
            "success": True,
            "message": "Task updated successfully"
        })

    except Exception as e:

        try:
            connection.rollback()
        except Exception:
            pass

        close_db(connection, cursor)

        return jsonify({
            "success": False,
            "message": "Unable to update task",
            "error": str(e)
        }), 500


# =========================================================
# TASKS - DELETE
# =========================================================

@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):

    connection = get_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM tasks
            WHERE id = %s
            """,
            (task_id,)
        )

        if cursor.rowcount == 0:

            close_db(connection, cursor)

            return jsonify({
                "success": False,
                "message": "Task not found"
            }), 404

        connection.commit()

        close_db(connection, cursor)

        return jsonify({
            "success": True,
            "message": "Task deleted successfully"
        })

    except Exception as e:

        try:
            connection.rollback()
        except Exception:
            pass

        close_db(connection, cursor)

        return jsonify({
            "success": False,
            "message": "Unable to delete task",
            "error": str(e)
        }), 500

# =========================================================
# EMPLOYEE - MY TASKS
# =========================================================

@app.route("/api/employee/tasks/<int:user_id>", methods=["GET"])
def employee_tasks(user_id):

    connection = get_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:

        cursor = connection.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT
                t.id,
                t.project_id,
                t.employee_id,
                t.title,
                t.description,
                t.priority,
                t.status,
                t.deadline,
                t.created_at,
                p.project_name
            FROM tasks t
            LEFT JOIN projects p
                ON t.project_id = p.id
            INNER JOIN employees e
                ON t.employee_id = e.id
            WHERE e.user_id = %s
            ORDER BY t.id DESC
        """, (user_id,))

        tasks = cursor.fetchall()

        for task in tasks:

            if task.get("deadline"):
                task["deadline"] = str(
                    task["deadline"]
                )

            if task.get("created_at"):
                task["created_at"] = str(
                    task["created_at"]
                )

        return jsonify({
            "success": True,
            "tasks": tasks
        })

    except Exception as e:

        print("EMPLOYEE TASK ERROR:", e)

        return jsonify({
            "success": False,
            "message": "Unable to fetch employee tasks",
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# USER PROFILE - UPDATE
# =========================================================

@app.route("/api/users/<int:user_id>", methods=["PUT"])
def update_user_profile(user_id):

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "Profile data is required"
        }), 400

    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({
            "success": False,
            "message": "Name and email are required"
        }), 400

    connection = get_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE users
            SET name = %s,
                email = %s
            WHERE id = %s
            """,
            (name, email, user_id)
        )

        if cursor.rowcount == 0:

            close_db(connection, cursor)

            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404

        connection.commit()

        close_db(connection, cursor)

        return jsonify({
            "success": True,
            "message": "Profile updated successfully",
            "user": {
                "id": user_id,
                "name": name,
                "email": email
            }
        })

    except Exception as e:

        try:
            connection.rollback()
        except Exception:
            pass

        close_db(connection, cursor)

        return jsonify({
            "success": False,
            "message": "Unable to update profile",
            "error": str(e)
        }), 500


# =========================================================
# USER PASSWORD - UPDATE
# =========================================================

@app.route("/api/users/<int:user_id>/password", methods=["PUT"])
def update_user_password(user_id):

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "Password data is required"
        }), 400

    current_password = data.get("current_password")
    new_password = data.get("new_password")

    if not current_password or not new_password:

        return jsonify({
            "success": False,
            "message": "Current and new password are required"
        }), 400

    connection = get_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:

        cursor = connection.cursor(cursor_factory=RealDictCursor)

        cursor.execute(
            """
            SELECT password
            FROM users
            WHERE id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if user is None:

            close_db(connection, cursor)

            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404

        if current_password != user["password"]:

            close_db(connection, cursor)

            return jsonify({
                "success": False,
                "message": "Current password is incorrect"
            }), 401

        cursor.execute(
            """
            UPDATE users
            SET password = %s
            WHERE id = %s
            """,
            (new_password, user_id)
        )

        connection.commit()

        close_db(connection, cursor)

        return jsonify({
            "success": True,
            "message": "Password changed successfully"
        })

    except Exception as e:

        try:
            connection.rollback()
        except Exception:
            pass

        close_db(connection, cursor)

        return jsonify({
            "success": False,
            "message": "Unable to change password",
            "error": str(e)
        }), 500

# =========================================================
# ATTENDANCE APIs
# =========================================================

@app.route(
    "/api/attendance/<int:user_id>/today",
    methods=["GET"]
)
def get_today_attendance(user_id):

    connection = get_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:

        cursor = connection.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute("""
            SELECT
                id,
                user_id,
                attendance_date,
                check_in,
                check_out,
                status,
                working_hours,
                created_at
            FROM attendance
            WHERE user_id = %s
            AND attendance_date = CURRENT_DATE
            LIMIT 1
        """, (user_id,))

        attendance = cursor.fetchone()

        if attendance:

            if attendance.get("attendance_date"):
                attendance["attendance_date"] = str(
                    attendance["attendance_date"]
                )

            if attendance.get("check_in"):
                attendance["check_in"] = str(
                    attendance["check_in"]
                )

            if attendance.get("check_out"):
                attendance["check_out"] = str(
                    attendance["check_out"]
                )

            if attendance.get("created_at"):
                attendance["created_at"] = str(
                    attendance["created_at"]
                )

            attendance["working_hours"] = float(
                attendance.get("working_hours") or 0
            )

        return jsonify({
            "success": True,
            "attendance": attendance
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Unable to load attendance",
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# CHECK IN
# =========================================================

@app.route(
    "/api/attendance/<int:user_id>/check-in",
    methods=["POST"]
)
def attendance_check_in(user_id):

    connection = get_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:

        cursor = connection.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute("""
            SELECT
                id,
                check_in,
                check_out,
                status
            FROM attendance
            WHERE user_id = %s
            AND attendance_date = CURRENT_DATE
            LIMIT 1
        """, (user_id,))

        existing = cursor.fetchone()

        # Already checked in
        if existing and existing.get("check_in"):

            return jsonify({
                "success": False,
                "message": "You have already checked in today",
                "attendance": existing
            }), 400

        # Existing record without check-in
        if existing:

            cursor.execute("""
                UPDATE attendance
                SET
                    check_in = NOW(),
                    status = 'Present'
                WHERE id = %s
            """, (existing["id"],))

        else:

            cursor.execute("""
                INSERT INTO attendance
                (
                    user_id,
                    attendance_date,
                    check_in,
                    status,
                    working_hours
                )
                VALUES
                (
                    %s,
                    CURRENT_DATE,
                    NOW(),
                    'Present',
                    0
                )
            """, (user_id,))

        connection.commit()

        cursor.execute("""
            SELECT
                id,
                user_id,
                attendance_date,
                check_in,
                check_out,
                status,
                working_hours,
                created_at
            FROM attendance
            WHERE user_id = %s
            AND attendance_date = CURRENT_DATE
            LIMIT 1
        """, (user_id,))

        attendance = cursor.fetchone()

        if attendance:

            if attendance.get("attendance_date"):
                attendance["attendance_date"] = str(
                    attendance["attendance_date"]
                )

            if attendance.get("check_in"):
                attendance["check_in"] = str(
                    attendance["check_in"]
                )

            if attendance.get("check_out"):
                attendance["check_out"] = str(
                    attendance["check_out"]
                )

            if attendance.get("created_at"):
                attendance["created_at"] = str(
                    attendance["created_at"]
                )

            attendance["working_hours"] = float(
                attendance.get("working_hours") or 0
            )

        return jsonify({
            "success": True,
            "message": "Check-in successful",
            "attendance": attendance
        })

    except Exception as e:

        connection.rollback()

        return jsonify({
            "success": False,
            "message": "Check-in failed",
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# CHECK OUT
# =========================================================

@app.route(
    "/api/attendance/<int:user_id>/check-out",
    methods=["POST"]
)
def attendance_check_out(user_id):

    connection = get_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:

        cursor = connection.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute("""
            SELECT
                id,
                check_in,
                check_out,
                status
            FROM attendance
            WHERE user_id = %s
            AND attendance_date = CURRENT_DATE
            LIMIT 1
        """, (user_id,))

        attendance = cursor.fetchone()

        if not attendance:
            return jsonify({
                "success": False,
                "message": "Please check in first"
            }), 400

        if not attendance.get("check_in"):
            return jsonify({
                "success": False,
                "message": "Please check in first"
            }), 400

        if attendance.get("check_out"):
            return jsonify({
                "success": False,
                "message": "You have already checked out today"
            }), 400

        cursor.execute("""
            UPDATE attendance
            SET
                check_out = NOW(),
                working_hours =
                    ROUND(
                        (EXTRACT(EPOCH FROM (NOW() - check_in)) / 3600.0)::numeric,
                        2
                    )
            WHERE id = %s
        """, (attendance["id"],))

        connection.commit()

        cursor.execute("""
            SELECT
                id,
                user_id,
                attendance_date,
                check_in,
                check_out,
                status,
                working_hours,
                created_at
            FROM attendance
            WHERE id = %s
            LIMIT 1
        """, (attendance["id"],))

        updated = cursor.fetchone()

        if updated:

            if updated.get("attendance_date"):
                updated["attendance_date"] = str(
                    updated["attendance_date"]
                )

            if updated.get("check_in"):
                updated["check_in"] = str(
                    updated["check_in"]
                )

            if updated.get("check_out"):
                updated["check_out"] = str(
                    updated["check_out"]
                )

            if updated.get("created_at"):
                updated["created_at"] = str(
                    updated["created_at"]
                )

            updated["working_hours"] = float(
                updated.get("working_hours") or 0
            )

        return jsonify({
            "success": True,
            "message": "Check-out successful",
            "attendance": updated
        })

    except Exception as e:

        connection.rollback()

        return jsonify({
            "success": False,
            "message": "Check-out failed",
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()
# =========================================================
# EMPLOYEE ATTENDANCE PAGE
# =========================================================

@app.route("/employee-attendance")
def employee_attendance_page():
    file_path = os.path.join(
        FRONTEND_DIR,
        "employee-attendance.html"
    )

    if os.path.exists(file_path):
        return send_from_directory(
            FRONTEND_DIR,
            "employee-attendance.html"
        )

    return "employee-attendance.html not found", 404

# =========================================================
# EMPLOYEE ATTENDANCE HISTORY
# =========================================================

@app.route(
    "/api/attendance/<int:user_id>/history",
    methods=["GET"]
)
def get_attendance_history(user_id):

    connection = get_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:

        cursor = connection.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT
                id,
                user_id,
                attendance_date,
                check_in,
                check_out,
                status,
                working_hours,
                created_at
            FROM attendance
            WHERE user_id = %s
            ORDER BY attendance_date DESC
            LIMIT 30
        """, (user_id,))

        history = cursor.fetchall()

        for row in history:

            if row.get("attendance_date"):
                row["attendance_date"] = str(
                    row["attendance_date"]
                )

            if row.get("check_in"):
                row["check_in"] = str(
                    row["check_in"]
                )

            if row.get("check_out"):
                row["check_out"] = str(
                    row["check_out"]
                )

            if row.get("created_at"):
                row["created_at"] = str(
                    row["created_at"]
                )

            row["working_hours"] = float(
                row.get("working_hours") or 0
            )

        return jsonify({
            "success": True,
            "history": history
        })

    except Exception as e:

        print("ATTENDANCE HISTORY ERROR:", e)

        return jsonify({
            "success": False,
            "message": "Unable to load attendance history",
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()

# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":
    print()
    print("=" * 60)
    print("          MAYUR TECH - SCMS")
    print(" Software Company Management System")
    print("=" * 60)
    print("Company   : Mayur Tech")
    print("Location  : Dadiyapura, Jhansi")
    print("Server    : http://127.0.0.1:5000")
    print("Login     : http://127.0.0.1:5000/login")
    print("Dashboard : http://127.0.0.1:5000/dashboard")
    print("Employees : http://127.0.0.1:5000/employees")
    print("Projects  : http://127.0.0.1:5000/projects")
    print("Tasks     : http://127.0.0.1:5000/tasks")
    print("About     : http://127.0.0.1:5000/about")
    print("Settings  : http://127.0.0.1:5000/settings")
    print("=" * 60)
    print()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
