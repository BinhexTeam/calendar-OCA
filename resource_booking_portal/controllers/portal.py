# Copyright 2024 Binhex - Adasat Torres de León
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from datetime import datetime
from urllib.parse import quote_plus

from dateutil.parser import isoparse

from odoo.exceptions import ValidationError
from odoo.http import request, route
from odoo.tests.common import Form

from odoo.addons.portal.controllers import portal


class CustomerPortal(portal.CustomerPortal):
    @route(
        ["/my/bookings/prepare/form"],
        auth="user",
        type="http",
        website=True,
    )
    def portal_bookings_prepare_form(self):
        values = {
            "page_name": "create_booking",
            "types": request.env["resource.booking.type"]
            .sudo()
            .search_read([], ["id", "name"]),
        }
        return request.render("resource_booking_portal.booking_create_form", values)

    @route(
        ["/my/bookings/create"],
        auth="user",
        type="http",
        method=["POST"],
        website=True,
        csrf=False,
    )
    def portal_bookings_create(self, **post):
        Booking = request.env["resource.booking"].sudo()
        BookingType = request.env["resource.booking.type"].sudo()
        partner_id = request.env.user.partner_id
        res = Booking.create(
            {
                "name": post.get("name"),
                "type_id": BookingType.browse(int(post.get("type"))).id,
                "partner_id": partner_id.id,
                "combination_auto_assign": True,
                "description": post.get("description", False),
                "user_id": partner_id.user_id.id,
            }
        )
        return request.redirect("/my/bookings/%s/schedule" % res.id)

    @route(
        ["/my/bookings/<int:booking_id>/reserve"],
        auth="user",
        type="http",
        method=["POST"],
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
                suffix="/schedule/{:%Y/%m}".format(when_tz_aware),
                query_string="&error={}".format(quote_plus(error.name)),
            )
            return request.redirect(url)
        return request.redirect(booking_sudo.get_portal_url())
