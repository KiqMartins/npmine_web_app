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

class Compounds(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_comp = db.Column(db.String(50))
    smiles = db.Column(db.String(5000))
    inchi = db.Column(db.String(5000))
    inchikey = db.Column(db.String(5000))
    exactmolwt = db.Column(db.Integer)
    pubchem = db.Column(db.Integer)
    source = db.Column(db.String(10))
    user_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    account = db.relationship("Accounts", backref="user_id_comp")

    def __repr__(self):
        return f'Compounds: {self.id_comp}'

    def to_dict(self):
        return {
            'id': self.id,
            'id_comp': self.id_comp,
            'smiles': self.smiles,
            'inchi': self.inchi,
            'inchikey': self.inchikey,
            'exactmolwt': self.exactmolwt,
            'pubchem': self.pubchem,
            'source': self.source,
            'user_id': self.user_id
        }

class Taxa(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     verbatim = db.Column(db.String(150))
     classificationPath = db.Column(db.String(150))
     classificationRank = db.Column(db.String(150))
     user_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
     account = db.relationship("Accounts", backref="user_id_taxa")

     def __repr__(self):
        return f'<Taxa: {self.verbatim}, {self.classificationPath}, {self.classificationRank}, {self.user_id}>'

class doi(db.Model):
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

