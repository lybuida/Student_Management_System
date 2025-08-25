#routes/admin.py
from flask import render_template, request, jsonify
from StudentManagementApp import app, db, utils
from StudentManagementApp.models import Regulation, Classroom, AcademicYear
from StudentManagementApp.dao import staff_service, stat_service

# === API: Thống kê điểm theo môn học ===
@app.route("/api/statisticsScore", methods=['POST'])
def StatisticsScore():
    id_subject = request.json.get('id_subject')
    id_semester = request.json.get('id_semester')
    id_year = request.json.get('id_year')

    if not all([id_subject, id_semester, id_year]):
        return jsonify({'status': 400, 'content': 'Thiếu thông tin lọc'}), 400

    subject = staff_service.get_subject_by_id(id_subject)
    semester = staff_service.get_semester_by_id(id_semester)
    year = AcademicYear.query.get(id_year)

    if not all([subject, semester, year]):
        return jsonify({'status': 404, 'content': 'Dữ liệu không hợp lệ'}), 404

    # Nếu môn học có gradelevel_id, chỉ lấy lớp thuộc khối đó
    if subject.gradelevel_id:
        classes = Classroom.query.filter_by(
            academic_year_id=year.id,
            gradelevel_id=subject.gradelevel_id
        ).all()
    else:
        classes = Classroom.query.filter_by(academic_year_id=year.id).all()

    result = {
        0: {
            'subject': subject.name,
            'semester': semester.name,
            'schoolyear': f"{year.start_year}–{year.end_year}",
            'quantity': len(classes)
        }
    }

    for idx, classroom in enumerate(classes, start=1):
        statistics = stat_service.statistics_subject(
            classroom_id=classroom.id,
            subject_id=id_subject,
            semester_id=id_semester
        )
        passed_count = sum(1 for s in statistics if s['score'] >= 5)
        total = len(statistics)
        rate = round((passed_count / total) * 100, 1) if total else 0

        result[idx] = {
            'class': classroom.name,
            'quantity_student': total,
            'quantity_passed': passed_count,
            'rate': rate
        }

    return jsonify(result)

# === API: Thay đổi quy định sĩ số và độ tuổi ===
@app.route("/api/changeRule", methods=['POST'])
def ChangeRule():
    quantity = int(request.json.get('quantity'))
    min_age = int(request.json.get('min_age'))
    max_age = int(request.json.get('max_age'))

    if quantity <= 0 or min_age <= 0 or max_age <= 0:
        return jsonify({'status': 500, 'content': 'Thông tin không hợp lệ. Vui lòng kiểm tra lại!'})

    if min_age >= max_age:
        return jsonify({'status': 500, 'content': 'Tuổi lớn nhất phải lớn hơn tuổi nhỏ nhất. Vui lòng kiểm tra lại!'})

    # Kiểm tra có lớp nào đang vượt sĩ số không
    overloaded_classes = [c for c in Classroom.query.all() if len(c.students) > quantity]
    need_reassign = len(overloaded_classes) > 0

    # Cập nhật hoặc tạo mới bản ghi Regulation
    rule = Regulation.query.first()
    if not rule:
        rule = Regulation(min_age=min_age, max_age=max_age, max_class_size=quantity)
        db.session.add(rule)
    else:
        rule.min_age = min_age
        rule.max_age = max_age
        rule.max_class_size = quantity

    db.session.commit()

    if need_reassign:
        return jsonify({
            'status': 300,
            'content': 'Một số lớp hiện tại có sĩ số vượt quá giới hạn mới. '
                       'Hệ thống sẽ tự động tạo lớp mới và phân bổ lại học sinh. Bạn có muốn tiếp tục không?'
        })

    return jsonify({'status': 200, 'content': 'Thay đổi quy định thành công!'})


@app.route("/api/reassign_overloaded", methods=['POST'])
def reassign_after_confirm():
    from StudentManagementApp.dao.staff_service import reassign_overloaded_classes
    max_size = Regulation.query.first().max_class_size
    reassign_overloaded_classes(max_size)
    return jsonify({'message': 'Thay đổi quy định thành công!'})



