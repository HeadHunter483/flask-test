from flask import (Blueprint, render_template, request, flash, redirect,
                   url_for, current_app as app)
from flask_babel import _
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.models import db, User, Post

acc_bp = Blueprint('accounts', __name__)


@acc_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('accounts.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home.index')
        return redirect(next_page)
    return render_template('login.html', title=_('Sign In'), form=form)


@acc_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home.index'))


@acc_bp.route('/registration', methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations! You have successfully signed up! '
              'Now you can sign in to your account.'))
        return redirect(url_for('accounts.login'))
    return render_template('registration.html', title=_('Sign Up'), form=form)


@acc_bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    title = _("%(username)s's Profile", username=username)
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('accounts.user', username=user.username,
                       page=posts.next_num) if posts.has_next else None
    prev_url = url_for('accounts.user', username=user.username,
                       page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html', title=title, user=user,
                           posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@acc_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('accounts.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form)


@acc_bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('home.index'))
    if user == current_user:
        flash(_('You cannot follow yourself.'))
        return redirect(url_for('accounts.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following %(username)s!', username=username))
    return redirect(url_for('accounts.user', username=username))


@acc_bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('home.index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself.'))
        return redirect(url_for('accounts.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s.', username=username))
    return redirect(url_for('accounts.user', username=username))
