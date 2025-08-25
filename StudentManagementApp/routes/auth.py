from flask import render_template, request, redirect, jsonify
from StudentManagementApp import app, login, db, dao
from StudentManagementApp.models import *
from flask_login import login_user, current_user, logout_user
from werkzeug.security import check_password_hash

# ✅ Trang chủ công khai (hiện trước khi đăng nhập)
@app.route('/')
def home_page():
    if current_user.is_authenticated:
        # Nếu đã đăng nhập → tự động chuyển đúng trang
        if current_user.role == Role.ADMIN:
            return redirect('/admin')
        elif current_user.role == Role.TEACHER:
            return redirect('/teacher')
        elif current_user.role == Role.STAFF:
            return redirect('/staff')
    return render_template('home.html')  # Trang public

# ✅ Trang đăng nhập
@app.route('/login', methods=['GET', 'POST'])
def login_view():
    err_msg = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)

            # Chuyển trang đúng theo vai trò
            if user.role == Role.ADMIN:
                return redirect('/admin')
            elif user.role == Role.TEACHER:
                return redirect('/teacher')
            elif user.role == Role.STAFF:
                return redirect('/staff')
        else:
            err_msg = 'Tên đăng nhập hoặc mật khẩu không đúng!'

    return render_template('login.html', err_msg=err_msg)

# ✅ Đăng xuất
@app.route('/logout')
def logout_view():
    logout_user()
    return redirect('/')

# ✅ Flask-Login: lấy người dùng theo ID
@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)
