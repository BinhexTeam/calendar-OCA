# Copyright 2024 Binhex - Adasat Torres de León
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from freezegun import freeze_time
from lxml.html import fromstring

from odoo.tests import tagged
from odoo.tests.common import HttpCase


@tagged("post_install", "-at_install")
@freeze_time("2024-01-01 00:00:00", tick=True)
class TestCustomerPortal(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = cls.env["res.users"].create(
            {
                "name": "test user",
                "login": "test@test.com",
                "password": "password",
                "groups_id": [(4, cls.env.ref("base.group_user").id)],
            }
        )
        cls.resource = cls.env["resource.resource"].create(
            {"name": "Test Resource", "user_id": cls.test_user.id}
        )
        cls.combination = cls.env["resource.booking.combination"].create(
            {"resource_ids": [(6, 0, cls.resource.ids)]}
        )
        cls.booking_type = cls.env["resource.booking.type"].create(
            {
                "name": "Test Booking Type",
                "combination_rel_ids": [(6, 0, cls.combination.ids)],
            }
        )
        cls.portal_user = cls.env["res.users"].create(
            {
                "name": "Portal user",
                "login": "portal@portal.com",
                "password": "portal",
                "groups_id": [(4, cls.env.ref("base.group_portal").id)],
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
