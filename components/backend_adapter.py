# -*- coding: utf-8 -*-
# Copyright 2018 Halltic eSolutions S.L.
# © 2018 Halltic eSolutions S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# This project is based on connector-magneto, developed by Camptocamp SA

import StringIO
import logging
import dateutil.parser
import re
from lxml import etree

import unicodecsv
from odoo.fields import Datetime
from odoo.addons.component.core import AbstractComponent
from odoo.addons.queue_job.exception import FailedJobError, RetryableJobError

_logger = logging.getLogger(__name__)

_logger.debug("Cannot import 'wallapop' API")

class WallapopAPI(object):

    def __init__(self, backend):
        """
        :param backend: Wallapop Backend
        """
        self._backend = backend
        self._api = None
        self._method = None

    @property
    def api(self):
        api = None
        self._api = api
        return self._api

    def __enter__(self):
        # we do nothing, api is lazy
        return self

    def __exit__(self, type, value, traceback):
        if self._api is not None:
            self._api.__exit__(type, value, traceback)

    def call(self, method, arguments):
        try:
            self.method = method
            result = self.api.execute(self.method, arguments)
        except ConnectionError as e:
            _logger.error(e.response.dict())
            raise e
        except:
            _logger.error("api.call('%s', %s) failed", method, arguments)
            raise
        return result


class WallapopCRUDAdapter(AbstractComponent):
    """ External Records Adapter for Wallapop """

    _name = 'wallapop.crud.adapter'
    _inherit = ['base.backend.adapter', 'base.wallapop.connector']
    _usage = 'backend.adapter'

    def search(self, filters=None):
        """ Search records according to some criterias
        and returns a list of ids """
        raise NotImplementedError

    def read(self, id, attributes=None):
        """ Returns the information of a record """
        raise NotImplementedError

    def search_read(self, filters=None):
        """ Search records according to some criterias
        and returns their information"""
        raise NotImplementedError

    def create(self, data):
        """ Create a record on the external system """
        raise NotImplementedError

    def write(self, id, data):
        """ Update records on the external system """
        raise NotImplementedError

    def delete(self, id):
        """ Delete a record on the external system """
        raise NotImplementedError

    def _call(self, method, arguments):
        try:
            wallapop_api = getattr(self.work, 'wallapop_api')
        except AttributeError:
            raise AttributeError(
                'You must provide a wallapop_api attribute with a '
                'WallapopAPI instance to be able to use the '
                'Backend Adapter.'
            )
        return wallapop_api.call(method, arguments)


class GenericAdapter(AbstractComponent):
    _name = 'wallapop.adapter'
    _inherit = 'wallapop.crud.adapter'

    _wallapop_model = None
    _admin_path = None

    def _get_model(self):
        if self._wallapop_model:
            return self._wallapop_model
        elif self.model:
            return self.model._name
        elif self._apply_on:
            return self._apply_on
        return ''

    def search(self, filters=None):
        """ Search records according to some criterias
        and returns a list of ids

        :rtype: list
        """
        return self._call('%s_search' % self._get_model().replace('.', '_'), filters if filters else {})

    def read(self, external_id, attributes=None):
        """ Returns the information of a record

        :rtype: dict
        """
        if external_id and isinstance(external_id, (list, tuple)):
            arguments = external_id
        else:
            arguments = [external_id]
        if attributes:
            arguments.append(attributes)
        return self._call('%s_read' % self._get_model().replace('.', '_'), [arguments])

    def search_read(self, filters=None):
        """ Search records according to some criterias
        and returns their information"""
        return self._call('%s_list' % self._get_model(), [filters])

    def create(self, data):
        """ Create a record on the external system """
        return self._call('%s_create' % self._get_model(), [data])

    def write(self, id, data):
        """ Update records on the external system """
        return self._call('%s_update' % self._get_model(),
                          [int(id), data])

    def delete(self, id):
        """ Delete a record on the external system """
        return self._call('%s.delete' % self._get_model(), [int(id)])
