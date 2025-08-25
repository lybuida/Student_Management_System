#models.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, DateTime, Table
from sqlalchemy.orm import relationship, backref
from StudentManagementApp import db
from flask_login import UserMixin
from enum import Enum as enum
from sqlalchemy.ext.hybrid import hybrid_property
import hashlib

# ========== ENUMS ==========
class Role(enum):
    ADMIN = 1
    STAFF = 2
    TEACHER = 3

class Gender(enum):
    MALE = "Nam"
    FEMALE = "Nữ"

class Grade(enum):
    GRADE_10 = "10"
    GRADE_11 = "11"
    GRADE_12 = "12"

class ScoreType(enum):
    FIFTEEN_MIN = "Điểm 15 phút"
    ONE_PERIOD = "Điểm 1 tiết"
    FINAL = "Điểm thi"

# ========== USER & ROLE ==========
class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(512), nullable=False)
    role = Column(Enum(Role), nullable=False)

    # active = Column(Boolean, default=True)

    def __str__(self):
        return self.name

    def get_id(self):
        return str(self.id)

class Admin(db.Model):
    __tablename__ = 'admin'
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)

    user = relationship('User', backref='admin_profile')

class Staff(db.Model):
    __tablename__ = 'staff'
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)

    user = relationship('User', backref='staff_profile')

# ========== CORE MODELS ==========
class GradeLevel(db.Model):
    __tablename__ = 'gradelevel'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Enum(Grade), nullable=False)

class Classroom(db.Model):
    __tablename__ = 'classroom'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    gradelevel_id = Column(Integer, ForeignKey('gradelevel.id'), nullable=False)
    academic_year_id = Column(Integer, ForeignKey('academic_year.id'), nullable=False)
    homeroom_teacher_id = Column(Integer, ForeignKey('teacher.id'), unique=True)

    gradelevel = relationship('GradeLevel', backref='classrooms')
    students = relationship('Student', backref='classroom', lazy=True)
    teachers = relationship('Teacher', secondary='teacher_classroom', back_populates='classrooms')
    academic_year = relationship('AcademicYear', back_populates='classrooms')

    @property
    def current_student(self):
        return len(self.students)  # Tự động tính số học sinh trong lớp

class Teacher(db.Model):
    __tablename__ = 'teacher'
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)

    subject_id = Column(Integer, ForeignKey('subject.id'), nullable=False)

    subject = relationship('Subject', backref='teachers')
    user = relationship('User', backref='teacher_profile')
    classrooms = relationship('Classroom', secondary='teacher_classroom', back_populates='teachers')
    homeroom_class = relationship('Classroom', uselist=False, backref='homeroom_teacher', foreign_keys='Classroom.homeroom_teacher_id')

class Student(db.Model):
    __tablename__ = 'student'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    birth_date = Column(DateTime, nullable=False)
    address = Column(String(255))
    phone = Column(String(20))
    email = Column(String(50))

    classroom_id = Column(Integer, ForeignKey('classroom.id'), nullable=True)
    grade_id = Column(Integer, ForeignKey('gradelevel.id'), nullable=False)

    gradelevel = relationship("GradeLevel", backref="students", lazy = True)
    score_sheets = relationship('ScoreSheet', backref='student', lazy=True)
    draft_scores = relationship('DraftScore', backref='student', lazy=True)

class Semester(db.Model):
    __tablename__ = 'semester'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)

    score_sheets = relationship('ScoreSheet', backref='semester', lazy=True)
    draft_scores = relationship('DraftScore', backref='semester', lazy=True)


class AcademicYear(db.Model):
    __tablename__ = 'academic_year'

    id = Column(Integer, primary_key=True)
    start_year = Column(Integer, nullable=False)
    end_year = Column(Integer, nullable=False)
    is_active = Column(db.Boolean, default=True)


    classrooms = relationship('Classroom', back_populates='academic_year', lazy=True)
    scoresheets = relationship('ScoreSheet', backref='academic_year_obj', lazy=True)
    draft_scores = relationship('DraftScore', backref='academic_year_obj', lazy=True)

    @hybrid_property
    def name(self):
        return f"{self.start_year}–{self.end_year}"  #Tự sinh name khi gọi


class Subject(db.Model):
    __tablename__ = 'subject'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    gradelevel_id = Column(Integer, ForeignKey('gradelevel.id'))

    score15P_column_number = Column(Integer, nullable=True)  # Số điểm 15p tối đa
    score1T_column_number = Column(Integer, nullable=True)   # Số điểm 1 tiết tối đa
    scoreF_column_number = Column(Integer, default=1, nullable=False)

    gradelevel = relationship('GradeLevel', backref='subjects')
    score_sheets = relationship('ScoreSheet', backref='subject', lazy=True)
    draft_scores = relationship('DraftScore', backref='subject', lazy=True)


# ========== SCORE MODELS ==========
class ScoreSheet(db.Model):
    __tablename__ = 'score_sheet'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('student.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subject.id'), nullable=False)
    semester_id = Column(Integer, ForeignKey('semester.id'), nullable=False)
    academic_year_id = Column(Integer, ForeignKey('academic_year.id'), nullable=False)

    classroom_id = Column(Integer, ForeignKey('classroom.id'), nullable=False)

    details = relationship('ScoreDetail', backref='score_sheet', lazy=True)

class ScoreDetail(db.Model):
    __tablename__ = 'score_detail'
    id = Column(Integer, primary_key=True)
    score_sheet_id = Column(Integer, ForeignKey('score_sheet.id'), nullable=False)
    type = Column(Enum(ScoreType), nullable=False)
    value = Column(Float, nullable=False)

class DraftScore(db.Model):
    __tablename__ = 'draft_score'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('student.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subject.id'), nullable=False)
    semester_id = Column(Integer, ForeignKey('semester.id'), nullable=False)
    academic_year_id = Column(Integer, ForeignKey('academic_year.id'), nullable=False)
    type = Column(Enum(ScoreType), nullable=False)
    value = Column(Float, nullable=False)

# ========== RELATIONSHIPS & RULE ==========
Teacher_Classroom = db.Table(
    'teacher_classroom',
    db.Column('teacher_id', db.Integer, db.ForeignKey('teacher.id'), primary_key=True),
    db.Column('classroom_id', db.Integer, db.ForeignKey('classroom.id'), primary_key=True)
)

class Regulation(db.Model):
    __tablename__ = 'regulation'
    id = Column(Integer, primary_key=True)
    min_age = Column(Integer, default=15)
    max_age = Column(Integer, default=20)
    max_class_size = Column(Integer, default=40)

# #xem giáo viên nào dạy lớp nào trong năm học nào
# class TeachingAssignment(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
#     subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
#     classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)
#     academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_year.id'), nullable=False)
#
#     teacher = relationship("Teacher", backref="teaching_assignments")
#     subject = relationship("Subject", backref="teaching_assignments")
#     classroom = relationship("Classroom", backref="teaching_assignments")
#     academic_year = relationship("AcademicYear", backref="teaching_assignments")
#
# #xem lại lịch sử lớp của học sinh trong từng năm học
# class EnrollmentHistory(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
#     classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)
#     academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_year.id'), nullable=False)
#     enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
#
#     student = relationship("Student", backref="enrollments")
#     classroom = relationship("Classroom", backref="enrollments")
#     academic_year = relationship("AcademicYear", backref="enrollments")

