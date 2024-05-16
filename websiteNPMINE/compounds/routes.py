from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from websiteNPMINE.compounds.forms import CompoundForm
from websiteNPMINE.models import Compounds,DOI,Taxa
from websiteNPMINE import db
import os
import json
import requests
from websiteNPMINE.compounds.utils import *
from rdkit import Chem
from rdkit.Chem import Draw
import pubchempy as pcp


compounds = Blueprint('compounds', __name__)

def save_compound_image(compound_id, smiles):
    try:
        # Create directory if it doesn't exist
        image_dir = os.path.join(current_app.root_path, 'static', 'compound_images')
        os.makedirs(image_dir, exist_ok=True)

        # Save compound image
        img_path = os.path.join(image_dir, f'{compound_id}.png')
        mol = Chem.MolFromSmiles(smiles)
        if mol:
            Draw.MolToFile(mol, img_path)
            return img_path
    except Exception as e:
        print(f"Error saving compound image: {e}")

@compounds.route('/new_compound', methods=['GET', 'POST'])
@login_required
def registerCompound():
    logged_in = current_user.is_authenticated
    form = CompoundForm()
    
    if form.validate_on_submit():
        doi = form.doi.data
        inchikey = form.inchikey.data
        genus = form.genus.data
        origin_type = form.origin_type.data
        species = form.species.data
        
        # Check if DOI and InChI Key are provided
        if not doi:
            flash('DOI Link is required', 'error')
            return redirect(request.url)
        if not inchikey:
            flash('InChI Key is required', 'error')
            return redirect(request.url)
        
        # Fetch compound data from PubChem
        pubchem_data = fetch_pubchem_data(inchikey)
        if not pubchem_data:
            flash('Failed to fetch data from PubChem', 'error')
            return redirect(request.url)
        
        # Create Compounds object
        compound = Compounds(
            journal=None,
            compound_name=pubchem_data['compound_name'],
            smiles=pubchem_data['smiles'],
            article_url=doi,
            inchi_key=inchikey,
            exact_molecular_weight=pubchem_data['exact_molecular_weight'],
            class_results=None,
            superclass_results=None,
            pathway_results=None,
            isglycoside=None,
            pubchem_id=pubchem_data['pubchem_id'],
            inchi=pubchem_data['inchi'],
            source='NPMine',
            user_id=current_user.id
        )
        db.session.add(compound)
        db.session.commit()

        # Fetch PubChem data and get smiles
        pubchem_data = fetch_pubchem_data(inchikey)
        smiles = pubchem_data.get('smiles')
        
        # Save compound image
        img_path = save_compound_image(compound.id, smiles)
        if img_path:
            # Update compound image path in database
            compound = Compounds.query.get(compound.id)
            compound.compound_image = img_path
            db.session.commit()
        
        # Create Taxa object if genus is provided
        if genus:
            verbatim = f"{genus} {species}"
            taxon = Taxa(
                article_url=doi,
                verbatim=verbatim,
                odds=None,
                datasourceid=None,
                taxonid=None,
                classificationpath=None,
                classificationrank=None,
                matchtype=None,
                user_id=current_user.id
            )
            db.session.add(taxon)
            db.session.commit()
        
        flash('Compound added successfully!', 'success')
        return redirect(url_for('compounds.registerCompound'))
    
    # Display validation errors
    for error in form.errors.values():
        flash(error[0], 'error')
    
    return render_template('new_compound.html', form=form, logged_in=logged_in)

def fetch_pubchem_data(inchikey):
    try:
        # Search for the compound using the InChI Key
        compound = pcp.get_compounds(inchikey, 'inchikey')[0]
        return {
            'compound_name': compound.synonyms[0] if compound.synonyms else None,
            'smiles': compound.canonical_smiles,
            'inchi': compound.inchi,
            'exact_molecular_weight': compound.molecular_weight,
            'pubchem_id': compound.cid
        }
    except pcp.PubChemHTTPError as e:
        print(f"PubChem HTTP Error: {e}")
        return {}
    except pcp.PubChemPyError as e:
        print(f"PubChemPy Error: {e}")
        return {}

@compounds.route('/home/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def editCompound(id):
    return render_template('editCompound.html')

