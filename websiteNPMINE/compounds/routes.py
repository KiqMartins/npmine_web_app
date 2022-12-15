from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from websiteNPMINE.compounds.forms import CompoundForm
from websiteNPMINE.models import Compounds
from websiteNPMINE import db
import os
import json
import requests
from rdkit import Chem
from websiteNPMINE.compounds.utils import *

compounds = Blueprint('inserts', __name__)

#@compounds.route("/new_compound", methods=["GET", "POST"])
#@login_required
#def new_compound():
    #form = CompoundForm()
    #if form.validate_on_submit():
        #compound = Compounds(smiles=form.smiles.data, inchi=form.inchi.data, inchikey=form.inchikey.data, exactmolwt=form.exactmolwt.data,
                            #pubchem=form.pubchem.data, source=form.source.data)
        #db.session.add(compound)
        #db.session.commit()
        #flash("You have inserted a new compound!", "success")
        #return redirect(url_for("main.home"))
    #return render_template("new_compound.html", title = 'New Compound', form=form)

@compounds.route('/new_compound', methods=['GET', 'POST'])
@login_required
def registerCompound():
    form = CompoundForm()
    if form.validate_on_submit():
        if form.inchikey.data=='':
            inchikey = Chem.InchiToInchiKey(form.inchi.data)
        else:
            inchikey = form.inchikey.data

        #check inchikey
        compoundToView = db.session.query(Compounds).filter_by(inchikey=inchikey).all()
        if len(compoundToView):
            flash('Compound %s already registered' % compoundToView[0].inchikey, 'error')
            return redirect(url_for('main.home'))

        d = cpd2prop(inchikey)
        if not len(d):
            compound = Compounds(inchi=form.inchi.data,
                                inchikey=inchikey,
                                smiles=form.smiles.data,
                                pubchem=form.pubchem.data,
                                user_id=current_user.id)
        else:
            if 'CID' in d.keys():
                pubchem = '%s' % d['CID']
                d.pop('CID')
            props = json.dumps(d)
            compound = Compounds(inchi=form.inchi.data,
                                inchikey=inchikey,
                                smiles=form.smiles.data,
                                pubchem=pubchem,
                                user_id=current_user.id)
        db.session.add(compound)
        db.session.commit()
        flash('Congratulations, you registered a new compound!')
        return redirect(url_for('main.home'))
    return render_template('new_compound.html',
                           form=form)

@compounds.route('/home/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def editCompound(id):
    return render_template('editCompound.html')

