# Copyright 2024 Binhex - Adasat Torres de León
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from freezegun import freeze_time
from lxml.html import fromstring

from odoo.tests import tagged
from odoo.tests.common import HttpCase

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
@freeze_time("2024-01-01 00:00:00", tick=True)
class TestCustomerPortal(HttpCase):
    def setUp(self):
        super().setUp()
        self.test_user = self.env["res.users"].create(
            {
                "name": "test user",
                "login": "test@test.com",
                "password": "password",
                "groups_id": [(4, self.env.ref("base.group_user").id)],
            }
        )
        self.resource = self.env["resource.resource"].create(
            {"name": "Test Resource", "user_id": self.test_user.id}
        )
        self.combination = self.env["resource.booking.combination"].create(
            {"resource_ids": [(6, 0, self.resource.ids)]}
        )
        self.booking_type = self.env["resource.booking.type"].create(
            {
                "name": "Test Booking Type",
                "combination_rel_ids": [(6, 0, self.combination.ids)],
            }
        )
        self.portal_user = self.env["res.users"].create(
            {
                "name": "Portal user",
                "login": "portal@portal.com",
                "password": "portal",
                "groups_id": [(4, self.env.ref("base.group_portal").id)],
                "create_booking_from_portal": True,
            }
        )

    def test_portal_bookings_prepare_form(self):
        self.authenticate("portal@portal.com", "portal")
        response = self.url_open("/my/bookings/prepare/form")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("/web/login", response.url)
        page = fromstring(response.content)
        self.assertTrue(page.xpath("//form")[0])

    def test_portal_bookings_create(self):
        self.authenticate("portal@portal.com", "portal")
        response = self.url_open(
            "/my/bookings/create",
            data={
                "name": "Test Booking",
                "type": str(self.booking_type.id),
                "description": "Test Description",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("/web/login", response.url)
        self.assertIn("/my/bookings/", response.url)

    def test_portal_booking_reserve(self):
        self.authenticate("portal@portal.com", "portal")
        booking = self.env["resource.booking"].create(
            {
                "name": "Test Booking",
                "type_id": self.booking_type.id,
                "partner_id": self.portal_user.partner_id.id,
                "combination_auto_assign": True,
                "user_id": self.portal_user.id,
            }
        )
        url = f"/my/bookings/{booking.id}/schedule"
        response = self.url_open(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("/web/login", response.url)
        fromstring(response.content)
