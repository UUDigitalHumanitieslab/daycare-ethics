# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""
    Directly visitable routes on the domain.
"""

from datetime import date, datetime

from flask import send_from_directory, jsonify, current_app, abort, request, escape

from ..util import image_variants, TARGET_WIDTHS
from ..database.models import *
from ..database.db import db
from blueprint import public


ISOFORMAT = '%Y-%m-%d %H:%M:%S%z'


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
def current_casus():
    latest_casus = (
        Case.query
        .filter(Case.publication <= date.today())
        .order_by(Case.publication.desc())
        .first()
    )
    if latest_casus.publication:
        publication = str(latest_casus.publication)
        week = latest_casus.publication.strftime('%W')
    else:
        publication = None
        week = None
    if latest_casus.closure:
        closure = str(latest_casus.closure)
    else:
        closure = None
    return jsonify(
        id=latest_casus.id,
        title=latest_casus.title,
        publication=publication,
        week=week,
        closure=closure,
        text=latest_casus.text,
        proposition=latest_casus.proposition,
        picture=latest_casus.picture_id,
        background=latest_casus.background,
        yes=latest_casus.yes_votes,
        no=latest_casus.no_votes )


@public.route('/case/vote')
def vote_casus():
    now = datetime.today()
    if 'id' not in request.values or 'choice' not in request.values:
        return 'invalid'
    id, choice = int(request.values['id']), request.values['choice']
    try:
        casus = Case.query.filter_by(id=id).one()
    except:
        return 'unavailable'
    if casus.closure and casus.closure <= date.today():
        return 'unavailable'
    ses = db.session
    if choice == 'yes':
        casus.yes_votes += 1
        ses.add(Vote(agree=True, submission=now, case=casus))
        ses.commit()
        return 'success'
    elif choice == 'no':
        casus.no_votes += 1
        ses.add(Vote(agree=False, submission=now, case=casus))
        ses.commit()
        return 'success'
    else:
        return 'invalid'


@public.route('/reflection/')
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
    return jsonify(
        id=latest_reflection.id,
        title=latest_reflection.title,
        publication=publication,
        week=week,
        closure=closure,
        text=latest_reflection.text )


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


@public.route('/reflection/<int:id>/reply')
def reply_to_reflection(id):
    now = datetime.today()
    topic = BrainTeaser.query.get_or_404(id)
    if topic.closure and topic.closure <= now:
        return 'closed'
    if 'last-retrieve' in request.values:
        ninjas = reflection_replies(id, request.values['last-retrieve'])
        if ninjas:
            return jsonify(
                new=ninjas,
                since=str(now) )
    if 'pseudonym' in request.values:
        pseudonym = request.values['pseudonym']
    else:
        pseudonym = 'anoniem'
    if 'message' not in request.values or not request.values['message']:
        return 'invalid'
    db.session.add(Response(
        brain_teaser=topic,
        submission=now,
        pseudonym=escape(pseudonym.strip())[:30],
        message=escape(request.values['message'].strip())
    ))
    db.session.commit()
    return 'success'
