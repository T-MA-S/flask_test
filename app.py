from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from forms import *
from utils import init_db_data

import xlwt
import csv
from io import StringIO, BytesIO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://stage_user:qwerty789@db:5432/test_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret_key'

db = SQLAlchemy(app)

migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)


# модель ассортимент
class Assortment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    measureUnit = db.Column(db.String(5), nullable=False)


# модель подразделения
class Division(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)


# usermodel
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.email

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        flash('Неверное имя пользователя или пароль')
        return redirect(url_for('login'))

    login_user(user)

    return redirect(url_for('index'))


# главная страница
@app.route('/')
@login_required
def index():
    if request.method == "GET":
        assortment_form = AssortmentForm()
        division_form = DivisionForm()

        goods = db.session.query(Assortment).all()
        divisions = db.session.query(Division).all()

        context = {
            "goods": goods,
            "divisions": divisions,
            "assortment_form": assortment_form,
            "division_form": division_form
        }
        return render_template('index.html', **context)


@app.route('/add_product', methods=['POST'])
@login_required
def add_product():
    form = AssortmentForm()
    if form.validate_on_submit():
        assortment = Assortment(name=form.name.data, measureUnit=form.measureUnit.data)
        db.session.add(assortment)
        db.session.commit()
        return redirect(url_for('index'))
    return redirect(url_for('index'))


@app.route('/add_division', methods=['POST'])
@login_required
def add_division():
    form = DivisionForm()
    if form.validate_on_submit():
        division = Division(name=form.name.data)
        db.session.add(division)
        db.session.commit()
        return redirect(url_for('index'))
    return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/delete_assortment/<assortment_id>', methods=['DELETE'])
@login_required
def delete_assortment(assortment_id):
    good = db.session.get(Assortment, assortment_id)
    if good:
        db.session.delete(good)
        db.session.commit()
        return jsonify({'success': True}), 200
    else:
        return jsonify({'error': 'Resource not found'}), 404


@app.route('/delete_division/<division_id>', methods=['DELETE'])
@login_required
def delete_division(division_id):
    division = db.session.get(Division, division_id)
    if division:
        db.session.delete(division)
        db.session.commit()
        return jsonify({'success': True}), 200
    else:
        return jsonify({'error': 'Resource not found'}), 404


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')


@app.route('/download_assortment_csv')
@login_required
def download_assortment_csv():
    separator = ';'  # comma separated value, но ; excel поддерживает
    # изменяется по запросу заказчика

    assortments = db.session.query(Assortment).all()

    output = StringIO()
    writer = csv.writer(output, delimiter=separator, quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')

    writer.writerow(['id', 'Наименование', 'Единица измерения'])

    for assortment in assortments:
        writer.writerow([assortment.id, assortment.name, assortment.measureUnit])

    response = make_response(output.getvalue().encode('cp1251'))
    response.headers.set('Content-Type', 'text/csv; charset=cp1251')
    response.headers.set('Content-Disposition', 'attachment', filename='assortment.csv')
    return response


@app.route('/download_assortment_xls')
@login_required
def download_assortment_xls():
    assortments = db.session.query(Assortment).all()

    output = BytesIO()
    book = xlwt.Workbook(encoding='cp1251')
    sheet = book.add_sheet('Assortment')

    sheet.write(0, 0, 'id')
    sheet.write(0, 1, 'Наименование')
    sheet.write(0, 2, 'Единица измерения')

    row = 1
    for assortment in assortments:
        sheet.write(row, 0, assortment.id)
        sheet.write(row, 1, assortment.name)
        sheet.write(row, 2, assortment.measureUnit)
        row += 1

    book.save(output)

    response = make_response(output.getvalue())
    response.headers.set('Content-Type', 'application/vnd.ms-excel')
    response.headers.set('Content-Disposition', 'attachment', filename='assortment.xls')
    return response


@app.route('/download_division_csv')
@login_required
def download_division_csv():
    separator = ';'  # comma separated value, но ; excel поддерживает
    # изменяется по запросу заказчика

    divisions = db.session.query(Division).all()

    output = StringIO()
    writer = csv.writer(output, delimiter=separator, quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')

    writer.writerow(['id', 'Наименование'])

    for division in divisions:
        writer.writerow([division.id, division.name])

    response = make_response(output.getvalue().encode('cp1251'))
    response.headers.set('Content-Type', 'text/csv; charset=cp1251')
    response.headers.set('Content-Disposition', 'attachment', filename='divisions.csv')
    return response


@app.route('/download_division_xls')
@login_required
def download_division_xls():
    divisions = db.session.query(Division).all()

    output = BytesIO()
    book = xlwt.Workbook(encoding='cp1251')
    sheet = book.add_sheet('Divisions')

    sheet.write(0, 0, 'id')
    sheet.write(0, 1, 'Наименование')

    row = 1
    for division in divisions:
        sheet.write(row, 0, division.id)
        sheet.write(row, 1, division.name)
        row += 1

    book.save(output)

    response = make_response(output.getvalue())
    response.headers.set('Content-Type', 'application/vnd.ms-excel')
    response.headers.set('Content-Disposition', 'attachment', filename='divisions.xls')
    return response


if __name__ == '__main__':
    with app.app_context():
        # создание тестового набора данных
        init_db_data(User, Assortment, Division, db)

    app.run(debug=True, host='0.0.0.0')
