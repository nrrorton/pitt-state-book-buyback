import os
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from config import Config
from models import db, User, Listing, Rating, Report
from forms import RegistrationForm, LoginForm, ListingForm, ReportForm, RatingForm
from flask_mail import Mail
from werkzeug.utils import secure_filename

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

app = Flask(__name__)
app.config.from_object(Config)


db.init_app(app)
mail = Mail(app)
jwt = JWTManager(app)

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
        {'email': 'norton@gus.pittstate.edu', 'phone_number': '3165186906', 'display_name': 'Nicholas', 'password': 'Norton123'},
        {'email': 'tsickles@gus.pittstate.edu', 'phone_number': '4797159096', 'display_name': 'Travis', 'password': 'temporary_change123'},
    ]

    for admin_data in admins:
        if not User.query.filter_by(email=admin_data['email']).first():
            admin = User(
                email=admin_data['email'],
                phone_number=admin_data['phone_number'],
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
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            display_name=form.display_name.data,
            phone_number=form.phone_number.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('auth/register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account is suspended. Please contact an admin.', 'error')
                return redirect(url_for('login'))
            login_user(user)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'error')
    return render_template('auth/login.html', form=form)

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
    query = Listing.query.filter_by(status='active')
    
    # Get parameters from url 
    course_code = request.args.get('course_code')
    professor = request.args.get('professor')
    search_term = request.args.get('search')

    # All queries are case insensitive
    # Find listings matching course_code 
    if course_code:
        query = query.filter(Listing.course_code.ilike(f'%{course_code}%'))
    if professor:
        query = query.filter(Listing.professor.ilike(f'%{professor}%'))
    # If a matching word is found anywhere in the title, author, or description section, return the books
    if search_term:
        query = query.filter(db.or_(
            Listing.title.ilike(f'%{search_term}%'),
            Listing.author.ilike(f'%{search_term}%'),
            Listing.description.ilike(f'%{search_term}%')
        ))

    all_listings = query.order_by(Listing.created_at.desc()).all()
    return render_template('listings/index.html', listings=all_listings)

@app.route('/listings/new', methods=['GET', 'POST'])
@login_required
def new_listing():
    form = ListingForm()
    if form.validate_on_submit():
        image_filename = None
        if form.image.data and allowed_file(form.image.data.filename):
            filename = secure_filename(form.image.data.filename)
            unique_filename = f"{current_user.id}_{filename}"
            form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            image_filename = unique_filename

        listing = Listing(
            title=form.title.data,
            author=form.author.data,
            edition=form.edition.data,
            condition=form.condition.data,
            price=float(form.price.data),
            course_code=form.course_code.data,
            professor=form.professor.data,
            description=form.description.data,
            image_filename=image_filename,
            seller_id=current_user.id
        )
        db.session.add(listing)
        db.session.commit()
        flash('Your book has been listed!', 'success')
        return redirect(url_for('listings'))
    return render_template('listings/new.html', form=form, title='New Listing')

@app.route('/listings/<int:listing_id>')
def listing_detail(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    form = RatingForm()
    already_rated = False
    if current_user.is_authenticated:
        already_rated = Rating.query.filter_by(
            listing_id=listing_id,
            reviewer_id=current_user.id
        ).first() is not None
    return render_template('listings/detail.html', listing=listing, form=form, already_rated=already_rated)

@app.route('/listings/<int:listing_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)

    # checking to make sure it's either admin or current user before edits are permitted
    if listing.seller_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to edit this listing.', 'error')
        return redirect(url_for('listing_detail', listing_id=listing.id))
    
    form = ListingForm(obj=listing)
    if form.validate_on_submit():
        listing.title = form.title.data
        listing.author = form.author.data
        listing.edition = form.edition.data
        listing.condition = form.condition.data
        listing.price = float(form.price.data)
        listing.course_code = form.course_code.data
        listing.professor = form.professor.data
        listing.description = form.description.data

        # We need to verify that a photo exists before replacement can occur
        if form.image.data and allowed_file(form.image.data.filename):
            if listing.image_filename:
                old_path = os.path.join(app.config['UPLOAD_FOLDER'], listing.image_filename)
                if os.path.exists(old_path):
                    os.remove(old_path)
            filename = secure_filename(form.image.data.filename)
            unique_filename = f"{current_user.id}_{filename}"
            form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            listing.image_filename = unique_filename

        db.session.commit()
        flash('Listing updated successfully!', 'success')
        return redirect(url_for('listing_detail', listing_id=listing.id))
    
    return render_template('listings/edit.html', form=form, listing=listing)

@app.route('/listings/<int:listing_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)

    # Checking to make sure it's either admin or current user wishing to delete listing before doing so
    if listing.seller_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to delete this listing.', 'error')
        return redirect(url_for('listings'))
    
    # Cleaning up the image file if it exists
    if listing.image_filename:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], listing.image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(listing)
    db.session.commit()
    flash('Listing deleted.', 'info')
    return redirect(url_for('listings'))

@app.route('/listings/<int:listing_id>/report', methods=['GET', 'POST'])
@login_required
def report_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)

    if listing.seller_id == current_user.id:
        flash('You cannot report your own listing.', 'error')
        return redirect(url_for('listing_ddetail', listing_id=listing.id))
    
    form = ReportForm()
    if form.validate_on_submit():
        report = Report(
            reporter_id=current_user.id,
            listing_id=listing.id,
            reason=form.reason.data
        )
        db.session.add(report)
        db.session.commit()
        flash('Your report has been submitted. We will review it shortly.', 'success')
        return redirect(url_for('listing_detail', listing_id=listing.id))
    return render_template('listings/report.html', form=form, listing=listing)

@app.route('/listings/<int:listing_id>/rate', methods=['POST'])
@login_required
def rate_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)

    if listing.seller_id == current_user.id:
        flash("You can't rate your own listing.", 'error')
        return redirect(url_for('listing_detail', listing_id=listing_id))
    
    existing = Rating.query.filter_by(listing_id=listing_id, reviewer_id=current_user.id).first()
    if existing:
        flash('You have already rated this listing.', 'error')
        return redirect(url_for('listing_detail', listing_id=listing_id))
    
    score = int(request.form.get('score'))
    comment = request.form.get('comment', '')

    rating = Rating(
        listing_id=listing_id,
        reviewer_id=current_user.id,
        seller_id=listing.seller_id,
        score=score,
        comment=comment
    )

    db.session.add(rating)
    db.session.commit()
    flash('Rating submitted!', 'success')
    return redirect(url_for('listing_detail', listing_id=listing_id))

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
    active_listings = Listing.query.filter_by(status='active').count()
    return render_template('admin/dashboard.html', users=users, reports=reports, active_listings=active_listings)

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

@app.route('/admin/reports/<int:report_id>/resolve', methods=['POST'])
@login_required
def resolve_report(report_id):
    if not current_user.is_admin:
        flash('Access Denied.', 'error')
        return redirect(url_for('index'))
    report = Report.query.get_or_404(report_id)
    report.resolved = True
    db.session.commit()
    flash('Report marked as resolved.', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/users/<int:user_id>/reinstate', methods=['POST'])
@login_required
def reinstate_user(user_id):
    if not current_user.is_admin:
        flash('Access Denied.', 'error')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    user.is_active = True
    db.session.commit()
    flash(f'{user.display_name} has been reinstated.', 'info')
    return redirect(url_for('admin_dashboard'))


# Adding API Routes for potential future mobile expansion

@app.route('/api/v1/auth/login', methods=['POST'])
def api_login():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required.'}), 400
    
    user = User.query.filter_by(email=data['email'].strip().lower()).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password.'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Your account has been suspended. Please contact an admin'}), 403
    
    access_token = create_access_token(identity=str(user.id))
    return jsonify({'access_token': access_token, 'user': user.to_dict()}), 200

@app.route('/api/v1/listings', methods=['GET'])
def api_get_listings():
    listings = Listing.query.filter_by(status='active').order_by(Listing.created_at.desc()).all()
    return jsonify([listing.to_dict() for listing in listings]), 200

@app.route('/api/v1/listings/<int:listing_id>', methods=['GET'])
def api_get_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    return jsonify(listing.to_dict()), 200

@app.route('/api/v1/listings', methods=['POST'])
@jwt_required()
def api_create_listings():
    current_user_id = int(get_jwt_identity())
    data = request.get_json()

    required_fields = ['title', 'author', 'condition', 'price']
    for field in required_fields:
        if not data or not data.get(field):
            return jsonify({'error': f'{field} is required.'}), 400
        
    try:
        price = float(data['price'])
        if price < 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({'error': 'Price must be a positive number.'}), 400
    
    listing = Listing(
        title=data['title'],
        author=data['author'],
        edition=data.get('edition'),
        condition=data['condition'],
        price=price,
        course_code=data.get('course_code'),
        professor=data.get('professor'),
        description=data.get('description'),
        seller_id=current_user_id
    )
    db.session.add(listing)
    db.session.commit()
    return jsonify(listing.to_dict()), 201

@app.route('/api/v1/listings/<int:listing_id>', methods=['PUT'])
@jwt_required()
def api_edit_listing(listing_id):
    current_user_id = int(get_jwt_identity())
    listing = Listing.query.get_or_404(listing_id)

    if listing.seller_id != current_user_id:
        user = User.query.get(current_user_id)
        if not user or not user.is_admin:
            return jsonify({'error': 'You do not have permission to edit this listing.'}), 403
        
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided.'}), 400
    
    listing.title = data.get('title', listing.title)
    listing.author = data.get('author', listing.author)
    listing.edition = data.get('edition', listing.edition)
    listing.condition = data.get('condition', listing.condition)
    listing.professor = data.get('professor', listing.professor)
    listing.course_code = data.get('course_code', listing.course_code)
    listing.description = data.get('description', listing.description)

    if 'price' in data:
        try:
            price = float(data['price'])
            if price < 0:
                raise ValueError
            listing.price = price
        except (ValueError, TypeError):
            return jsonify({'error': 'Price must be a positive number.'}), 400
        
    db.session.commit()
    return jsonify(listing.to_dict()), 200

@app.route('/api/v1/listings/<int:listing_id>', methods=['DELETE'])
@jwt_required()
def api_delete_listing(listing_id):
    current_user_id = int(get_jwt_identity())
    listing = Listing.query.get_or_404(listing_id)

    if listing.seller_id != current_user_id:
        user = User.query.get(current_user_id)
        if not user or not user.is_admin:
            return jsonify({'error': 'You do not have permission to delete this listing.'}), 403
        
    if listing.image_filename:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], listing.image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(listing)
    db.session.commit()
    return jsonify({'message': 'Listing deleted successfully.'}), 200

@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
def api_get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200



if __name__ == "__main__":
    app.run(debug = True, host = "0.0.0.0", port = 3000)