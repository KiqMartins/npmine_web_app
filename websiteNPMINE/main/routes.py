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
    search_query = or_(
        Compounds.id.like(f'%{search}%'),
        Compounds.compound_name.like(f'%{search}%')
    )

    # Sorting
    sort = request.args.get('sort', '')
    sort_columns = ['id', 'compound_name']  # Add more columns if needed
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
    query = Compounds.query.filter_by(status='public')
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
        compound_data['compound_image'] = url_for('static', filename=compound.compound_image) if compound.compound_image else ''

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
    logged_in = current_user.is_authenticated  # Check if the user is logged in
    if not compound:
        abort(404)

    # Get the article URLs and their corresponding IDs associated with the compound
    articles = [(doi.id, doi.doi) for doi in compound.dois]

    # Use NPclassifier API
    #api_url = f'https://npclassifier.gnps2.org/classify?smiles={compound.smiles}'
    #resposta_api = requests.get(api_url).json()

    # Pass all the required information from the compound object and the articles to the template
    return render_template('compound.html', logged_in=logged_in, compound=compound, articles=articles)


@main.route('/article/<int:article_id>')
def article(article_id):
    logged_in = current_user.is_authenticated  # Check if the user is logged in
    # Fetch article from the DOI table based on the article_id
    doi_record = DOI.query.get(article_id)
    if not doi_record:
        abort(404)
    
     # Retrieve the compounds associated with the article
    compounds = doi_record.compounds

    if compounds:
        first_compound = compounds[0]
        journal_name = first_compound.journal
        article_url = first_compound.article_url
        created_at = first_compound.created_at
    else:
        journal_name = None
        article_url = None
        created_at = None

    # Retrieve related compound names
    related_compound_names = set()
    for doi_compound in compounds:
        related_compounds = Compounds.query.join(doicomp).filter(doicomp.columns.doi_id == article_id).all()
        for compound in related_compounds:
            related_compound_names.add(compound.compound_name)
    
    cleaned_related_compound_names = [name for name in related_compound_names if name is not None]

    # Retrieve compound IDs for the related compound names
    compound_name_to_id_map = {}  # Create an empty dictionary
    for compound_name in cleaned_related_compound_names:
        compound = Compounds.query.filter_by(compound_name=compound_name).first()
        if compound:
            compound_name_to_id_map[compound_name] = compound.id

    # Retrieve matches in the taxa table based on the article_url
    matching_taxa = Taxa.query.filter_by(article_url=article_url).all()

    # Retrieve the list of verbatim values associated with the matches
    verbatim_values = [taxon.verbatim for taxon in matching_taxa]

    # Pass the article to the template
    return render_template('article.html', doi_record=doi_record, journal_name=journal_name, article_url=article_url, created_at=created_at, related_compound_names=cleaned_related_compound_names, logged_in=logged_in, verbatim_values=verbatim_values, compound_name_to_id_map=compound_name_to_id_map)

@main.route('/profile/<int:profile_id>')
@login_required
def profile(profile_id):
    logged_in = current_user.is_authenticated
    # Fetch the user's profile information based on the profile_id
    user = Accounts.query.get(profile_id)
    if not user:
        abort(404)  # User not found

    # Fetch both public and private compounds inserted by the user
    public_compounds = Compounds.query.filter_by(user_id=profile_id, status='public').all()
    private_compounds = Compounds.query.filter_by(user_id=profile_id, status='private').all()

    # Pass the public and private compounds to the template
    return render_template('profile.html', logged_in=logged_in, user=user, public_compounds=public_compounds, private_compounds=private_compounds)

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

@main.route('/toggle_privacy/<int:compound_id>', methods=['POST'])
@login_required
def toggle_privacy(compound_id):
    compound = Compounds.query.get_or_404(compound_id)

    # Check if the current user has permission to change the privacy status
    if current_user.id != compound.user_id:
        abort(403)  # Forbidden

    # Toggle the privacy status
    if compound.status == 'private':
        compound.status = 'public'
        flash(f"Compound '{compound.compound_name}' is now public.", "success")
    else:
        compound.status = 'private'
        flash(f"Compound '{compound.compound_name}' is now private.", "success")

    # Commit the changes to the database
    db.session.commit()

    # Redirect back to the profile page
    return redirect(url_for('main.profile', profile_id=current_user.id))




