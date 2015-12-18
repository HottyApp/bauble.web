from flask import redirect, request, url_for
from flask.ext.login import login_required
import sqlalchemy.orm as orm

import bauble.db as db
from bauble.forms import form_factory
from bauble.models import Family
from bauble.middleware import use_model
from bauble.resource import Resource
import bauble.utils as utils


resource = Resource('family', __name__)

@resource.index
def index(families):
    families = Family.query.all()
    if request.accept_mimetypes.best == 'application/json':
        return resource.render_json(families)
    return resource.render_html(families=families)

@resource.show
def show(id):
    family = Family.query \
                   .options(orm.joinedload(*Family.synonyms.attr)) \
                   .get_or_404(id)

    if request.prefers_json:
        return resource.render_json(family)

    relations = ['/genera', '/genera/taxa', '/genera/taxa/accessions',
                 '/genera/taxa/accessions/plants']
    counts = {}
    for relation in relations:
        _, base = relation.rsplit('/', 1)
        counts[base] = utils.count_relation(family, relation)

    return resource.render_html(family=family, counts=counts)

@resource.new
def new():
    family = Family()
    return resource.render_html(family=family, form=form_factory(family))

@resource.create
@login_required
@use_model(Family)
def create(family):
    db.session.add(family)
    db.session.commit()
    if request.prefers_json:
        return resource.rendor_json(family)
    return resource.render_html(family=family, form=form_factory(family))


@resource.update
@login_required
@use_model(Family)
def update(family, id):
    db.session.commit()
    if request.prefers_json:
        return resource.rendor_json(family)
    # return resource.render_html(family=family, form=form_factory(family))
    return redirect(url_for('.edit', id=id))

@resource.edit
@login_required
def edit(id):
    family = Family.query.get_or_404(id)
    if request.prefers_json:
        return resource.rendor_json(family)
    return resource.render_html(family=family, form=form_factory(family))

@resource.destroy
@login_required
@use_model(Family)
def destroy(family, id):
    db.session.delete(family)
    db.session.commit()
    return '', 204

# @route()
def count(id):
    pass
