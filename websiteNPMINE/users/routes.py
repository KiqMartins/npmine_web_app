from flask import Blueprint, render_template, request, flash, redirect, url_for
from websiteNPMINE.models import Accounts, Role
from werkzeug.security import generate_password_hash, check_password_hash
from websiteNPMINE import db, bcrypt
from flask_login import login_user, login_required, logout_user, current_user
from .forms import RegistrationForm, LoginForm


users = Blueprint('users', __name__)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Accounts.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form, user=current_user)


@users.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        # You can set the default role_id for new users here (1 for User, 2 for Editor, 3 for Admin)
        # Change the value according to your needs
        default_role_id = 3  # For example, setting the default role to User
        
        user = Accounts(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            role_id=default_role_id  # Set the default role_id
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('signup.html', title='Register', form=form, user=current_user)

@users.route('/admin_panel', methods=['GET', 'POST'])
@login_required
def admin_panel():
    print("Current user:", current_user)  # Check if the current user object is loaded
    print("Current user role:", current_user.role)  # Check if the role object is loaded

    if current_user.role.name != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.home'))

    users = Accounts.query.all()
    roles = Role.query.all()

    if request.method == 'POST':
        try:
            for user in users:
                role_id = int(request.form.get(f'user_role_{user.id}'))
                user.role_id = role_id

            db.session.commit()
            flash('User roles updated successfully.', 'success')
        except Exception as e:
            print("Error updating user roles:", e)  # Print the error message
            db.session.rollback()  # Rollback changes in case of error

        return redirect(url_for('users.admin_panel'))

    return render_template('admin_panel.html', users=users, roles=roles, logged_in=current_user.is_authenticated)

