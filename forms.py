from flask_wtf import FlaskForm
from wtforms import StringField, validators


class AssortmentForm(FlaskForm):
    name = StringField('Наименование', validators=[validators.DataRequired(), validators.Length(max=255)],
                       render_kw={"class": "form-control"})
    measureUnit = StringField('Единица измерения', validators=[validators.DataRequired(), validators.Length(max=5)],
                              render_kw={"class": "form-control"})


class DivisionForm(FlaskForm):
    name = StringField('Наименование', validators=[validators.DataRequired(), validators.Length(max=255)],
                       render_kw={"class": "form-control"})
