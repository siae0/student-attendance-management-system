USE attendance_db;

-- Insert Faculty Records
INSERT INTO Faculty (faculty_name, subject, email)
VALUES
('Anita Sharma', 'DBMS', 'anita@example.com'),
('Rahul Verma', 'Python', 'rahul@example.com');

-- Insert Student Records
INSERT INTO Students (roll_no, student_name, department, semester)
VALUES
('101', 'Rahul', 'CSE', 3),
('102', 'Priya', 'CSE', 3),
('103', 'Aman', 'CSE', 3),
('104', 'Sneha', 'CSE', 3),
('105', 'Karan', 'CSE', 3);

-- Insert Attendance Records
INSERT INTO Attendance
(student_id, faculty_id, attendance_date, status)
VALUES
(1, 1, '2026-11-12', 'Present'),
(2, 1, '2026-11-12', 'Present'),
(3, 1, '2026-11-12', 'Absent'),
(4, 1, '2026-11-12', 'Present'),
(5, 1, '2026-11-12', 'Absent');
