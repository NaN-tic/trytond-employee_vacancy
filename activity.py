# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta
from trytond.transaction import Transaction

__all__ = ['Activity']


class Activity:
    __name__ = 'activity.activity'
    __metaclass__ = PoolMeta

    @classmethod
    def default_party(cls):
        vacancy_party_id = Transaction().context.get('vacancy_party')
        if vacancy_party_id:
            return vacancy_party_id
        return super(Activity, cls).default_party()
