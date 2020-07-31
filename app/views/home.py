from flask import (Blueprint, url_for, render_template, redirect, flash,
                   request, current_app as app)
from flask_babel import _
from flask_login import current_user, login_required

from app.forms import PostForm
from app.models import db, Post

home_bp = Blueprint('home', __name__)


@home_bp.route('/', methods=['GET', 'POST'])
@home_bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('home.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('home.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('home.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Home'), form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@home_bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('home.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('home.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Explore'),
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@home_bp.route('/about')
def about():
    return render_template('about.html', title=_('About'))
