# Copyright 2024 Binhex - Adasat Torres de León
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from datetime import datetime

from dateutil.parser import isoparse

from odoo.exceptions import ValidationError
from odoo.http import request, route
from odoo.tests.common import Form

from odoo.addons.portal.controllers import portal


class CustomerPortal(portal.CustomerPortal):
    def _prepare_portal_layout_values(self):
        """Compute values for single-booking portal views."""
        res = super()._prepare_portal_layout_values()
        res["booking_types"] = (
            request.env["resource.booking.type"].sudo().search_read([], ["id", "name"])
        )
        return res

    @route(
        ["/my/bookings/<int:booking_id>/reserve"],
        auth="user",
        type="http",
        methods=["POST"],
        website=True,
    )
    def portal_booking_reserve(self, booking_id, access_token, when, **kwargs):
        booking_sudo = self._get_booking_sudo(booking_id, access_token)
        when_tz_aware = isoparse(when)
        when_naive = datetime.utcfromtimestamp(when_tz_aware.timestamp())
        try:
            with Form(booking_sudo) as booking_form:
                booking_form.start = when_naive
        except ValidationError as error:
            url = booking_sudo.get_portal_url(
                suffix=f"/schedule/{when_tz_aware:%Y/%m}",
                query_string=f"&error={error.args[0]}",
            )
            return request.redirect(url)
        return request.redirect(booking_sudo.get_portal_url())
