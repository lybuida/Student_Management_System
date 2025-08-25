# === INIT DB SCRIPT WITH SUBJECTS SHARED ACROSS GRADES ===
from StudentManagementApp import app
from StudentManagementApp.models import *
from faker import Faker
from werkzeug.security import generate_password_hash
import random

fake = Faker('vi_VN')

with app.app_context():
    # Xoá và tạo lại toàn bộ cơ sở dữ liệu
    db.drop_all()
    db.create_all()

    # Quy định chung về độ tuổi và sĩ số lớp
    rule = Regulation(min_age=15, max_age=20, max_class_size=40)
    db.session.add(rule)

    # Tạo năm học hiện hành
    year_2024 = AcademicYear(start_year=2024, end_year=2025, is_active=True)
    db.session.add(year_2024)
    db.session.flush()

    # Tạo các khối lớp 10, 11, 12
    grade10 = GradeLevel(id=1, name=Grade.GRADE_10)
    grade11 = GradeLevel(id=2, name=Grade.GRADE_11)
    grade12 = GradeLevel(id=3, name=Grade.GRADE_12)
    db.session.add_all([grade10, grade11, grade12])
    db.session.flush()

    # Tạo các môn học dùng chung cho mọi khối
    subject_configs = [
        ("Toán", 5, 3),
        ("Văn", 4, 2),
        ("Anh", 3, 2),
        ("Lý", 4, 2),
        ("Hóa", 4, 2),
        ("Sinh", 4, 2),
        ("Tin", 3, 1),
        ("GDCD", 2, 1),
    ]
    subjects = [Subject(name=name, score15P_column_number=s15, score1T_column_number=s1t)
                for name, s15, s1t in subject_configs]
    db.session.add_all(subjects)
    db.session.flush()

    # Tạo người dùng admin, giáo viên A và nhân viên B
    admin = User(id=1, name='Quản trị viên', username='admin', password=generate_password_hash('admin123'), role=Role.ADMIN)
    teacher = User(id=2, name='Giáo viên A', username='teacher1', password=generate_password_hash('teacher123'), role=Role.TEACHER)
    staff = User(id=3, name='Nhân viên B', username='staff1', password=generate_password_hash('staff123'), role=Role.STAFF)
    db.session.add_all([admin, teacher, staff])
    db.session.flush()

    db.session.add_all([
        Admin(id=admin.id),
        Teacher(id=teacher.id, subject_id=subjects[0].id),  # Giáo viên A dạy Toán
        Staff(id=staff.id)
    ])
    db.session.flush()

    # Tạo 2 học kỳ
    semester1 = Semester(name='Học kỳ 1')
    semester2 = Semester(name='Học kỳ 2')
    db.session.add_all([semester1, semester2])
    db.session.flush()

    # Tạo lớp học: 2 lớp mỗi khối
    class_map = {}
    for grade in [grade10, grade11, grade12]:
        class_map[grade.id] = []
        for i in range(1, 3):
            c = Classroom(name=f"{grade.name.value}A{i}", gradelevel_id=grade.id, academic_year_id=year_2024.id)
            db.session.add(c)
            db.session.flush()
            class_map[grade.id].append(c)

    # Gán lớp khối 10 cho giáo viên A
    teacher_obj = db.session.get(Teacher, 2)
    for c in class_map[grade10.id]:
        teacher_obj.classrooms.append(c)

    # Thêm giáo viên B dạy môn Văn, dạy lớp khối 11
    teacher_b = User(id=4, name='Giáo viên B', username='teacher2', password=generate_password_hash('teacher123'), role=Role.TEACHER)
    db.session.add(teacher_b)
    db.session.flush()

    db.session.add(Teacher(id=teacher_b.id, subject_id=subjects[1].id))
    db.session.flush()

    teacher_b_obj = db.session.get(Teacher, teacher_b.id)
    for c in class_map[grade11.id]:
        teacher_b_obj.classrooms.append(c)

    # Tạo học sinh (40 mỗi khối, chia đều vào A1 và A2)
    students = []
    for grade in [grade10, grade11, grade12]:
        for i in range(40):
            classroom = class_map[grade.id][i % 2]
            s = Student(
                name=fake.name(),
                gender=random.choice([Gender.MALE, Gender.FEMALE]),
                birth_date=fake.date_of_birth(minimum_age=15, maximum_age=20),
                address=fake.address(),
                phone=fake.phone_number(),
                email=fake.email(),
                classroom_id=classroom.id,
                grade_id=grade.id
            )
            students.append(s)
    db.session.add_all(students)
    db.session.flush()

    # Gán ScoreSheet cho từng học sinh, mỗi môn, mỗi học kỳ
    semesters = Semester.query.all()
    for student in students:
        for semester in semesters:
            for subject in subjects:
                sheet = ScoreSheet(
                    student_id=student.id,
                    subject_id=subject.id,
                    semester_id=semester.id,
                    academic_year_id=year_2024.id,
                    classroom_id=student.classroom_id
                )
                db.session.add(sheet)
    db.session.flush()

    # Tạo điểm mẫu cho từng ScoreSheet
    score_sheets = ScoreSheet.query.all()
    for sheet in score_sheets:
        fif_min, one_period, final = (5, 10), (5, 9), (5, 10)
        db.session.add_all([
            ScoreDetail(score_sheet_id=sheet.id, type=ScoreType.FIFTEEN_MIN, value=random.uniform(*fif_min)),
            ScoreDetail(score_sheet_id=sheet.id, type=ScoreType.FIFTEEN_MIN, value=random.uniform(*fif_min)),
            ScoreDetail(score_sheet_id=sheet.id, type=ScoreType.FIFTEEN_MIN, value=random.uniform(*fif_min)),
            ScoreDetail(score_sheet_id=sheet.id, type=ScoreType.ONE_PERIOD, value=random.uniform(*one_period)),
            ScoreDetail(score_sheet_id=sheet.id, type=ScoreType.ONE_PERIOD, value=random.uniform(*one_period)),
            ScoreDetail(score_sheet_id=sheet.id, type=ScoreType.FINAL, value=random.uniform(*final)),
        ])

    db.session.commit()
    print("Dữ liệu đã được khởi tạo thành công")
