#routes/teacher.py
from flask import Blueprint, render_template, request, send_file
from flask_login import current_user, login_required
from StudentManagementApp import db
from StudentManagementApp.models import Teacher, Classroom, Student, Semester, AcademicYear
from StudentManagementApp.dao import score_service, export_score_service, staff_service

teacher = Blueprint('teacher', __name__, url_prefix='/teacher')

@teacher.route('/')
@login_required
def index():
    teacher = Teacher.query.filter_by(id=current_user.id).first()
    return render_template('teacher/index.html', teacher=teacher)

@teacher.route('/avg_scores')
@login_required
def view_avg_scores():
    selected_class = request.args.get('class_id', type=int)
    selected_year_id = request.args.get('year', type=int)
    selected_semester = request.args.get('semester', type=int)

    teacher_obj = Teacher.query.filter_by(id=current_user.id).first()
    classes = teacher_obj.classrooms
    years = AcademicYear.query.order_by(AcademicYear.start_year.desc()).all()
    semesters = Semester.query.all()
    scores_list = []

    if selected_class and selected_year_id:
        students = Student.query.filter_by(classroom_id=selected_class).all()

        for student in students:
            if selected_semester:
                avg = score_service.calculate_avg_score(student.id, selected_year_id, selected_semester)
                scores_list.append({
                    "name": student.name,
                    "avg_score": round(avg, 2) if avg is not None else None
                })
            else:
                avg1 = score_service.calculate_avg_score(student.id, selected_year_id, 1)
                avg2 = score_service.calculate_avg_score(student.id, selected_year_id, 2)
                avg_year = round((avg1 + avg2) / 2, 2) if avg1 is not None and avg2 is not None else None
                scores_list.append({
                    "name": student.name,
                    "avg_score_sem1": round(avg1, 2) if avg1 is not None else None,
                    "avg_score_sem2": round(avg2, 2) if avg2 is not None else None,
                    "avg_score_year": avg_year
                })

    return render_template(
        'teacher/avg_scores.html',
        classes=classes,
        years=years,
        semesters=semesters,
        selected_class=selected_class,
        selected_year=selected_year_id,
        selected_semester=selected_semester,
        scores=scores_list
    )

@teacher.route('/export_avg_scores')
@login_required
def export_avg_scores():
    class_id = request.args.get('class_id', type=int)
    year_id = request.args.get('year', type=int)
    semester = request.args.get('semester', type=int)
    teacher = Teacher.query.filter_by(id=current_user.id).first()

    excel_file, filename = export_score_service.generate_avg_score_excel(class_id, year_id, semester, teacher=teacher)
    return send_file(excel_file, download_name=filename, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@teacher.route('/my_classes')
@login_required
def view_classes():
    teacher_obj = Teacher.query.filter_by(id=current_user.id).first()
    classrooms = teacher_obj.classrooms
    return render_template('teacher/my_classes.html', classrooms=classrooms)

@teacher.route('/class/<int:class_id>')
@login_required
def view_class_detail(class_id):
    classroom = Classroom.query.get_or_404(class_id)
    students = Student.query.filter_by(classroom_id=class_id).all()
    return render_template('teacher/class_detail.html', classroom=classroom, students=students)

@teacher.route('/select_for_grading', methods=['GET', 'POST'])
@login_required
def select_for_grading():
    teacher_obj = Teacher.query.filter_by(id=current_user.id).first()
    subject = teacher_obj.subject
    classes = teacher_obj.classrooms
    semesters = Semester.query.all()

    selected_class = selected_semester = None
    students = []
    scores_map = {}
    message = None

    if request.method == 'POST':
        class_id = int(request.form['class_id'])
        semester_id = int(request.form['semester_id'])
        selected_class = Classroom.query.get_or_404(class_id)
        selected_semester = Semester.query.get_or_404(semester_id)
        academic_year_id = selected_class.academic_year_id
        subject_id = subject.id

        students = Student.query.filter_by(classroom_id=class_id).all()

        # Lưu điểm chính thức
        if 'save_scores' in request.form:
            score_service.store_scores(
                request.form, students, academic_year_id, semester_id, subject_id
            )
            db.session.commit()

        # Lưu nháp
        elif 'draft' in request.form:
            score_service.save_draft_scores(
                request.form, students, academic_year_id, semester_id, subject_id
            )
            db.session.commit()

        scores_map = score_service.fetch_scores_for_students(
            students, academic_year_id, semester_id, subject_id
        )

    return render_template(
        'teacher/select_grading.html',
        classes=classes,
        semesters=semesters,
        selected_class=selected_class,
        selected_semester=selected_semester,
        students=students,
        scores_map=scores_map,
        subject=subject,
        message=message
    )
