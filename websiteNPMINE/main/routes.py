from flask import Blueprint, render_template, request, jsonify, abort, redirect, url_for,flash
from flask_login import login_required, current_user, login_user, logout_user
from websiteNPMINE.models import Compounds, DOI, Accounts, Taxa
from websiteNPMINE import db
import requests

main = Blueprint('main', __name__)

@main.route('/')
@main.route("/home")
def home():
    logged_in = current_user.is_authenticated  # Check if the user is logged in
    return render_template("index.html", logged_in=logged_in)

def fetch_structure_image(inchikey):
    cactus_api_url = f"https://cactus.nci.nih.gov/chemical/structure/{inchikey}/image"
    response = requests.get(cactus_api_url)
    
    if response.status_code == 200:
        return response.url
    else:
        return None
    
@main.route('/api/data')
def data():
    # Pagination parameters
    start = request.args.get('start', type=int, default=0)
    length = request.args.get('length', type=int, default=10)

    # Search filter
    search = request.args.get('search', '').strip()
    search_query = db.or_(
        Compounds.id.like(f'%{search}%'),
        Compounds.smiles.like(f'%{search}%')
    )

    # Sorting
    sort = request.args.get('sort', '')
    sort_columns = ['id', 'inchi', 'pubchem']
    order = []
    for field in sort.split(','):
        direction = '-' if field.startswith('-') else ''
        name = field.lstrip('-')
        if name not in sort_columns:
            name = 'id'
        col = getattr(Compounds, name)
        order.append(getattr(col, direction + 'asc')())
    if not order:
        order.append(Compounds.id.asc())

    # Fetch data
    query = Compounds.query
    if search:
        query = query.filter(search_query)
    total = query.count()
    query = query.order_by(*order).offset(start).limit(length)
    compounds = query.all()

    # Prepare response data
    data = []
    for compound in compounds:
        compound_data = compound.to_dict()
        compound_data['id'] = compound.id
        inchi = compound.inchi
        inchikey = compound.inchi_key

        # Append edit and delete buttons based on authentication status
        if current_user.is_authenticated:
            edit_button = f'<a href="/compound/{compound.id}/edit">Edit</a>'
            delete_button = f'<a href="/compound/{compound.id}/delete" onclick="return confirm(\'Are you sure you want to delete this compound?\')">Delete</a>'
            compound_data['Edit'] = edit_button
            compound_data['Delete'] = delete_button

        data.append(compound_data)

    return jsonify({'data': data, 'total': total})

@main.route('/compound/<int:compound_id>')
def compound(compound_id):
    compound = Compounds.query.get(compound_id)
    if not compound:
        abort(404)

    # Fetch the required information from the compound object
    compound_id = compound.id
    inchi = compound.inchi
    pubchem_id = compound.pubchem_id
    inchi_key = compound.inchi_key
    exact_mol_weight = compound.exact_molecular_weight

    # Get the articles associated with the compound using the `dois` relationship
    articles = [doi.doi.replace('<DOI: ', '').replace('>', '') for doi in compound.dois]

    # Pass the variables to the template
    return render_template(
        'compound.html',
        compound_id=compound_id,
        inchi=inchi,
        inchi_key=inchi_key,
        pubchem_id=pubchem_id,
        exact_mol_weight=exact_mol_weight,
        articles=articles
    )

@main.route('/compound/<int:compound_id>/delete', methods=['POST'])
@login_required
def delete_compound(compound_id):
    # Find the compound to delete
    compound = Compounds.query.get_or_404(compound_id)

    # Check if the current user has permission to delete the compound
    if not current_user.role_id == 1 and current_user.id != compound.user_id:
        flash("You don't have permission to delete this compound.", "error")
        return redirect(url_for('main.home'))

    try:
        # Delete the compound from the database
        db.session.delete(compound)
        db.session.commit()
        flash("Compound deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting the compound.", "error")

    return redirect(url_for('main.home'))




