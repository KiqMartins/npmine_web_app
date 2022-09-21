from flask import Blueprint, render_template
from websiteNPMINE.models import Compounds
from websiteNPMINE import db

main = Blueprint('main', __name__)

@main.route('/')
@main.route("/home")
def home():
    compounds = db.session.query(Compounds).all()
    #compounds = Compounds.query.with_entities(Compounds.smiles)
    return render_template("index.html", compounds=compounds)