from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User, Listing, Rating, Report
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object(Config)


db.init_app(app)
mail = Mail(app)

# Ensuring anyone trying to access @login_required routes without being logged
# in are redirected to login page.
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'error'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

    admins = [
        {'email': 'norton@gus.pittstate.edu', 'display_name': 'Nicholas', 'password': 'Norton123'},
        {'email': 'tsickles@gus.pittstate.edu', 'display_name': 'Travis', 'password': 'temporary_change123'},
    ]

    for admin_data in admins:
        if not User.query.filter_by(email=admin_data['email']).first():
            admin = User(
                email=admin_data['email'],
                display_name=admin_data['display_name'],
                is_admin=True,
                is_active=True,
                email_verified=True
            )
            admin.set_password(admin_data['password'])
            db.session.add(admin)
    db.session.commit()


# Authentication Routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    # This is a placeholder for form handling once we build those out
    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    # Again, this is a placeholder until forms.py is built
    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# Main Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/listings')
def listings():
    # Placeholder to add search/filter logic here later
    all_listings = Listing.query.filter_by(status='active').order_by(Listing.created_at.desc()).all()
    return render_template('listings/index.html', listings=all_listings)

@app.route('/listings/new', methods=['GET', 'POST'])
@login_required
def new_listing():
    # Placeholder for form handling
    return render_template('listings/new.html')

@app.route('/listings/<int:listing_id>')
def listing_detail(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    return render_template('listings/detail.html', listing=listing)

@app.route('/listings/<int:listing_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    # checking to make sure it's either admin or current user before edits are permitted
    if listing.seller_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to edit this listing.', 'error')
        return redirect(url_for('listings'))
    # Form handling logic will go here later
    return render_template('listings/edit.html', listing=listing)

@app.route('/listings/<int:listing_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    # Checking to make sure it's either admin or current user wishing to delete listing before doing so
    if listing.seller_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to delete this listing.', 'error')
        return redirect(url_for('listings'))
    db.session.delete(listing)
    db.session.commit()
    flash('Listing deleted.', 'info')
    return redirect(url_for('listings'))


# Route for User Profile
@app.route('/users/<int:user_id>')
def profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('users/profile.html', user=user)


# Admin Routes
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access Denied.', 'error')
        return redirect(url_for('index'))
    users = User.query.order_by(User.created_at.desc()).all()
    reports = Report.query.filter_by(resolved=False).all()
    return render_template('admin/dashboard.html', users=users, reports=reports)

@app.route('/admin/users/<int:user_id>/suspend', methods=['POST'])
@login_required
def suspend_user(user_id):
    if not current_user.is_admin:
        flash('Access Denied.', 'error')
        return redirect(url_for('index'))
    user = User.query.get_or_404(user_id)
    user.is_active = False
    db.session.commit()
    flash(f'{user.display_name} has been suspended.', 'info')
    return redirect(url_for('admin_dashboard'))

if __name__ == "__main__":
    app.run(debug = True, host = "0.0.0.0", port = 3000)