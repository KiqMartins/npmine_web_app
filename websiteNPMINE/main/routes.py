from flask import Blueprint, render_template, request, jsonify, abort, redirect, url_for,flash
from flask_login import login_required, current_user, login_user, logout_user
from websiteNPMINE.models import Compounds, DOI, Accounts, Taxa, doicomp, doitaxa
from websiteNPMINE import db
import requests
from sqlalchemy import or_
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm import aliased
import collections

main = Blueprint('main', __name__)

@main.route('/')
@main.route("/home")
def home():
    logged_in = current_user.is_authenticated  # Check if the user is logged in
    return render_template("index.html", logged_in=logged_in)
    
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
        compound_data['compound_name'] = compound.compound_name
        compound_data['compound_image'] = url_for('static', filename=f'{compound.compound_image}') if compound.compound_image else ''
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

    # Get the articles associated with the compound using the `dois` relationship
    articles = [doi.doi.replace('<DOI: ', '').replace('>', '') for doi in compound.dois]

    # Pass all the required information from the compound object and the articles to the template
    return render_template('compound.html', compound=compound, articles=articles)

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


@main.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    print(f"Query: {query}")

    # Query Compounds, DOI, and Taxa
    compounds = Compounds.query.filter(
        or_(
            Compounds.journal.ilike(f'%{query}%'),
            Compounds.inchi_key.ilike(f'%{query}%'),
            Compounds.article_url.ilike(f'%{query}%')  # Add article_url search criteria
        )
    ).all()

    taxa = Taxa.query.filter(
        or_(
            Taxa.verbatim.ilike(f'%{query}%'),
            Taxa.article_url.ilike(f'%{query}%')  # Add article_url search criteria
        )
    ).all()

    # Initialize defaultdicts to store related compounds and taxa
    related_compounds = collections.defaultdict(list)
    related_taxa = collections.defaultdict(list)

    # Query DOI
    dois = DOI.query.filter(DOI.doi.ilike(f'%{query}%')).all()

    # Query related compounds and taxa based on DOI
    for doi in dois:
        # Create aliases for the association tables
        doicomp_alias = aliased(doicomp)
        doitaxa_alias = aliased(doitaxa)
        
        # Query related compounds
        compound_query = Compounds.query.join(doicomp_alias).filter(doicomp_alias.c.doi_id == doi.id)
        related_compounds[doi.id].extend(compound_query.all())

        # Query related taxa
        taxa_query = Taxa.query.join(doitaxa_alias).filter(doitaxa_alias.c.doi_id == doi.id)
        related_taxa[doi.id].extend(taxa_query.all())

    return render_template(
        'search_results.html',
        compounds=compounds,
        taxa=taxa,
        related_compounds=related_compounds,
        related_taxa=related_taxa,
        query=query
    )




