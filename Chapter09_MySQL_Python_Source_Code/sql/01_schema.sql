-- Chapter 9 teaching schema. No DROP commands: reruns preserve existing data.
-- MySQL 8.0+ / InnoDB. Change USE if your DB_NAME differs from MyUniversityDB.
USE MyUniversityDB;

CREATE TABLE IF NOT EXISTS Departments (
    DepartmentID VARCHAR(10) PRIMARY KEY,
    DepartmentName VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Students (
    StudentID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Major VARCHAR(100) NULL,
    EnrollmentDate DATE NOT NULL,
    Email VARCHAR(255) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- Separate, simplified accounts for the atomic-transfer exercise (§9.5.2).
-- These IDs need not be in Students. This is NOT a real banking schema.
CREATE TABLE IF NOT EXISTS StudentAccounts (
    StudentID INT PRIMARY KEY,
    Balance DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    CONSTRAINT chk_studentaccounts_nonnegative CHECK (Balance >= 0)
) ENGINE=InnoDB;

-- Optional extension for the atomic student + advisor project exercise.
CREATE TABLE IF NOT EXISTS AdvisorAssignments (
    StudentID INT PRIMARY KEY,
    AdvisorName VARCHAR(100) NOT NULL,
    CONSTRAINT fk_advisor_student FOREIGN KEY (StudentID)
        REFERENCES Students(StudentID) ON DELETE CASCADE
) ENGINE=InnoDB;
