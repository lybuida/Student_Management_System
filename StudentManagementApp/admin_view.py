#admin_view.py
from StudentManagementApp.models import *
from StudentManagementApp import app, db, dao
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose, AdminIndexView
from flask_login import logout_user, current_user
from flask import redirect, render_template, url_for, request


class AuthenticatedAdmin(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == Role.ADMIN


class Authenticated_Admin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == Role.ADMIN


class AuthenticatedUser(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class StatsView(AuthenticatedAdmin):
    @expose("/")
    def index(self):
        return self.render(
            'admin/Statistics.html',
            subjects=dao.get_subject(),
            semesters=dao.get_semester(),
            academic_years=AcademicYear.query.order_by(AcademicYear.start_year.desc()).all()
        )


class ChangeRule(AuthenticatedAdmin):
    @expose("/")
    def index(self):
        rule = Regulation.query.first()
        return self.render(
            'admin/ChangeRule.html',
            quantity=rule.max_class_size if rule else 40,
            min_age=rule.min_age if rule else 15,
            max_age=rule.max_age if rule else 20
        )


class SubjectView(Authenticated_Admin):
    column_list = ['id', 'name']
    column_searchable_list = ['name']
    column_filters = ['id', 'name']
    column_editable_list = ['name']
    edit_modal = True
    can_export = True
    list_template = 'admin/subject_view.html'

    @expose('/')
    def index(self):
        keyword = request.args.get('q', '')
        if keyword:
            subjects = Subject.query.filter(Subject.name.ilike(f"%{keyword}%")).all()
        else:
            subjects = Subject.query.all()

        gradelevels = GradeLevel.query.all()
        return self.render('admin/subject_view.html', data=subjects, gradelevels=gradelevels)


    @expose('/subject/create', methods=['POST'])
    def create_subject(self):
        name = request.form.get('name', '').strip()
        normalized_name = name.lower()

        from flask import flash
        from sqlalchemy import func

        # Kiểm tra trùng
        existing = Subject.query.filter(func.lower(Subject.name) == normalized_name).first()
        if existing:
            flash(f"Môn học '{name}' đã tồn tại!", "danger")
        else:
            gradelevel_id = request.form.get('gradelevel_id', type=int)

            subject = Subject(
                name=name,
                score15P_column_number=request.form.get('score15', type=int),
                score1T_column_number=request.form.get('score1tiet', type=int),
                scoreF_column_number=request.form.get('score_final', type=int),
                gradelevel_id=gradelevel_id if gradelevel_id else None
            )

            db.session.add(subject)
            try:
                db.session.commit()
                flash(f"Đã thêm môn học '{name}' thành công.", "success")
            except Exception as e:
                db.session.rollback()
                flash("Đã xảy ra lỗi khi thêm môn học.", "danger")

        return redirect(url_for('.index'))



    @expose('/subject/update/<int:subject_id>', methods=['POST'])
    def update_subject(self, subject_id):
        subject = Subject.query.get(subject_id)
        if subject:
            new_name = request.form.get('name')
            score15 = request.form.get('score15', type=int)
            score1tiet = request.form.get('score1tiet', type=int)
            score_final = request.form.get('score_final', type=int)

            from flask import flash

            # Nếu đổi tên, kiểm tra tên mới đã tồn tại chưa (không phân biệt hoa thường)
            if new_name.lower() != subject.name.lower() and Subject.query.filter(Subject.name.ilike(new_name)).first():
                flash(f"Môn học '{new_name}' đã tồn tại!", "danger")
            else:
                subject.name = new_name
                subject.score15P_column_number = score15
                subject.score1T_column_number = score1tiet
                subject.scoreF_column_number = score_final
                db.session.commit()
                flash(f"Cập nhật môn học '{subject.name}' thành công.", "success")

        return redirect(url_for('.index'))

    @expose('/subject/delete/<int:subject_id>', methods=['POST'])
    def delete_subject(self, subject_id):
        subject = Subject.query.get(subject_id)
        if subject:
            db.session.delete(subject)
            db.session.commit()
            from flask import flash
            flash(f"Đã xoá môn học '{subject.name}' thành công.")
        return redirect(url_for('.index'))


class LogoutView(AuthenticatedUser):
    @expose("/")
    def index(self):
        logout_user()
        return redirect('/admin')


class AdminIndex(AdminIndexView):
    @expose('/')
    def index(self):
        total_users = dao.count_users()
        total_subjects = dao.count_subjects()
        total_classes = dao.count_classrooms()
        total_teachers = dao.count_teachers()
        return self.render('admin/index.html',
                           total_users=total_users,
                           total_subjects=total_subjects,
                           total_classes=total_classes,
                           total_teachers=total_teachers)


admin = Admin(app=app, name='Quản lý học sinh', template_mode='bootstrap4', index_view=AdminIndex(name='Trang chủ'))

admin.add_view(SubjectView(Subject, db.session, name='Quản lý môn học', endpoint='subjectview'))
admin.add_view(StatsView(name='Thống kê báo cáo'))
admin.add_view(ChangeRule(name='Thay đổi quy định'))
admin.add_view(LogoutView(name='Đăng xuất'))
