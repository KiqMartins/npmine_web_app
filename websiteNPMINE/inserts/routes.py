from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required
from websiteNPMINE.inserts.forms import CompoundForm
from websiteNPMINE.models import Compounds, doi, Accounts

inserts = Blueprint('inserts', __name__)

@inserts.route("/new_compound", methods=["GET", "POST"])
@login_required
def new_compound():
    form = CompoundForm()
    if form.validate_on_submit():
        compound = Compounds(smiles=form.smiles.data, inchi=form.inchi.data, inchikey=form.inchikey.data, exactmolwt=form.exactmolwt.data,
                            pubchem=form.pubchem.data, source=form.source.data, )
        flash("You have inserted a new compound!", "success")
        return redirect(url_for("main.home"))
    return render_template("new_compound.html", title = 'New Compound', form=form)
