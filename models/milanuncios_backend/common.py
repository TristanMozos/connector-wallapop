# -*- coding: utf-8 -*-
# Copyright 2019 Halltic eSolutions S.L.
# © 2019 Halltic eSolutions S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import datetime, timedelta

from decorator import contextmanager
from odoo import models, fields, api, _
from odoo.addons.connector.checkpoint import checkpoint

from ...components.backend_adapter import MilanunciosAPI

_logger = logging.getLogger(__name__)

IMPORT_DELTA_BUFFER = 120  # seconds


class MilanunciosBackend(models.Model):
    _name = 'milanuncios.backend'
    _description = 'Milanuncios Backend'
    _inherit = 'connector.backend'

    name = fields.Char('name', required=True)
    user = fields.Char('User', required=True)
    psw = fields.Char('Password', required=True)

    @contextmanager
    def work_on(self, model_name, **kwargs):
        self.ensure_one()
        # We create a eBay Client API here, so we can create the
        # client once (lazily on the first use) and propagate it
        # through all the sync session, instead of recreating a client
        # in each backend adapter usage.
        with MilanunciosAPI(self) as milanuncios_api:
            _super = super(MilanunciosBackend, self)
            # from the components we'll be able to do: self.work.ebay_api
            with _super.work_on(
                    model_name, milanuncios_api=milanuncios_api, **kwargs) as work:
                yield work

    def _export_product_stock(self,
                            import_start_time=None,
                            import_end_time=None,
                            update_import_date=True):

        for backend in self:
            return

        return True


    @api.model
    def _milanuncios_backend(self, callback, domain=None):
        if domain is None:
            domain = []
        backends = self.search(domain)
        if backends:
            getattr(backends, callback)()

    @api.model
    def _scheduler_export_product_stock(self, domain=None):
        self._milanuncios_backend('_export_product_stock', domain=domain)
