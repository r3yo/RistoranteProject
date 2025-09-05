from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from .models import Table
from django.contrib.auth.models import User, Group

class TableViewTests(TestCase):
    def setUp(self):
        # Create manager user
        self.manager = User.objects.create_user(username="manager", password="pass")
        group, _ = Group.objects.get_or_create(name="Managers") # "_" refers to "created" in (object, created) which is not needed
        self.manager.groups.add(group)
        self.manager.save()

        # Create non-manager user
        self.user = User.objects.create_user(username="user", password="pass")

        # Create a table
        self.table = Table.objects.create(number=1, seats=4)

        self.client = Client()

    def test_table_list_view_requires_manager(self):
        url = reverse("tables:tables-list")
        # Not logged in --> redirected
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        # Logged in as non-manager --> redirected
        self.client.login(username="user", password="pass")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        # Logged in as manager --> allowed
        self.client.login(username="manager", password="pass")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.table, response.context["tables"])

    def test_create_table_view(self):
        url = reverse("tables:add-table")
        self.client.login(username="manager", password="pass")
        response = self.client.post(url, {
            "number": 2,
            "seats": 6
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Table.objects.filter(number=2).exists())

    def test_update_table_view(self):
        url = reverse("tables:update-table", kwargs={"pk": self.table.slug})
        self.client.login(username="manager", password="pass")
        response = self.client.post(url, {
            "number": self.table.number,
            "seats": 8
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.table.refresh_from_db()
        self.assertEqual(self.table.seats, 8)

    def test_delete_table_view(self):
        url = reverse("tables:delete-table", kwargs={"pk": self.table.slug})
        self.client.login(username="manager", password="pass")
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Table.objects.filter(slug=self.table.slug).exists())

    def test_table_detail_view(self):
        url = reverse("tables:table-detail", kwargs={"pk": self.table.slug})
        self.client.login(username="manager", password="pass")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"Table {self.table.number}")