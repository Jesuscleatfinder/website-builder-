from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from app import app, db
from app.models import Tutorial, User, Comment, LikeDislike
from app.forms import TutorialForm, CommentForm, LoginForm, RegistrationForm
from werkzeug.security import check_password_hash
from sqlalchemy import func

# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data, method='sha256')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login failed. Check your email and password.', 'danger')
    return render_template('login.html', form=form)

# Home Route (list tutorials)
@app.route('/')
def home():
    tutorials = Tutorial.query.all()
    return render_template('home.html', tutorials=tutorials)

# Tutorial Details
@app.route('/tutorial/<int:id>')
def tutorial(id):
    tutorial = Tutorial.query.get_or_404(id)
    comments = Comment.query.filter_by(tutorial_id=id).all()
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(content=form.content.data, tutorial_id=tutorial.id, user_id=current_user.id)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added!', 'success')
        return redirect(url_for('tutorial', id=tutorial.id))
    return render_template('tutorial_detail.html', tutorial=tutorial, comments=comments, form=form)

# Tutorial Edit
@app.route('/edit_tutorial/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_tutorial(id):
    tutorial = Tutorial.query.get_or_404(id)
    if tutorial.author != current_user.id:
        flash('You are not authorized to edit this tutorial', 'danger')
        return redirect(url_for('home'))
    form = TutorialForm(obj=tutorial)
    if form.validate_on_submit():
        tutorial.title = form.title.data
        tutorial.content = form.content.data
        db.session.commit()
        flash('Tutorial updated!', 'success')
        return redirect(url_for('tutorial', id=tutorial.id))
    return render_template('edit_tutorial.html', form=form)

# Like/Dislike Tutorial
@app.route('/like_dislike/<int:id>', methods=['POST'])
@login_required
def like_dislike(id):
    action = request.form.get('action')  # 'like' or 'dislike'
    tutorial = Tutorial.query.get_or_404(id)
    existing_action = LikeDislike.query.filter_by(tutorial_id=id, user_id=current_user.id).first()
    if existing_action:
        existing_action.action = action
    else:
        like_dislike = LikeDislike(tutorial_id=id, user_id=current_user.id, action=action)
        db.session.add(like_dislike)
    db.session.commit()

    # Update tutorial likes/dislikes
    likes = LikeDislike.query.filter_by(tutorial_id=id, action='like').count()
    dislikes = LikeDislike.query.filter_by(tutorial_id=id, action='dislike').count()
    tutorial.likes = likes
    tutorial.dislikes = dislikes
    db.session.commit()

    flash('Your reaction has been recorded!', 'success')
    return redirect(url_for('tutorial', id=tutorial.id))
