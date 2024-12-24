from flask import Blueprint, redirect, url_for, render_template, request, session
from Db import db
from Db.models import book, useradmin
from werkzeug.security import check_password_hash
from flask_login import login_user, login_required, current_user, logout_user
from sqlalchemy import func
from utils import save_uploaded_file

rgz = Blueprint('rgz', __name__)

@rgz.route('/rgz')
def index():
    username_form = session.get('username')
    is_authenticated = current_user.is_authenticated
    page = request.args.get('page', 1, type=int)
    per_page = 20

    sort_field = request.args.get('sort', 'id')
    sort_direction = request.args.get('direction', 'asc')

    title_filter = request.args.get('title', '')
    author_filter = request.args.get('author', '')
    pages_filter = request.args.get('pages', '')
    publisher_filter = request.args.get('publisher', '')

    base_query = book.query

    if title_filter:
        base_query = base_query.filter(book.title.ilike(f"%{title_filter}%"))
    if author_filter:
        base_query = base_query.filter(book.author.ilike(f"%{author_filter}%"))
    if pages_filter:
        base_query = base_query.filter(book.pages == int(pages_filter))
    if publisher_filter:
        base_query = base_query.filter(book.publisher.ilike(f"%{publisher_filter}%"))

    sort_attr = getattr(book, sort_field)
    if sort_direction == 'asc':
        books = base_query.order_by(sort_attr).paginate(page=page, per_page=per_page, error_out=False)
    else:
        books = base_query.order_by(sort_attr.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('index.html', current_user=current_user, is_authenticated=is_authenticated, 
                           books=books, sort_field=sort_field, sort_direction=sort_direction,
                           title_filter=title_filter, author_filter=author_filter,
                           pages_filter=pages_filter, publisher_filter=publisher_filter)


@rgz.route('/rgz/login', methods=['GET', 'POST'])
def login():
    errors = []
    if request.method == 'GET':
        return render_template('login.html')

    username_form = request.form.get('username')
    password_form = request.form.get('password')

    my_user = useradmin.query.filter_by(username=username_form).first()

    if my_user is not None:
        # Сравнение введенного пароля с хэшированным паролем
        if check_password_hash(my_user.password, password_form):
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


@rgz.route('/rgz/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        pages_str = request.form.get('pages')
        publisher = request.form.get('publisher')

        if pages_str and pages_str.isdigit():
            pages = int(pages_str)
        else:
            pages = 0

        cover_image = request.files.get('cover_image')

        if cover_image:
            # Используйте функцию save_uploaded_file для сохранения оригинального имени файла
            filename = save_uploaded_file(cover_image, 'static/kartinki')

            if filename:
                max_id = db.session.query(func.max(book.id)).scalar()
                new_id = max_id + 1 if max_id is not None else 1

                new_book = book(
                    id=new_id,
                    title=title,
                    author=author,
                    pages=pages,
                    publisher=publisher,
                    cover_image_url=filename
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
    else:
        abort(403)