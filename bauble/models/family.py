from sqlalchemy import (func, Column, Date, Enum, ForeignKey, Integer, String, Text,
                        UniqueConstraint)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy

import bauble.db as db
import bauble.search as search


def family_markup_func(family):
    """
    return a string or object with __str__ method to use to markup
    text in the results view
    """
    return family


class Family(db.Model):
    """
    :Table name: family

    :Columns:
        *family*:
            The name if the family. Required.

        *qualifier*:
            The family qualifier.

            Possible values:
                * s. lat.: aggregrate family (senso lato)

                * s. str.: segregate family (senso stricto)

                * '': the empty string

        *notes*:
            Free text notes about the family.

    :Properties:
        *synonyms*:
            An association to _synonyms that will automatically
            convert a Family object and create the synonym.

    :Constraints:
        The family table has a unique constraint on family/qualifier.
    """
    __table_args__ = (UniqueConstraint('family', 'qualifier'),)
    # __mapper_args__ = {'order_by': ['Family.family', 'Family.qualifier']}
    __mapper_args__ = {'order_by': ['family', 'qualifier']}

    # columns
    family = Column(String(45), nullable=False, index=True)

    # we use the blank string here instead of None so that the
    # contraints will work properly,
    qualifier = Column(Enum('s. lat.', 's. str.'))

    # relations
    synonyms = association_proxy('_synonyms', 'synonym')
    _synonyms = relationship('FamilySynonym',
                             primaryjoin='Family.id==FamilySynonym.family_id',
                             cascade='all, delete-orphan', uselist=True,
                             backref='family')

    def __str__(self):
        return Family.str(self)


    def str(self, qualifier=False):
        if self.family is None:
            return ''
        return ' '.join(filter(lambda s: s not in (None, ''),
                               [self.family, self.qualifier]))


class FamilyNote(db.Model):
    """
    Notes for the family table
    """
    date = Column(Date, default=func.now())
    user = Column(String(64))
    category = Column(String(32))
    note = Column(Text, nullable=False)
    family_id = Column(Integer, ForeignKey('family.id'), nullable=False)
    family = relationship('Family', uselist=False,
                          backref=backref('notes', cascade='all, delete-orphan'))


class FamilySynonym(db.Model):
    """
    :Table name: family_synonyms

    :Columns:
        *family_id*:

        *synonyms_id*:

    :Properties:
        *synonyms*:

        *family*:
    """
    # columns
    family_id = Column(Integer, ForeignKey('family.id'), nullable=False)
    synonym_id = Column(Integer, ForeignKey('family.id'), nullable=False,
                        unique=True)

    # relations
    synonym = relationship('Family', uselist=False,
                           primaryjoin='FamilySynonym.synonym_id==Family.id')

    def __init__(self, synonym=None, **kwargs):
        # it is necessary that the first argument here be synonym for
        # the Family.synonyms association_proxy to work
        self.synonym = synonym
        super(FamilySynonym, self).__init__(**kwargs)


    def __str__(self):
        return Family.str(self.synonym)


#
# setup the search matchers
#
mapper_search = search.get_strategy('MapperSearch')
mapper_search.add_meta(('families', 'family', 'fam'), Family, ['family'])
