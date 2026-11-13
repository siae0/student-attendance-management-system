
from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_connection

app = Flask(__name__)
app.secret_key = "attendance_project_secret_key"


# Dashboard
@app.route("/")
def dashboard():
    connection = get_connection()

    if not connection:
        return "Database connection failed!"

    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM Students")
    total_students = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM Faculty")
    total_faculty = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM Attendance
        WHERE attendance_date = CURDATE()
        AND status = 'Present'
    """)
    present_today = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM Attendance
        WHERE attendance_date = CURDATE()
    """)
    total_today = cursor.fetchone()["total"]

    percentage = (
        round((present_today / total_today) * 100, 2)
        if total_today > 0 else 0
    )

    cursor.close()
    connection.close()

    return render_template(
        "dashboard.html",
        total_students=total_students,
        total_faculty=total_faculty,
        present_today=present_today,
        percentage=percentage
    )


# View Students
@app.route("/students")
def students():
    connection = get_connection()

    if not connection:
        return "Database connection failed!"

    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Students ORDER BY student_id")
    student_list = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("students.html", students=student_list)


# Add Student
@app.route("/students/add", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":
        roll_no = request.form["roll_no"]
        student_name = request.form["student_name"]
        department = request.form["department"]
        semester = request.form["semester"]

        connection = get_connection()

        if not connection:
            return "Database connection failed!"

        cursor = connection.cursor()

        try:
            query = """
                INSERT INTO Students
                (roll_no, student_name, department, semester)
                VALUES (%s, %s, %s, %s)
            """

            cursor.execute(
                query,
                (roll_no, student_name, department, semester)
            )

            connection.commit()
            flash("Student added successfully!", "success")

        except Exception as error:
            connection.rollback()
            flash("Error adding student: " + str(error), "danger")

        finally:
            cursor.close()
            connection.close()

        return redirect(url_for("students"))

    return render_template("add_student.html")


# Delete Student
@app.route("/students/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    connection = get_connection()

    if not connection:
        return "Database connection failed!"

    cursor = connection.cursor()

    try:
        cursor.execute(
            "DELETE FROM Students WHERE student_id = %s",
            (student_id,)
        )
        connection.commit()
        flash("Student deleted successfully!", "success")

    except Exception as error:
        connection.rollback()
        flash("Could not delete student: " + str(error), "danger")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("students"))

# ==========================================
# FACULTY MANAGEMENT
# ==========================================

@app.route("/faculty")
def faculty():
    connection = get_connection()

    if not connection:
        return "Database connection failed!"

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Faculty ORDER BY faculty_id")
    faculty_list = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("faculty.html", faculty=faculty_list)


@app.route("/faculty/add", methods=["GET", "POST"])
def add_faculty():

    if request.method == "POST":
        name = request.form["faculty_name"]
        subject = request.form["subject"]
        email = request.form.get("email") or None

        connection = get_connection()
        if not connection:
            return "Database connection failed!"

        cursor = connection.cursor()

        try:
            cursor.execute("""
                INSERT INTO Faculty (faculty_name, subject, email)
                VALUES (%s, %s, %s)
            """, (name, subject, email))

            connection.commit()
            flash("Faculty added successfully!", "success")

        except Exception as error:
            connection.rollback()
            flash("Error: " + str(error), "danger")

        finally:
            cursor.close()
            connection.close()

        return redirect(url_for("faculty"))

    return render_template("add_faculty.html")


@app.route("/faculty/delete/<int:faculty_id>", methods=["POST"])
def delete_faculty(faculty_id):

    connection = get_connection()
    if not connection:
        return "Database connection failed!"

    cursor = connection.cursor()

    try:
        cursor.execute(
            "DELETE FROM Faculty WHERE faculty_id = %s",
            (faculty_id,)
        )
        connection.commit()
        flash("Faculty deleted successfully!", "success")

    except Exception as error:
        connection.rollback()
        flash("Cannot delete faculty: " + str(error), "danger")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("faculty"))


# ==========================================
# ATTENDANCE MANAGEMENT
# ==========================================

@app.route("/attendance", methods=["GET", "POST"])
def attendance():

    connection = get_connection()
    if not connection:
        return "Database connection failed!"

    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":
        student_id = request.form["student_id"]
        faculty_id = request.form["faculty_id"]
        attendance_date = request.form["attendance_date"]
        status = request.form["status"]

        try:
            # Prevent duplicate attendance for the same student and date
            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM Attendance
                WHERE student_id = %s
                AND attendance_date = %s
            """, (student_id, attendance_date))

            if cursor.fetchone()["total"] > 0:
                flash("Attendance already marked for this student on this date!", "warning")

            else:
                cursor.execute("""
                    INSERT INTO Attendance
                    (student_id, faculty_id, attendance_date, status)
                    VALUES (%s, %s, %s, %s)
                """, (student_id, faculty_id, attendance_date, status))

                connection.commit()
                flash("Attendance marked successfully!", "success")

        except Exception as error:
            connection.rollback()
            flash("Error: " + str(error), "danger")

        finally:
            cursor.close()
            connection.close()

        return redirect(url_for("attendance"))

    cursor.execute("SELECT * FROM Students ORDER BY student_name")
    student_list = cursor.fetchall()

    cursor.execute("SELECT * FROM Faculty ORDER BY faculty_name")
    faculty_list = cursor.fetchall()

    cursor.execute("""
        SELECT A.*, S.student_name, S.roll_no, F.faculty_name
        FROM Attendance A
        JOIN Students S ON A.student_id = S.student_id
        JOIN Faculty F ON A.faculty_id = F.faculty_id
        ORDER BY A.attendance_date DESC, A.attendance_id DESC
    """)

    attendance_list = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "attendance.html",
        students=student_list,
        faculty=faculty_list,
        records=attendance_list
    )


# ==========================================
# ATTENDANCE REPORTS
# ==========================================

@app.route("/reports")
def reports():

    connection = get_connection()
    if not connection:
        return "Database connection failed!"

    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            S.student_id,
            S.roll_no,
            S.student_name,
            S.department,
            COUNT(A.attendance_id) AS total_classes,
            SUM(CASE WHEN A.status = 'Present' THEN 1 ELSE 0 END) AS present,
            SUM(CASE WHEN A.status = 'Absent' THEN 1 ELSE 0 END) AS absent,
            ROUND(
                100.0 * SUM(CASE WHEN A.status = 'Present' THEN 1 ELSE 0 END)
                / NULLIF(COUNT(A.attendance_id), 0),
                2
            ) AS percentage
        FROM Students S
        LEFT JOIN Attendance A
        ON S.student_id = A.student_id
        GROUP BY
            S.student_id, S.roll_no, S.student_name, S.department
        ORDER BY S.student_name
    """)

    report_list = cursor.fetchall()

    cursor.execute("""
        SELECT
            COUNT(*) AS total_records,
            SUM(status = 'Present') AS total_present,
            SUM(status = 'Absent') AS total_absent
        FROM Attendance
    """)

    summary = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template(
        "reports.html",
        reports=report_list,
        summary=summary
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
 