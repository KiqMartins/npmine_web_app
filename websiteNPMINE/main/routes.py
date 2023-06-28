from flask import Blueprint, render_template, request,jsonify, abort
from websiteNPMINE.models import Compounds, Accounts, doicomp, DOI
from websiteNPMINE import db

main = Blueprint('main', __name__)

@main.route('/')
@main.route("/home")
def home():
    return render_template("index.html")

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
    sort_columns = ['id', 'inchikey', 'pubchem']
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
    inchi_key = compound.inchi_key
    pubchem_id = compound.pubchem_id
    exact_mol_weight = compound.exact_molecular_weight

    return render_template('compound.html', compound_id=compound_id, inchi=inchi, inchi_key=inchi_key, pubchem_id=pubchem_id, exact_mol_weight=exact_mol_weight)
