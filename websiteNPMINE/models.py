from . import db, login_manager
from flask_login import UserMixin
from itsdangerous import TimedSerializer as Serializer
from flask import current_app

@login_manager.user_loader
def load_user(user_id):
    return Accounts.query.get(int(user_id))

class Accounts(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

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

    def __repr__(self):
        return f'<DOI: {self.doi}>'

doicomp = db.Table('doicomp', 
          db.Column('doi_id', db.Integer, db.ForeignKey('doi.id')),
          db.Column('compounds_id', db.Integer, db.ForeignKey('compounds.id'))
)

doitaxa = db.Table('doitaxa', 
          db.Column('doi_id', db.Integer, db.ForeignKey('doi.id')),
          db.Column('taxa_id', db.Integer, db.ForeignKey('taxa.id'))
)

class Compounds(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    journal = db.Column(db.String(5000))
    smiles = db.Column(db.String(5000))
    article_url = db.Column(db.String(500))
    inchi_key = db.Column(db.String(5000))
    exact_molecular_weight = db.Column(db.Float)
    pubchem_id = db.Column(db.String(50))
    inchi = db.Column(db.String(5000))
    source = db.Column(db.String(10))
    user_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    doicomp = db.relationship('DOI', secondary=doicomp, backref=db.backref('compounds', lazy='dynamic'))
    account = db.relationship("Accounts", backref="compounds")

    def __repr__(self):
        return f'Compounds: {self.id}'

    def to_dict(self):
        return {
            'id': self.id,
            'journal': self.journal,
            'smiles': self.smiles,
            'article_id': self.article_url,
            'inchi': self.inchi,
            'inchikey': self.inchi_key,
            'exactmolwt': self.exact_molecular_weight,
            'pubchem': self.pubchem_id,
            'source': self.source,
            'user_id': self.user_id
        }

class Taxa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article_url = db.Column(db.String(5000))
    verbatim = db.Column(db.String(5000))
    odds = db.Column(db.Float)
    datasourceid = db.Column(db.String(5000))
    taxonid = db.Column(db.Integer)
    classificationpath = db.Column(db.String(5000))
    classificationrank = db.Column(db.String(5000))
    matchtype = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    account = db.relationship("Accounts", backref="taxons")

    def __repr__(self):
        return f'<Taxa: {self.verbatim}, {self.article_url}, {self.classificationpath}, {self.classificationrank}, {self.user_id}>'



