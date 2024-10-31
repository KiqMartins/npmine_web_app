from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, FloatField, TextAreaField, FieldList, FormField
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


class DOIForm(FlaskForm):
    doi = StringField('DOI', validators=[Optional()])

class TaxaForm(FlaskForm):
    verbatim = StringField('Verbatim', validators=[Optional()])

class CompoundEditForm(FlaskForm):
    journal = StringField('Journal', validators=[Optional()])
    compound_name = StringField('Compound Name', validators=[Optional()])
    smiles = StringField('SMILES')
    exact_molecular_weight = FloatField('Exact Molecular Weight')
    class_results = TextAreaField('Class Results')
    superclass_results = TextAreaField('Superclass Results')
    pathway_results = TextAreaField('Pathway Results')
    isglycoside = StringField('Is Glycoside')
    pubchem_id = StringField('PubChem ID')
    inchi_key = StringField('InChI Key')
    inchi = StringField('InChI')
    article_url = StringField('Article URL')
    status = StringField('Status')

    dois = FieldList(FormField(DOIForm), min_entries=1)
    taxa = FieldList(FormField(TaxaForm), min_entries=1)

    submit = SubmitField('Update')