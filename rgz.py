from flask import Blueprint, redirect, url_for, render_template, Blueprint, request, session
from Db import db
from Db.models import book, useradmin
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, login_required, current_user, logout_user
import os
from werkzeug.utils import secure_filename

rgz = Blueprint('rgz', __name__)

@rgz.route('/rgz')
def index():
    username_form = session.get('username')
    is_authenticated = current_user.is_authenticated
    page = request.args.get('page', 1, type=int)
    per_page = 20
    sort_field = request.args.get('sort', 'id')  # Здесь 'id' - поле, по которому происходит сортировка
    sort_direction = request.args.get('direction', 'asc')  # 'asc' - по возрастанию, 'desc' - по убыванию
    
    # Динамически определяем поле сортировки
    sort_attr = getattr(book, sort_field)
    if sort_direction == 'asc':
        book = book.query.order_by(sort_attr).paginate(page=page, per_page=per_page, error_out=False)
    else:
        book = book.query.order_by(sort_attr.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('index.html',  current_user=current_user, is_authenticated=is_authenticated, book=book, sort_field=sort_field,
                            sort_direction=sort_direction)  
      
@rgz.route('/rgz/login', methods=['GET', 'POST'])
def login():
    errors = []
    if request.method == 'GET':
        return render_template('login.html')
    username_form = request.form.get('username')
    password_form = request.form.get('password')
    my_user = useradmin.query.filter_by(username=username_form).first()
    if my_user is not None:
        # Сравнение введенного пароля с паролем администратора
        if my_user.password == password_form:
            login_user(my_user, remember=False)
            return redirect('/rgz')
        else:
            errors.append("Неправильный пароль")
            return render_template('login.html', errors=errors)
    if not (username_form or password_form):
        errors.append("Пожалуйста, заполните все поля")
        return render_template("login.html", errors=errors)
    if username_form == '' or password_form == '':
        errors.append("Пожалуйста, заполните все поля")
        return render_template('login.html', errors=errors)
    else:
        errors.append('Пользователя не существует')
        return render_template('login.html', errors=errors)
    
@rgz.route('/rgz/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect('/rgz')
UPLOAD_FOLDER = ''
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@rgz.route('/rgz/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        pages_str = request.form.get('pages')
        publisher = request.form.get('publisher')
        # Проверка, что pages_str не равно None или пустой строке
        if pages_str and pages_str.isdigit():
            pages = int(pages_str)
        else:
            # Если pages_str не является числом, установите значение по умолчанию (например, 0)
            pages = 0
        # Получение файла из формы
        cover_image = request.files.get('cover_image')
        # Проверка, что файл был загружен и имеет разрешенное расширение
        if cover_image and allowed_file(cover_image.filename):
            # Генерация уникального имени файла
            filename = secure_filename(cover_image.filename)
            # Сохранение файла в директории для хранения изображений
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            cover_image.save(file_path)
            # Создание новой книги с путем к изображению
            new_book = book(
                title=title,
                author=author,
                pages=pages,
                publisher=publisher,
                cover_image_url=f'uploads/{filename}'  # Путь к изображению
            )
            db.session.add(new_book)
            db.session.commit()
            return redirect('/rgz')
    return render_template('add_book.html')

@rgz.route('/rgz/delete_book/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    if current_user.is_authenticated:
        book_to_delete = book.query.get_or_404(book_id)
        db.session.delete(book_to_delete)
        db.session.commit()
        return redirect('/rgz')