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
from PIL import Image


compounds = Blueprint('compounds', __name__)

def save_compound_image(compound_id, smiles):
    # Generate the filename
    filename = f"{compound_id}.png"
    relative_path = os.path.join('compound_images', filename)
    
    # Normalize the path and replace backslashes with forward slashes
    relative_path = os.path.normpath(relative_path).replace("\\", "/")

    # Define the full path to save the image
    full_path = os.path.join(current_app.root_path, 'static', relative_path)

    # Check if the image already exists; if not, generate it
    if not os.path.exists(full_path):
        mol = Chem.MolFromSmiles(smiles)
        img = Draw.MolToImage(mol, size=(200, 200))
        img.save(full_path)

    # Return the relative path to be stored in the database
    return relative_path

@compounds.route('/new_compound', methods=['GET', 'POST'])
@login_required
def registerCompound():
    logged_in = current_user.is_authenticated
    form = CompoundForm()

    if form.validate_on_submit():
        doi = form.doi.data

        # Ensure DOI is provided
        if not doi:
            flash('DOI Link is required', 'error')
            return redirect(request.url)

        # Check if DOI exists in the DOI table
        existing_doi = DOI.query.filter_by(doi=doi).first()

        if not existing_doi:
            # If DOI does not exist, create a new DOI object
            new_doi = DOI(doi=doi)
            db.session.add(new_doi)
            db.session.commit()
            existing_doi = new_doi
        else:
            flash('DOI already in database!', 'info')

        compound_blocks = request.form.getlist('inchikey')  # This should return all inchikey fields
        for i, inchikey in enumerate(compound_blocks):
            genus = request.form.getlist('genus')[i]
            species = request.form.getlist('species')[i]

            # Validate InChI Key
            if not inchikey:
                flash(f'InChI Key is required for Compound {i + 1}', 'error')
                continue  # Skip this compound if InChI Key is missing

            # Check if InChI Key exists
            existing_compound = Compounds.query.filter_by(inchi_key=inchikey).first()

            if existing_compound:
                if existing_doi in existing_compound.dois:
                    flash(f'DOI and InChI Key already in database for Compound {i + 1}!', 'info')
                    continue  # Skip this compound as both DOI and InChI Key are already present
            else:
                # Fetch compound data from PubChem
                pubchem_data = fetch_pubchem_data(inchikey)
                if not pubchem_data:
                    flash(f'Failed to fetch data from PubChem for Compound {i + 1}', 'error')
                    continue

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

                # Associate the compound with the DOI
                compound.dois.append(existing_doi)
                db.session.commit()

                # Save compound image
                smiles = pubchem_data.get('smiles')
                img_path = save_compound_image(compound.id, smiles)
                if img_path:
                    # Update compound image path in the database
                    compound.compound_image = img_path
                    db.session.commit()

            # Check if species exists for the given genus
            existing_taxon = Taxa.query.filter_by(verbatim=f"{genus} {species}").first()
            if not existing_taxon:
                # Create Taxa object if genus is provided
                if genus:
                    taxon = Taxa(
                        article_url=doi,
                        verbatim=f"{genus} {species}",
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

                    # Associate the taxa with the DOI
                    taxon.dois.append(existing_doi)
                    db.session.commit()

        flash('Compounds added successfully!', 'success')
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

