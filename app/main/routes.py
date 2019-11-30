# application routes file
from flask_login import login_required, current_user
from flask import current_app
from app import db
from app.main import bp
from flask import render_template, flash, redirect, url_for, request
from app.main.forms import EditProfileForm, PostForm
from app.models import User, Post

from datetime import datetime


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    """Home page view controller"""
    title = 'Homepage'
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None
    form = PostForm()

    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('main.index'))

    return render_template('main/index.html', title=title,
                           posts=posts, form=form, next_url=next_url, prev_url=prev_url)


@bp.route('/explore')
@login_required
def explore():
    title = 'Explore'
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) if posts.has_prev else None

    return render_template('main/index.html', title=title, posts=posts, next_url=next_url, prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    """User  profile page view controller"""
    title = 'User Profile'
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.followed_posts().paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=username, page=posts.prev_num) if posts.has_prev else None
    return render_template('main/user.html', title=title, user=user, posts=posts, next_url=next_url, prev_url=prev_url)


@bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile view controller"""
    title = 'Edit User Profile'
    form = EditProfileForm(current_user)

    if form.validate_on_submit():
        if form.username.data != current_user.username:
            current_user.username = form.username.data

        current_user.about_me = form.about_me.data
        db.session.commit()
        return redirect(url_for('main.user', username=current_user.username))

    return render_template('main/edit_profile.html', title=title, form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    """Follow another user."""
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))

    if user == current_user:
        flash('You can not follow yourself.')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}.'.format(username))
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    """Unfollow other user."""
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))

    if user == current_user:
        flash('You can not unfollow yourself.')
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {} anymore.'.format(username))
    return redirect(url_for('main.user', username=username))
