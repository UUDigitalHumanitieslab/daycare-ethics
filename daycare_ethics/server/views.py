# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""
    Directly visitable routes on the domain.
"""

from datetime import date, datetime, timedelta

from flask import send_from_directory, jsonify, current_app, abort, request, escape, session

from ..util import image_variants, TARGET_WIDTHS
from ..database.models import *
from ..database.db import db
from .blueprint import public
from .security import session_enable, session_protect, init_captcha, captcha_safe


ISOFORMAT = '%Y-%m-%d %H:%M:%S%z'
POST_INTERVAL = timedelta(minutes=10)


@public.route('/')
def index():
    return send_from_directory(public.static_folder, 'index.html')


@public.route('/media/<int:id>/<int:width>')
def media(id, width):
    try:
        image = Picture.query.filter_by(id=id).one().path
    except:
        abort(404)
    variants = image_variants(image)
    cutoffs = TARGET_WIDTHS[1:] + (100000,)
    for cutoff, variant in zip(cutoffs, variants):
        if cutoff >= width:
            return send_from_directory(current_app.instance_path, variant)
    abort(404)


@public.route('/case/')
@session_enable
def current_casus():
    latest_casus = available_casus().first()
    if not latest_casus or not latest_casus.publication:
        abort(404)
    return casus2dict(latest_casus)


@public.route('/case/<int:id>')
def retrieve_casus(id):
    casus = Case.query.get_or_404(id)
    if not casus.publication or casus.publication > date.today():
        abort(404)
    return jsonify(**casus2dict(casus))


def casus2dict(casus):
    if casus.closure:
        closure = str(casus.closure)
    else:
        closure = None
    return {
        'id': casus.id,
        'title': casus.title,
        'publication': str(casus.publication),
        'week': casus.publication.strftime('%W'),
        'closure': closure,
        'text': casus.text,
        'proposition': casus.proposition,
        'picture': casus.picture_id,
        'background': casus.background,
        'yes': casus.yes_votes,
        'no': casus.no_votes,
    }


def available_casus():
    now = date.today()
    return (
        Case.query
        .filter(Case.publication != None, Case.publication <= now)
        .order_by(Case.publication.desc())
    )


@public.route('/case/archive')
def casus_archive():
    return jsonify(all=map(casus2dict, available_casus().all()))


@public.route('/case/vote', methods=['POST'])
@session_protect
def vote_casus():
    now = datetime.today()
    if 'id' not in request.form or 'choice' not in request.form:
        return {'status': 'invalid'}, 400
    id, choice = int(request.form['id']), request.form['choice']
    try:
        casus = Case.query.filter_by(id=id).one()
    except:
        return {'status': 'unavailable'}, 400
    if casus.closure and casus.closure <= date.today():
        return {'status': 'unavailable'}, 400
    ses = db.session
    if choice == 'yes':
        casus.yes_votes += 1
        ses.add(Vote(agree=True, submission=now, case=casus))
        ses.commit()
        return {'status': 'success'}
    elif choice == 'no':
        casus.no_votes += 1
        ses.add(Vote(agree=False, submission=now, case=casus))
        ses.commit()
        return {'status': 'success'}
    else:
        return {'status': 'invalid'}, 400


@public.route('/reflection/')
@session_enable
def current_reflection():
    latest_reflection = (
        BrainTeaser.query
        .filter(BrainTeaser.publication <= date.today())
        .order_by(BrainTeaser.publication.desc())
        .first()
    )
    if latest_reflection.publication:
        publication = str(latest_reflection.publication)
        week = latest_reflection.publication.strftime('%W')
    else:
        publication = None
        week = None
    if latest_reflection.closure:
        closure = str(latest_reflection.closure)
    else:
        closure = None
    return {
        'id': latest_reflection.id,
        'title': latest_reflection.title,
        'publication': publication,
        'week': week,
        'closure': closure,
        'text': latest_reflection.text,
        'responses': reflection_replies(latest_reflection.id),
    }


def response2dict(response):
    return {
        'submission': str(response.submission.date()),
        'pseudonym': response.pseudonym,
        'message': response.message,
        'id': response.id,
        'up': response.upvotes,
        'down': response.downvotes,
    }


def reflection_replies(id, since=None):
    query = Response.query.filter_by(brain_teaser_id=id)
    if since is not None:
        if isinstance(since, str):
            since = datetime.strptime(since, ISOFORMAT)
        query.filter(Response.submission >= since)
    return map(response2dict, query.order_by(Response.submission).all())


@public.route('/reflection/<int:id>/reply', methods=['POST'])
@session_protect
def reply_to_reflection(id):
    now = datetime.today()
    topic = BrainTeaser.query.get_or_404(id)
    if topic.closure and topic.closure <= now:
        return {'status': 'closed'}, 400
    if 'last-retrieve' in request.form:
        ninjas = reflection_replies(id, request.form['last-retrieve'])
        if ninjas:
            return {
                'status': 'ninja',
                'new': ninjas,
                'since': str(now),
            }
    if ( 'p' not in request.form or not request.form['p']
         or 'r' not in request.form or not request.form['r'] ):
        return {'status': 'invalid'}, 400
    # code below does not enforce quarantine period.
    # in order to make it happen, return {status: quarantine} if not 
    # captcha_safe.
    if ( not captcha_safe() or 'captcha-quarantine' in session or
         'last-reply' in session and now - session['last-reply'] < POST_INTERVAL ):
        return dict(status='captcha', **init_captcha())
    db.session.add(Response(
        brain_teaser=topic,
        submission=now,
        pseudonym=escape(request.form['p'].strip())[:30],
        message=escape(request.form['r'].strip())
    ))
    db.session.commit()
    session['last-reply'] = now
    return {'status': 'success'}


def moderate_response(id, up):
    target = Response.query.get_or_404(id)
    if up:
        target.upvotes += 1
    else:
        target.downvotes += 1
    db.session.commit()
    return {'status': 'success'}


@public.route('/reflection/response/<int:id>/upmod', methods=['POST'])
@session_protect
def upmoderate_response(id):
    return moderate_response(id, True)


@public.route('/reflection/response/<int:id>/downmod', methods=['POST'])
@session_protect
def downmoderate_response(id):
    return moderate_response(id, False)
