-- Sample classroom rows. INSERT IGNORE avoids overwriting students' edits.
-- Re-running is convenient for lessons but will NOT reset balances or data.
USE MyUniversityDB;

INSERT IGNORE INTO Departments (DepartmentID, DepartmentName) VALUES
 ('CS', 'Computer Science'),
 ('MATH', 'Mathematics'),
 ('EE', 'Electrical Engineering');

INSERT IGNORE INTO Students
  (StudentID, FirstName, LastName, Major, EnrollmentDate, Email)
VALUES
 (2001, 'Alice', 'Morgan', 'Computer Science', '2025-08-20', 'alice.morgan@example.edu'),
 (2002, 'Ben', 'Rivera', 'Mathematics', '2025-08-20', 'ben.rivera@example.edu'),
 (2003, 'Chen', 'Park', 'Computer Science', '2026-01-15', 'chen.park@example.edu');

INSERT IGNORE INTO StudentAccounts (StudentID, Balance) VALUES
 (101, 200.00),
 (105, 100.00);
