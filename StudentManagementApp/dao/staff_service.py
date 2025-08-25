#staff_service.py
from StudentManagementApp.models import *
from StudentManagementApp import db
from datetime import datetime
import hashlib

# --- AUTH ---
def get_user_by_id(user_id):
    return User.query.get(user_id)

def auth_staff(username, password):
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
    return User.query.filter_by(username=username, password=password, role=Role.STAFF).first()

# --- QUY ĐỊNH ---
def get_regulation_value(attr):
    rule = Regulation.query.first()
    if not rule:
        return None
    return getattr(rule, attr, None)

# --- ACADEMIC YEAR ---
def get_active_academic_year():
    return AcademicYear.query.filter_by(is_active=True).first()

# --- CLASSROOMS ---
def get_all_classrooms():
    return Classroom.query.all()

def get_classroom_by_id(classroom_id):
    return Classroom.query.get(classroom_id)

def get_classrooms_by_gradelevel(gradelevel_id):
    return Classroom.query.filter_by(gradelevel_id=gradelevel_id).all()

def get_blank_classrooms():
    max_size = get_regulation_value("max_class_size")
    return [c for c in Classroom.query.all() if len(c.students) < max_size]

# --- STUDENTS ---
def get_all_students():
    return Student.query.all()

def get_student_by_id(student_id):
    return Student.query.get(student_id)

def get_student_by_class(classroom_id):
    return Student.query.filter_by(classroom_id=classroom_id).all()

def get_students_by_gradelevel(grade_id):
    return Student.query.filter_by(grade_id=grade_id).all()

def search_students_by_name(name, classroom_id=None):
    query = Student.query.filter(Student.name.ilike(f"%{name}%"))
    if classroom_id:
        query = query.filter_by(classroom_id=classroom_id)
    return query.all()

# --- SUBJECTS ---
def get_subject():
    return Subject.query.all()

def get_subject_by_id(subject_id):
    return Subject.query.get(subject_id)

# --- SEMESTERS ---
def get_semester():
    return Semester.query.all()

def get_semester_by_id(semester_id):
    return Semester.query.get(semester_id)

# --- GRADELEVELS ---
def get_grade():
    return GradeLevel.query.all()

# --- CLASS ASSIGNMENT ---
def create_class_list():
    grades = get_grade()
    unassigned_students = {g.id: [] for g in grades}
    active_year = get_active_academic_year()

    if not active_year:
        raise Exception("Năm học chưa bắt đầu hoặc đã kết thức!")

    for g in grades:
        students = get_students_by_gradelevel(g.id)
        unassigned = [s for s in students if not s.classroom_id]
        max_per_class = get_regulation_value("max_class_size")

        current_classes = Classroom.query.filter_by(gradelevel_id=g.id, academic_year_id=active_year.id).all()

        if not current_classes:
            new_class = create_new_classroom(g, 1)
            assign_teachers_to_class(new_class)
            current_classes = [new_class]

        suffix = len(current_classes) + 1
        while unassigned:
            # Tìm lớp còn chỗ
            placed = False
            for cls in current_classes:
                if cls.current_student < max_per_class:
                    cls.students.append(unassigned.pop(0))
                    db.session.commit()
                    placed = True
                    break

            if not placed:
                new_class = create_new_classroom(current_classes[0], suffix)
                assign_teachers_to_class(new_class)
                current_classes.append(new_class)
                suffix += 1

        unassigned_students[g.id] = [s for s in students if not s.classroom_id]

    return {
        "classes": get_all_classrooms(),
        "unassigned_students": unassigned_students
    }

# --- TẠO LỚP MỚI ---
def create_new_classroom(old_class, suffix):
    new_class_name = f"{old_class.gradelevel.name.value}A{suffix}"
    new_class = Classroom(
        name=new_class_name,
        gradelevel_id=old_class.gradelevel_id,
        academic_year_id=old_class.academic_year_id
    )
    db.session.add(new_class)
    db.session.commit()
    return new_class

# --- GÁN GIÁO VIÊN CHO LỚP MỚI ---
def assign_teachers_to_class(classroom):
    subjects_in_grade = Subject.query.filter_by(gradelevel_id=classroom.gradelevel_id).all()
    for subject in subjects_in_grade:
        teacher = Teacher.query.filter_by(subject_id=subject.id).order_by(db.func.rand()).first()
        if teacher:
            teacher.classrooms.append(classroom)
    db.session.commit()

# --- PHÂN LẠI LỚP KHI THAY ĐỔI QUY ĐỊNH ---
def reassign_overloaded_classes(max_size):
    overloaded_classes = [c for c in Classroom.query.all() if len(c.students) > max_size]

    for old_class in overloaded_classes:
        students = old_class.students
        extra_students = students[max_size:]

        available_classes = Classroom.query.filter(
            Classroom.gradelevel_id == old_class.gradelevel_id,
            Classroom.academic_year_id == old_class.academic_year_id
        ).all()

        for cls in available_classes:
            remaining = max_size - len(cls.students)
            if remaining > 0:
                to_move = extra_students[:remaining]
                for s in to_move:
                    s.classroom_id = cls.id
                extra_students = extra_students[remaining:]
                db.session.commit()

        while extra_students:
            existing_names = [c.name for c in Classroom.query.filter_by(gradelevel_id=old_class.gradelevel_id).all()]
            new_suffix = 1
            while f"{old_class.gradelevel.name.value}A{new_suffix}" in existing_names:
                new_suffix += 1

            new_class = create_new_classroom(old_class, new_suffix)

            for s in extra_students[:max_size]:
                s.classroom_id = new_class.id

            extra_students = extra_students[max_size:]
            db.session.commit()

            assign_teachers_to_class(new_class)

    db.session.commit()