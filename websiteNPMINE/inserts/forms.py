from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class CompoundForm(FlaskForm):
    smiles = StringField('SMILES', validators=[DataRequired()])
    inchi = StringField('InChI')
    inchikey = StringField('InChI Key')
    exactmolwt = StringField("Exact Molecular Weight")
    pubchem = StringField("Pubchem ID")
    source = StringField("Source")
    submit = SubmitField("Submit")
