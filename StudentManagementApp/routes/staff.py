#routes/staff.py
from flask import render_template, request, redirect, session, jsonify, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from StudentManagementApp.models import *
from StudentManagementApp.dao import staff_service as dao
from datetime import datetime

staff = Blueprint('staff', __name__, url_prefix='/staff')

@staff.route('/')
@login_required
def index():
    staff_info = Staff.query.filter_by(id=current_user.id).first()
    return render_template('staff/index.html', staff=staff_info)

@staff.route("/AddStudent")
def AddStudent():
    students = dao.get_all_students()
    grades = dao.get_grade()
    return render_template('staff/AddStudent.html', students=students, grades=grades)

@staff.route("/ThemHocSinh", methods=['POST'])
def ThemHocSinh():
    fullname = request.form.get('fullname')
    gender = request.form.get('sex')
    DoB = request.form.get('DoB')
    address = request.form.get('address')
    phone = request.form.get('phonenumber')
    email = request.form.get('email')
    grade_id = request.form.get('grade')

    if not phone or len(phone) != 10 or not phone.isdigit():
        return jsonify({'success': False, 'error': 'Số điện thoại sai. Vui lòng nhập lại!'})

    if not email.endswith('@gmail.com'):
        return jsonify({'success': False, 'error': 'Email sai. Vui lòng nhập lại!'})

    try:
        birth_date = datetime.strptime(DoB, '%Y-%m-%d')
    except:
        return jsonify({'success': False, 'error': 'Bạn chưa nhập ngày sinh. Vui lòng thử lại!'})

    current_year = datetime.now().year
    min_age = dao.get_regulation_value("min_age")
    max_age = dao.get_regulation_value("max_age")
    age = current_year - birth_date.year

    if age < min_age or age > max_age:
        return jsonify({'success': False, 'error': f'Ngày sinh không hợp lệ. Tuổi phải từ {min_age} đến {max_age}.'})

    try:
        student = Student(
            name=fullname,
            gender=Gender[gender],
            birth_date=birth_date,
            address=address,
            phone=phone,
            email=email,
            grade_id=int(grade_id)
        )
        db.session.add(student)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Lưu thành công',
            'student': {
                'id': student.id,
                'name': student.name,
                'sex': 'Nam' if student.gender == Gender.MALE else 'Nữ',
                'DoB': birth_date.strftime('%d/%m/%Y'),
                'address': student.address,
                'email': student.email,
                'phonenumber': student.phone,
                'grade': student.gradelevel.name.value if student.gradelevel else ''
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Lỗi khi lưu học sinh: {str(e)}'})


@staff.route("/api/searchStudentAddStu", methods=['POST'])
def search_student_add_stu():
    name = request.json.get('searchstudentAddStu')
    grade_id = request.json.get('grade_id')
    students = dao.search_students_by_name(name)
    if grade_id:
        students = [s for s in students if str(s.grade_id) == str(grade_id)]

    result = {0: {"quantity": len(students)}}
    for idx, student in enumerate(students, 1):
        result[idx] = {
            "id": student.id,
            "name": student.name,
            "sex": "Nam" if student.gender == Gender.MALE else "Nữ",
            "DoB": student.birth_date.strftime("%d/%m/%Y"),
            "address": student.address,
            "email": student.email,
            "phonenumber": student.phone,
            "grade": student.gradelevel.name.value,
            "class": student.classroom.name if student.classroom else "Chưa có lớp"
        }
    return jsonify(result)

@staff.route('/api/getStudents')
def get_students_api():
    students = dao.get_all_students()
    return jsonify([
        {
            "id": s.id,
            "name": s.name,
            "sex": "Nam" if s.gender == Gender.MALE else "Nữ",
            "DoB": s.birth_date.strftime("%d/%m/%Y"),
            "address": s.address,
            "email": s.email,
            "phonenumber": s.phone,
            "grade": s.gradelevel.name.value
        } for s in students
    ])

@staff.route('/api/deleteStudent/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    try:
        student = dao.get_student_by_id(student_id)
        if student:
            db.session.delete(student)
            db.session.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Học sinh không tồn tại'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@staff.route("/CreateClassList")
def CreateClassList():
    result = dao.create_class_list()
    return render_template('staff/CreateClassList.html',
                           classes=result["classes"],
                           unassigned_10=result["unassigned_students"].get(1, []),
                           unassigned_11=result["unassigned_students"].get(2, []),
                           unassigned_12=result["unassigned_students"].get(3, []),
                           grades=dao.get_grade())


@staff.route('/api/printClass', methods=['POST'])
def PrintClass():
    id_class = request.json.get('id_class')
    classroom = dao.get_classroom_by_id(id_class)
    students = dao.get_student_by_class(id_class)

    result = {0: {"id": classroom.id, "class": classroom.name, "quantity": len(students)}}
    for i, student in enumerate(students, 1):
        result[i] = {
            "name": student.name,
            "sex": student.gender.value,
            "DoB": student.birth_date.strftime("%d/%m/%Y"),
            "address": student.address
        }
    return jsonify(result)


@staff.route("/AdjustClass")
def AdjustClass():
    active_year = dao.get_active_academic_year()
    classes = Classroom.query.filter_by(academic_year_id=active_year.id).all() if active_year else []
    return render_template("staff/AdjustClass.html",
                           classes=classes,
                           grades=dao.get_grade(),
                           max_per_class=dao.get_regulation_value("max_class_size"))

@staff.route('/change_class', methods=['POST'])
def change_class():
    data = request.get_json()
    student_id = data.get('student_id')
    new_class_id = data.get('new_class_id')

    student = dao.get_student_by_id(student_id)
    new_class = dao.get_classroom_by_id(new_class_id)

    if not student or not new_class:
        return jsonify({"success": False, "message": "Học sinh hoặc lớp không tồn tại"}), 404

    if student.classroom_id == new_class.id:
        return jsonify({"success": False, "message": "Học sinh đã thuộc lớp này"}), 400

    max_per_class = dao.get_regulation_value("max_class_size")

    if new_class.current_student >= max_per_class:
        return jsonify({"success": False, "message": "Lớp đã đầy"}), 400

    if student.grade_id != new_class.gradelevel_id:
        return jsonify({"success": False, "message": "Không cùng khối"}), 400

    try:
        old_class = dao.get_classroom_by_id(student.classroom_id) if student.classroom_id else None
        student.classroom_id = new_class.id
        db.session.commit()

        return jsonify({
            "success": True,
            "message": f"Đã chuyển {student.name} đến lớp {new_class.name}",
            "old_class": {
                "id": old_class.id if old_class else None,
                "name": old_class.name if old_class else None,
                "current_student": old_class.current_student if old_class else 0
            },
            "new_class": {
                "id": new_class.id,
                "name": new_class.name,
                "current_student": new_class.current_student
            },
            "max_per_class": max_per_class
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@staff.route('/api/getClassesByGrade/<int:grade_id>')
def get_classes_by_grade(grade_id):
    classes = dao.get_classrooms_by_gradelevel(grade_id)
    return jsonify([{'id_class': c.id, 'name_class': c.name} for c in classes])

@staff.route("/api/searchStudent", methods=['POST'])
def search_student():
    data = request.get_json()
    name = data.get('searchstudent')
    class_id = data.get('class_id')
    students = dao.search_students_by_name(name, classroom_id=class_id)

    result = {0: {"quantity": len(students)}}
    for idx, student in enumerate(students, 1):
        result[idx] = {
            "id": student.id,
            "name": student.name,
            "class": student.classroom.name if student.classroom else "Chưa có lớp"
        }
    return jsonify(result)