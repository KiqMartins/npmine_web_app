from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Optional
from flask import request
from flask_babel import _

class CompoundForm(FlaskForm):
    doi = StringField('DOI Link', validators=[DataRequired()])
    inchikey = StringField('InChI Key', validators=[DataRequired()])
    genus = StringField('Genus', validators=[Optional()])
    origin_type = SelectField('Origin Type', choices=[('Bacteria', 'Bacteria'), ('Fungi', 'Fungi')])
    species = StringField('Species', default='sp', validators=[Optional()])
    submit = SubmitField('Submit')

class SearchForm(FlaskForm):
    q = StringField(_('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'meta' not in kwargs:
            kwargs['meta'] = {'csrf': False}
        super(SearchForm, self).__init__(*args, **kwargs)