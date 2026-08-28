from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from psycopg2.extras import RealDictCursor
from backend.database import get_connection
import os

# =========================================================
# SCMS - Software Company Management System
# PostgreSQL / Supabase version
# =========================================================

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")


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


# =========================================================
# PAGES
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
    return send_from_directory(FRONTEND_DIR, "projects.html")


@app.route("/tasks")
def tasks_page():
    return send_from_directory(FRONTEND_DIR, "tasks.html")


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
        database_name = cursor.fetchone()[0]

        return jsonify({
            "success": True,
            "message": "PostgreSQL connected successfully",
            "database": database_name
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Database query failed",
            "error": str(e)
        }), 500

    finally:
        close_db(connection, cursor)


# =========================================================
# LOGIN
# =========================================================

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "Request data is missing"
        }), 400

    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

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
            SELECT id, name, email, password, role
            FROM users
            WHERE email = %s
            LIMIT 1
        """, (email,))

        user = cursor.fetchone()

        if user is None or password != user["password"]:
            return jsonify({
                "success": False,
                "message": "Invalid email or password"
            }), 401

        return jsonify({
            "success": True,
            "message": "Login successful",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"]
            }
        })

    except Exception as e:
        print("LOGIN ERROR:", e)
        return jsonify({
            "success": False,
            "message": "Login failed",
            "error": str(e)
        }), 500

    finally:
        close_db(connection, cursor)


# =========================================================
# DASHBOARD
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

        cursor.execute("SELECT COUNT(*) AS total FROM employees")
        employees = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM projects")
        projects = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM tasks")
        tasks = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM projects
            WHERE status = 'Active'
        """)
        active_projects = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT id, project_name, description, client_name,
                   start_date, deadline, status, created_at
            FROM projects
            ORDER BY id DESC
            LIMIT 5
        """)
        recent_projects = cursor.fetchall()

        for project in recent_projects:
            for key in ("start_date", "deadline", "created_at"):
                if project.get(key):
                    project[key] = str(project[key])

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
        print("DASHBOARD ERROR:", e)
        return jsonify({
            "success": False,
            "message": "Unable to load dashboard",
            "error": str(e)
        }), 500

    finally:
        close_db(connection, cursor)


# =========================================================
# EMPLOYEES - GET
# =========================================================

@app.route("/api/employees", methods=["GET"])
def get_employees():
    connection = get_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:
        # IMPORTANT:
        # psycopg2 does not support cursor(dictionary=True).
        # RealDictCursor is used instead.
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT
                e.id,
                e.user_id,
                u.name AS name,
                u.email AS email,
                e.employee_code,
                e.department,
                e.designation,
                e.phone,
                e.joining_date,
                e.status
            FROM employees e
            LEFT JOIN users u
                ON e.user_id = u.id
            ORDER BY e.id DESC
        """)

        employees = cursor.fetchall()

        for employee in employees:
            if employee.get("joining_date"):
                employee["joining_date"] = str(employee["joining_date"])

        return jsonify({
            "success": True,
            "employees": employees
        })

    except Exception as e:
        print("EMPLOYEES GET ERROR:", e)
        return jsonify({
            "success": False,
            "message": "Unable to fetch employees",
            "error": str(e)
        }), 500

    finally:
        close_db(connection, cursor)


# =========================================================
# EMPLOYEES - ADD
# =========================================================

@app.route("/api/employees", methods=["POST"])
def add_employee():
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    password = (data.get("password") or "").strip()
    employee_code = (data.get("employee_code") or "").strip()
    department = (data.get("department") or "").strip()
    designation = (data.get("designation") or "").strip()
    phone = (data.get("phone") or "").strip()
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

    if status not in ("Active", "Inactive"):
        status = "Active"

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
            "SELECT id FROM users WHERE email = %s LIMIT 1",
            (email,)
        )
        if cursor.fetchone():
            return jsonify({
                "success": False,
                "message": "Email already exists"
            }), 409

        cursor.execute(
            "SELECT id FROM employees WHERE employee_code = %s LIMIT 1",
            (employee_code,)
        )
        if cursor.fetchone():
            return jsonify({
                "success": False,
                "message": "Employee code already exists"
            }), 409

        cursor.execute("""
            INSERT INTO users (name, email, password, role)
            VALUES (%s, %s, %s, 'employee')
            RETURNING id
        """, (name, email, password))

        user_id = cursor.fetchone()["id"]

        cursor.execute("""
            INSERT INTO employees
            (
                user_id,
                employee_code,
                department,
                designation,
                phone,
                joining_date,
                status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            user_id,
            employee_code,
            department,
            designation,
            phone,
            joining_date,
            status
        ))

        employee_id = cursor.fetchone()["id"]

        connection.commit()

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
        connection.rollback()
        print("EMPLOYEE ADD ERROR:", e)
        return jsonify({
            "success": False,
            "message": "Unable to add employee",
            "error": str(e)
        }), 500

    finally:
        close_db(connection, cursor)


# =========================================================
# EMPLOYEES - UPDATE
# =========================================================

@app.route("/api/employees/<int:employee_id>", methods=["PUT"])
def update_employee(employee_id):
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    employee_code = (data.get("employee_code") or "").strip()
    department = (data.get("department") or "").strip()
    designation = (data.get("designation") or "").strip()
    phone = (data.get("phone") or "").strip()
    joining_date = data.get("joining_date") or None
    status = data.get("status", "Active")

    if not name or not email or not employee_code:
        return jsonify({
            "success": False,
            "message": "Name, email and employee code are required"
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
            SELECT user_id
            FROM employees
            WHERE id = %s
        """, (employee_id,))

        employee = cursor.fetchone()

        if not employee:
            return jsonify({
                "success": False,
                "message": "Employee not found"
            }), 404

        user_id = employee["user_id"]

        cursor.execute("""
            SELECT id
            FROM employees
            WHERE employee_code = %s
              AND id != %s
            LIMIT 1
        """, (employee_code, employee_id))

        if cursor.fetchone():
            return jsonify({
                "success": False,
                "message": "Employee code already exists"
            }), 409

        if user_id:
            cursor.execute("""
                SELECT id
                FROM users
                WHERE email = %s
                  AND id != %s
                LIMIT 1
            """, (email, user_id))

            if cursor.fetchone():
                return jsonify({
                    "success": False,
                    "message": "Email already exists"
                }), 409

            cursor.execute("""
                UPDATE users
                SET name = %s, email = %s
                WHERE id = %s
            """, (name, email, user_id))

        cursor.execute("""
            UPDATE employees
            SET
                employee_code = %s,
                department = %s,
                designation = %s,
                phone = %s,
                joining_date = %s,
                status = %s
            WHERE id = %s
        """, (
            employee_code,
            department,
            designation,
            phone,
            joining_date,
            status,
            employee_id
        ))

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Employee updated successfully"
        })

    except Exception as e:
        connection.rollback()
        print("EMPLOYEE UPDATE ERROR:", e)
        return jsonify({
            "success": False,
            "message": "Unable to update employee",
            "error": str(e)
        }), 500

    finally:
        close_db(connection, cursor)


# =========================================================
# EMPLOYEES - DELETE
# =========================================================

@app.route("/api/employees/<int:employee_id>", methods=["DELETE"])
def delete_employee(employee_id):
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
            SELECT user_id
            FROM employees
            WHERE id = %s
        """, (employee_id,))

        employee = cursor.fetchone()

        if not employee:
            return jsonify({
                "success": False,
                "message": "Employee not found"
            }), 404

        user_id = employee["user_id"]

        cursor.execute(
            "DELETE FROM employees WHERE id = %s",
            (employee_id,)
        )

        if user_id:
            cursor.execute("""
                DELETE FROM users
                WHERE id = %s
                  AND role = 'employee'
            """, (user_id,))

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Employee deleted successfully"
        })

    except Exception as e:
        connection.rollback()
        print("EMPLOYEE DELETE ERROR:", e)
        return jsonify({
            "success": False,
            "message": "Unable to delete employee",
            "error": str(e)
        }), 500

    finally:
        close_db(connection, cursor)


# =========================================================
# EMPLOYEE PROFILE BY USER
# =========================================================

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
                e.id,
                e.user_id,
                u.name,
                u.email,
                e.employee_code,
                e.department,
                e.designation,
                e.phone,
                e.joining_date,
                e.status
            FROM employees e
            LEFT JOIN users u ON e.user_id = u.id
            WHERE e.user_id = %s
            LIMIT 1
        """, (user_id,))

        employee = cursor.fetchone()

        if not employee:
            return jsonify({
                "success": False,
                "message": "Employee profile not found"
            }), 404

        if employee.get("joining_date"):
            employee["joining_date"] = str(employee["joining_date"])

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
        close_db(connection, cursor)


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

        cursor.execute("""
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
        """)

        projects = cursor.fetchall()

        for project in projects:
            for key in ("start_date", "deadline", "created_at"):
                if project.get(key):
                    project[key] = str(project[key])

        return jsonify({
            "success": True,
            "projects": projects
        })

    except Exception as e:
        print("PROJECTS GET ERROR:", e)
        return jsonify({
            "success": False,
            "message": "Unable to fetch projects",
            "error": str(e)
        }), 500

    finally:
        close_db(connection, cursor)


# =========================================================
# PROJECTS - ADD
# =========================================================

@app.route("/api/projects", methods=["POST"])
def add_project():
    data = request.get_json(silent=True) or {}
    project_name = (data.get("project_name") or "").strip()

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

        cursor.execute("""
            INSERT INTO projects
            (
                project_name,
                description,
                client_name,
                start_date,
                deadline,
                status
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            project_name,
            data.get("description"),
            data.get("client_name"),
            data.get("start_date") or None,
            data.get("deadline") or None,
            data.get("status", "Pending")
        ))

        project_id = cursor.fetchone()[0]
        connection.commit()

        return jsonify({
            "success": True,
            "message": "Project added successfully",
            "project_id": project_id
        }), 201

    except Exception as e:
        connection.rollback()
        print("PROJECT ADD ERROR:", e)
        return jsonify({
            "success": False,
            "message": "Unable to add project",
            "error": str(e)
        }), 500

    finally:
        close_db(connection, cursor)


# =========================================================
# PROJECTS - UPDATE
# =========================================================

@app.route("/api/projects/<int:project_id>", methods=["PUT"])
def update_project(project_id):
    data = request.get_json(silent=True) or {}

    connection = get_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE projects
            SET
                project_name = %s,
                description = %s,
                client_name = %s,
                start_date = %s,
                deadline = %s,
                status = %s
            WHERE id = %s
        """, (
            data.get("project_name"),
            data.get("description"),
            data.get("client_name"),
            data.get("start_date") or None,
            data.get("deadline") or None,
            data.get("status", "Pending"),
            project_id
        ))

        if cursor.rowcount == 0:
            return jsonify({
                "success": False,
                "message": "Project not found"
            }), 404

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Project updated successfully"
        })

    except Exception as e:
        connection.rollback()
        print("PROJECT UPDATE ERROR:", e)
        return jsonify({
            "success": False,
            "message": "Unable to update project",
            "error": str(e)
        }), 500

    finally:
        close_db(connection, cursor)


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

        cursor.execute("""
            SELECT COUNT(*)
            FROM tasks
            WHERE project_id = %s
        """, (project_id,))

        task_count = cursor.fetchone()[0]

        if task_count > 0:
            return jsonify({
                "success": False,
                "message": "This project has tasks. Delete or move the tasks first."
            }), 400

        cursor.execute(
            "DELETE FROM projects WHERE id = %s",
            (project_id,)
        )

        if cursor.rowcount == 0:
            return jsonify({
                "success": False,
                "message": "Project not found"
            }), 404

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Project deleted successfully"
        })

    except Exception as e:
        connection.rollback()
        print("PROJECT DELETE ERROR:", e)
        return jsonify({
            "success": False,
            "message": "Unable to delete project",
            "error": str(e)
        }), 500

    finally:
        close_db(connection, cursor)


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
                p.project_name,
                u.name AS employee_name
            FROM tasks t
            LEFT JOIN projects p
                ON t.project_id = p.id
            LEFT JOIN employees e
                ON t.employee_id = e.id
            LEFT JOIN users u
                ON e.user_id = u.id
            ORDER BY t.id DESC
        """)

        tasks = cursor.fetchall()

        for task in tasks:
            for key in ("deadline", "created_at"):
                if task.get(key):
                    task[key] = str(task[key])

        return jsonify({
            "success": True,
            "tasks": tasks
        })

    except Exception as e:
        print("TASKS GET ERROR:", e)
        return jsonify({
            "success": False,
            "message": "Unable to fetch tasks",
            "error": str(e)
        }), 500

    finally:
        close_db(connection, cursor)


# =========================================================
# TASKS - ADD
# =========================================================

@app.route("/api/tasks", methods=["POST"])
def add_task():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()

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

        cursor.execute("""
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
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data.get("project_id") or None,
            data.get("employee_id") or None,
            title,
            data.get("description"),
            data.get("priority", "Medium"),
            data.get("status", "Pending"),
            data.get("deadline") or None
        ))

        task_id = cursor.fetchone()[0]
        connection.commit()

        return jsonify({
            "success": True,
            "message": "Task added successfully",
            "task_id": task_id
        }), 201

    except Exception as e:
        connection.rollback()
        print("TASK ADD ERROR:", e)
        return jsonify({
            "success": False,
            "message": "Unable to add task",
            "error": str(e)
        }), 500

    finally:
        close_db(connection, cursor)


# =========================================================
# TASKS - UPDATE
# =========================================================

@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json(silent=True) or {}

    connection = get_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute("""
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
        """, (
            data.get("project_id") or None,
            data.get("employee_id") or None,
            data.get("title"),
            data.get("description"),
            data.get("priority", "Medium"),
            data.get("status", "Pending"),
            data.get("deadline") or None,
            task_id
        ))

        if cursor.rowcount == 0:
            return jsonify({
                "success": False,
                "message": "Task not found"
            }), 404

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Task updated successfully"
        })

    except Exception as e:
        connection.rollback()
        print("TASK UPDATE ERROR:", e)
        return jsonify({
            "success": False,
            "message": "Unable to update task",
            "error": str(e)
        }), 500

    finally:
        close_db(connection, cursor)


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
            "DELETE FROM tasks WHERE id = %s",
            (task_id,)
        )

        if cursor.rowcount == 0:
            return jsonify({
                "success": False,
                "message": "Task not found"
            }), 404

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Task deleted successfully"
        })

    except Exception as e:
        connection.rollback()
        print("TASK DELETE ERROR:", e)
        return jsonify({
            "success": False,
            "message": "Unable to delete task",
            "error": str(e)
        }), 500

    finally:
        close_db(connection, cursor)


# =========================================================
# USER PROFILE - UPDATE
# =========================================================

@app.route("/api/users/<int:user_id>", methods=["PUT"])
def update_user_profile(user_id):
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()

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

        cursor.execute("""
            UPDATE users
            SET name = %s,
                email = %s
            WHERE id = %s
        """, (name, email, user_id))

        if cursor.rowcount == 0:
            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404

        connection.commit()

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
        connection.rollback()
        print("PROFILE UPDATE ERROR:", e)
        return jsonify({
            "success": False,
            "message": "Unable to update profile",
            "error": str(e)
        }), 500

    finally:
        close_db(connection, cursor)


# =========================================================
# USER PASSWORD - UPDATE
# =========================================================

@app.route("/api/users/<int:user_id>/password", methods=["PUT"])
def update_user_password(user_id):
    data = request.get_json(silent=True) or {}

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

        cursor.execute("""
            SELECT password
            FROM users
            WHERE id = %s
        """, (user_id,))

        user = cursor.fetchone()

        if user is None:
            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404

        if current_password != user["password"]:
            return jsonify({
                "success": False,
                "message": "Current password is incorrect"
            }), 401

        cursor.execute("""
            UPDATE users
            SET password = %s
            WHERE id = %s
        """, (new_password, user_id))

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Password changed successfully"
        })

    except Exception as e:
        connection.rollback()
        print("PASSWORD UPDATE ERROR:", e)
        return jsonify({
            "success": False,
            "message": "Unable to change password",
            "error": str(e)
        }), 500

    finally:
        close_db(connection, cursor)


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":
    print("=" * 60)
    print("          MAYUR TECH - SCMS")
    print(" Software Company Management System")
    print("=" * 60)
    print("Server    : http://127.0.0.1:5000")
    print("Login     : http://127.0.0.1:5000/login")
    print("Dashboard : http://127.0.0.1:5000/dashboard")
    print("Employees : http://127.0.0.1:5000/employees")
    print("Projects  : http://127.0.0.1:5000/projects")
    print("Tasks     : http://127.0.0.1:5000/tasks")
    print("=" * 60)

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )
