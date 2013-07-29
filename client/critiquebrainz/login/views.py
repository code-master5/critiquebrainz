from flask import Blueprint, request, redirect, render_template, url_for, session
from flask.ext.login import login_user, logout_user, login_required
from critiquebrainz.api import api
from critiquebrainz.login import User, login_forbidden
from critiquebrainz.exceptions import OAuthError

bp = Blueprint('login', __name__)

@bp.route('/', endpoint='index')
@login_forbidden
def login_twitter_handler():
    return render_template('login/login.html')

@bp.route('/twitter', endpoint='twitter')
@login_forbidden
def login_twitter_handler():
    next = request.args.get('next')
    session['next'] = next
    return redirect(api.generate_twitter_authorization_uri())

@bp.route('/musicbrainz', endpoint='musicbrainz')
@login_forbidden
def login_musicbrainz_handler():
    next = request.args.get('next')
    session['next'] = next
    return redirect(api.generate_musicbrainz_authorization_uri())

@bp.route('/post', endpoint='post')
@login_forbidden
def login_post_handler():
    code = request.args.get('code')
    error = request.args.get('error')
    next = session.get('next')
    if code:
        error, access_token, refresh_token, expires_in = api.get_token_from_code(code)
        if error:
            raise OAuthError(error)
        user = User(refresh_token)
        user.access_token, user.expires_in = (access_token, expires_in)
        login_user(user)

        if next:
            return redirect(next)
        else:
            return redirect(url_for('index'))
    elif error == 'access_token':
        flash('You did not authorize the request')
    elif error:
        raise OAuthError(error)

    return redirect(url_for('.index'))

@bp.route('/logout', endpoint='logout')
@login_required
def login_logout_handler():
    logout_user()
    session.clear()
    return redirect(url_for('index'))