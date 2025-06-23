# Copyright 2025 Binhex - Rolando Pérez Rebollo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, models
from odoo.exceptions import AccessDenied


class ResourceBooking(models.Model):
    _inherit = "resource.booking"

    @api.model
    def create_booking_portal(self, values):
        if not (self.env.user.create_booking_from_portal):
            raise AccessDenied()
        if not (values["resource_name"] and values["resource_type"]):
            return {"errors": _("Missing required fields!")}

        user = self.env.user
        self = self.sudo()

        partner = user.partner_id
        res = self.create(
            {
                "name": values.get("resource_name"),
                "type_id": int(values.get("resource_type")),
                "description": values.get("resource_description"),
                "combination_auto_assign": True,
                "partner_id": partner.id,
                "user_id": user.id,
            }
        )

        return {"id": res.id}
