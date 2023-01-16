from flask import Blueprint, render_template, request
from websiteNPMINE.models import Compounds, Accounts
from websiteNPMINE import db

main = Blueprint('main', __name__)

@main.route('/')
@main.route("/home")
def home():
    return render_template("index.html")

@main.route('/api/data')
def data():
    query = Compounds.query

    # search filter
    search = request.args.get('search')
    if search:
        query = query.filter(db.or_(
            Compounds.id_comp.like(f'%{search}%'),
            Compounds.smiles.like(f'%{search}%')
        ))
    total = query.count()

    # sorting
    sort = request.args.get('sort')
    if sort:
        order = []
        for s in sort.split(','):
            direction = s[0]
            name = s[1:]
            if name not in ['id_comp', 'smiles', 'inchikey', 'pubchem']:
                name = 'id_comp'
            col = getattr(Compounds, name)
            if direction == '-':
                col = col.desc()
            order.append(col)
        if order:
            query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int, default=-1)
    length = request.args.get('length', type=int, default=-1)
    if start != -1 and length != -1:
        query = query.offset(start).limit(length)

    # response
    return {
        'data': [compounds.to_dict() for compounds in query],
        'total': total,
    }