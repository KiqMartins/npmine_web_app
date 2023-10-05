from . import db, login_manager
from flask_login import UserMixin
from itsdangerous import TimedSerializer as Serializer
from flask import current_app
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return Accounts.query.get(int(user_id))

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f'<Role: {self.name}>'

class Accounts(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False, default=2)  # Set default to "editor"
    role = db.relationship('Role', backref=db.backref('accounts', lazy='dynamic'))
    
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Accounts.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class DOI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doi = db.Column(db.String(150), unique=True)

    compounds = db.relationship('Compounds', secondary='doicomp', back_populates='dois')
    taxa = db.relationship('Taxa', secondary='doitaxa', back_populates='dois')

    def __repr__(self):
        return f'<DOI: {self.doi}>'

class Compounds(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    journal = db.Column(db.String(5000))
    compound_name = db.Column(db.String(5000))
    compound_image = db.Column(db.String(5000))
    dois = db.relationship('DOI', secondary='doicomp', back_populates='compounds')
    smiles = db.Column(db.String(5000))
    article_url = db.Column(db.String(500))
    inchi_key = db.Column(db.String(5000))
    exact_molecular_weight = db.Column(db.Float)
    pubchem_id = db.Column(db.String(50))
    inchi = db.Column(db.String(5000))
    source = db.Column(db.String(10))
    user_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    
    # Add created_at field to track compound creation date
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    account = db.relationship("Accounts", backref="compounds")

    def __repr__(self):
        return f'Compounds: {self.id}'

    def to_dict(self):
        return {
            'id': self.id,
            'journal': self.journal,
            'compound_name': self.compound_name,
            'compound_image': self.compound_image,
            'smiles': self.smiles,
            'article_id': self.article_url,
            'inchi': self.inchi,
            'inchikey': self.inchi_key,
            'exactmolwt': self.exact_molecular_weight,
            'pubchem': self.pubchem_id,
            'source': self.source,
            'user_id': self.user_id,
        }


class Taxa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article_url = db.Column(db.String(5000))
    verbatim = db.Column(db.String(5000))
    odds = db.Column(db.Float)
    dois = db.relationship('DOI', secondary='doitaxa', back_populates='taxa')
    datasourceid = db.Column(db.String(5000))
    taxonid = db.Column(db.Integer)
    classificationpath = db.Column(db.String(5000))
    classificationrank = db.Column(db.String(5000))
    matchtype = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    
    # Add created_at field to track taxon creation date
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    account = db.relationship("Accounts", backref="taxons")

    def __repr__(self):
        return f'<Taxa: {self.verbatim}, {self.article_url}, {self.classificationpath}, {self.classificationrank}, {self.user_id}>'

doicomp = db.Table(
    'doicomp',
    db.Column('doi_id', db.Integer, db.ForeignKey('doi.id'), primary_key=True),
    db.Column('compound_id', db.Integer, db.ForeignKey('compounds.id'), primary_key=True)
)

doitaxa = db.Table(
    'doitaxa',
    db.Column('doi_id', db.Integer, db.ForeignKey('doi.id'), primary_key=True),
    db.Column('taxon_id', db.Integer, db.ForeignKey('taxa.id'), primary_key=True)
)