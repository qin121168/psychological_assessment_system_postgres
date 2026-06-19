#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应急中心 · 心理测评系统
后端主程序 - Flask + PostgreSQL（兼容 SQLite 本地开发）
"""

import os
from datetime import timedelta
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import generate_password_hash, check_password_hash

# ==================== 配置 ====================
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'psychological_assessment_system_2024_secret_key')
app.permanent_session_lifetime = timedelta(hours=2)  # Session 2小时过期

# 数据库配置：优先使用环境变量 DATABASE_URL（Render PostgreSQL），否则使用本地 SQLite
DATABASE_URL = os.environ.get('DATABASE_URL')
USE_POSTGRES = bool(DATABASE_URL)

if USE_POSTGRES:
    import psycopg2
    import psycopg2.extras
    # Render 的 DATABASE_URL 可能以 postgres:// 开头，需要替换为 postgresql://
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
else:
    import sqlite3
    DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'users.db')


# ==================== 数据库 ====================
def get_db():
    """获取数据库连接"""
    if 'db' not in g:
        if USE_POSTGRES:
            g.db = psycopg2.connect(DATABASE_URL)
            g.db.cursor_factory = psycopg2.extras.RealDictCursor
        else:
            g.db = sqlite3.connect(DATABASE)
            g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    """关闭数据库连接"""
    if 'db' in g:
        g.db.close()


def init_db():
    """初始化数据库，创建用户表"""
    if USE_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL)
        conn.cursor_factory = psycopg2.extras.RealDictCursor
        cursor = conn.cursor()

        # 创建用户表（PostgreSQL 语法）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                is_admin INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    else:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # 创建用户表（SQLite 语法）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

    # 检查是否存在管理员账号，不存在则创建
    cursor.execute('SELECT * FROM users WHERE username = %s', ('admin',) if USE_POSTGRES else ('admin',))
    if not cursor.fetchone():
        admin_hash = generate_password_hash('admin123')
        cursor.execute(
            'INSERT INTO users (username, password_hash, is_admin) VALUES (%s, %s, %s)' if USE_POSTGRES
            else 'INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)',
            ('admin', admin_hash, 1)
        )
        print('✓ 默认管理员账号已创建: admin / admin123')

    conn.commit()
    conn.close()


# ==================== 登录验证装饰器 ====================
def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """管理员权限验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if not session.get('is_admin'):
            flash('您没有管理员权限', 'error')
            return redirect(url_for('assessment'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== 路由 ====================

# ---------- 登录页 ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('请输入用户名和密码', 'error')
            return render_template('login.html')

        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session.permanent = True
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = bool(user['is_admin'])

            # 管理员跳转到后台，普通用户跳转到测评
            if user['is_admin']:
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('assessment'))
        else:
            flash('用户名或密码错误', 'error')

    return render_template('login.html')


# ---------- 登出 ----------
@app.route('/logout')
def logout():
    """退出登录"""
    session.clear()
    flash('您已安全退出', 'success')
    return redirect(url_for('login'))


# ---------- 测评系统主页 ----------
@app.route('/')
@login_required
def index():
    """首页重定向到测评"""
    return redirect(url_for('assessment'))


@app.route('/assessment')
@login_required
def assessment():
    """心理测评系统主页面"""
    return render_template('assessment.html', username=session.get('username'))


# ---------- 后台管理 ----------
@app.route('/admin')
@admin_required
def admin():
    """后台管理首页 - 用户列表"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users ORDER BY id ASC')
    users = cursor.fetchall()
    return render_template('admin.html', users=users, username=session.get('username'))


# ---------- 新增用户 ----------
@app.route('/admin/user/add', methods=['POST'])
@admin_required
def add_user():
    """新增用户"""
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    is_admin = 1 if request.form.get('is_admin') else 0

    if not username or not password:
        flash('用户名和密码不能为空', 'error')
        return redirect(url_for('admin'))

    if len(password) < 6:
        flash('密码长度不能少于6位', 'error')
        return redirect(url_for('admin'))

    db = get_db()
    cursor = db.cursor()

    # 检查用户名是否已存在
    cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
    existing = cursor.fetchone()
    if existing:
        flash('用户名已存在', 'error')
        return redirect(url_for('admin'))

    # 创建用户
    password_hash = generate_password_hash(password)
    cursor.execute(
        'INSERT INTO users (username, password_hash, is_admin) VALUES (%s, %s, %s)',
        (username, password_hash, is_admin)
    )
    db.commit()

    flash(f'用户 {username} 创建成功', 'success')
    return redirect(url_for('admin'))


# ---------- 修改密码 ----------
@app.route('/admin/user/<int:user_id>/password', methods=['POST'])
@admin_required
def change_password(user_id):
    """修改用户密码"""
    new_password = request.form.get('new_password', '')

    if not new_password or len(new_password) < 6:
        flash('密码长度不能少于6位', 'error')
        return redirect(url_for('admin'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()

    if not user:
        flash('用户不存在', 'error')
        return redirect(url_for('admin'))

    password_hash = generate_password_hash(new_password)
    cursor.execute('UPDATE users SET password_hash = %s WHERE id = %s', (password_hash, user_id))
    db.commit()

    flash(f'用户 {user["username"]} 的密码已更新', 'success')
    return redirect(url_for('admin'))


# ---------- 删除用户 ----------
@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """删除用户"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()

    if not user:
        flash('用户不存在', 'error')
        return redirect(url_for('admin'))

    if user['username'] == 'admin':
        flash('不能删除默认管理员账号', 'error')
        return redirect(url_for('admin'))

    # 不能删除自己
    if user_id == session.get('user_id'):
        flash('不能删除当前登录的账号', 'error')
        return redirect(url_for('admin'))

    cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
    db.commit()

    flash(f'用户 {user["username"]} 已删除', 'success')
    return redirect(url_for('admin'))


# ==================== 启动 ====================
if __name__ == '__main__':
    # 初始化数据库
    init_db()
    print('=' * 50)
    print('  心理测评系统启动成功')
    print('  数据库类型: ' + ('PostgreSQL' if USE_POSTGRES else 'SQLite'))
    print('  访问地址: http://127.0.0.1:5000')
    print('  默认管理员: admin / admin123')
    print('=' * 50)
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
