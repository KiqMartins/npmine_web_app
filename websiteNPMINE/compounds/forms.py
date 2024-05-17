from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Optional

class CompoundForm(FlaskForm):
    doi = StringField('DOI Link', validators=[DataRequired()])
    inchikey = StringField('InChI Key', validators=[DataRequired()])
    genus = StringField('Genus', validators=[Optional()])
    origin_type = SelectField('Origin Type', choices=[('Bacteria', 'Bacteria'), ('Fungi', 'Fungi')])
    species = StringField('Species', default='sp', validators=[Optional()])
    submit = SubmitField('Submit')

