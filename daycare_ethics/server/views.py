# (c) 2014, 2015 Digital Humanities Lab, Utrecht University
# Authors: Julian Gonggrijp, j.gonggrijp@uu.nl,
#          Martijn van der Klis, m.h.vanderklis@uu.nl

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


ISOFORMAT = '%Y-%m-%d %H:%M:%S.%f'
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
        if cutoff > width:
            return send_from_directory(current_app.instance_path, variant)
    abort(404)


@public.route('/case/')
def current_casus():
    latest_casus = available_casus().first()
    if not latest_casus or not latest_casus.publication:
        abort(404)
    return jsonify(**casus2dict(latest_casus))


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
        'week': casus.publication.isocalendar()[1],
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
    latest_reflection = available_reflection().first()
    if not latest_reflection or not latest_reflection.publication:
        abort(404)
    return reflection2dict(latest_reflection, True)


@public.route('/reflection/<int:id>/')
def retrieve_reflection(id):
    reflection = BrainTeaser.query.get_or_404(id)
    if not reflection.publication or reflection.publication > date.today():
        abort(404)
    return jsonify(**reflection2dict(reflection, True))


def reflection2dict(reflection, with_responses=False):
    if reflection.closure:
        closure = str(reflection.closure)
    else:
        closure = None
    if with_responses:
        replies = reflection_replies(reflection.id)
    else:
        replies = None
    now = datetime.today()
    return {
        'id': reflection.id,
        'title': reflection.title,
        'publication': str(reflection.publication),
        'week': reflection.publication.isocalendar()[1],
        'closure': closure,
        'text': reflection.text,
        'responses': replies,
        'since': str(now),
    }


def available_reflection():
    now = date.today()
    return (
        BrainTeaser.query
        .filter(BrainTeaser.publication != None)
        .filter(BrainTeaser.publication <= now)
        .order_by(BrainTeaser.publication.desc())
    )


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
        if isinstance(since, str) or isinstance(since, unicode):
            since = datetime.strptime(since, ISOFORMAT)
        query = query.filter(Response.submission >= since)
    return map(response2dict, query.order_by(Response.submission).all())


@public.route('/reflection/archive')
def reflection_archive():
    return jsonify(all=map(reflection2dict, available_reflection()))


@public.route('/reflection/<int:id>/reply', methods=['POST'])
@session_protect
def reply_to_reflection(id):
    now = datetime.today()
    topic = BrainTeaser.query.get_or_404(id)
    if topic.closure and topic.closure <= now.date():
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
    if ( 'last-reply' in session and
         now - session['last-reply'] < POST_INTERVAL and
         not 'captcha-answer' in session ):
        return dict(status='captcha', **init_captcha())
    # code below does not enforce quarantine period.
    # in order to make it happen, return {status: quarantine} if not 
    # captcha_safe.
    if (not captcha_safe() or 'captcha-quarantine' in session):
        return dict(status='captcha', **init_captcha())
    db.session.add(Response(
        brain_teaser=topic,
        submission=now,
        pseudonym=escape(request.form['p'].strip())[:30],
        message=escape(request.form['r'].strip())[:400]
    ))
    db.session.commit()
    session['last-reply'] = now
    return {'status': 'success'}


@public.route('/reply/<int:id>/moderate/', methods=['POST'])
@session_protect
def moderate_reply(id):
    if 'choice' not in request.form:
        return {'status': 'invalid'}, 400
    choice = request.form['choice']
    try:
        target = Response.query.filter_by(id=id).one()
    except:
        return {'status': 'unavailable'}, 400
    ses = db.session
    if choice == 'up':
        target.upvotes += 1
        ses.commit()
        return {'status': 'success'}
    elif choice == 'down':
        target.downvotes += 1
        ses.commit()
        return {'status': 'success'}
    else:
        return {'status': 'invalid'}, 400


def tip2dict(tip):
    return {
        'id': tip.id,
        'created': str(tip.create),
        'updated': str(tip.update),
        'author': tip.author,
        'title': tip.title,
        'text': tip.text,
        'href': tip.href,
    }


@public.route('/tips/')
def retrieve_tips():
    sorted_tips = Tip.query.order_by(Tip.update.desc())
    labour_code = map(tip2dict, sorted_tips.filter_by(what='labour code').all())
    book = map(tip2dict, sorted_tips.filter_by(what='book').all())
    site = map(tip2dict, sorted_tips.filter_by(what='site').all())
    return jsonify(labour=labour_code, book=book, site=site)
