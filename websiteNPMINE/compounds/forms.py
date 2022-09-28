from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class CompoundForm(FlaskForm):
    smiles = StringField('SMILES', validators=[DataRequired()])
    inchi = StringField('InChI')
    inchikey = StringField('InChI Key')
    pubchem = StringField("Pubchem ID")
    user_id = StringField("User ID")
    submit = SubmitField("Submit")
