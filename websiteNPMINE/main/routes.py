from flask import Blueprint, render_template
from websiteNPMINE.models import Compounds

main = Blueprint('main', __name__)

@main.route('/')
@main.route("/home")
def home():
    compounds = Compounds.query.all()
    return render_template("index.html")