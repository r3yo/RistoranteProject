from django.test import TestCase, Client
from django.urls import reverse
from .models import Notification, User
from django.utils import timezone

class NotificationViewsTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.other_user = User.objects.create_user(username='otheruser', password='pass')

        # Create 5 unread notifications for self.user
        for i in range(5):
            Notification.objects.create(
                user=self.user,
                message=f"Notification {i}",
                type="info",
                read=False,
                created_at=timezone.now()
            )

        # Create 3 notifications for other_user (should not appear)
        for i in range(3):
            Notification.objects.create(
                user=self.other_user,
                message=f"Other user notification {i}",
                type="info",
                read=False,
                created_at=timezone.now()
            )

    def test_notifications_json_returns_only_unread_for_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('notifications:json'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 5)
        for n in data:
            self.assertFalse(n['read'])
            self.assertIn("Notification", n['message'])

    def test_notifications_json_does_not_return_other_users(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('notifications:json'))
        data = response.json()
        for n in data:
            self.assertNotIn("Other user", n['message'])

    def test_mark_all_read_updates_notifications(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('notifications:mark_all_read'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})
        # All notifications for this user should now be read
        unread = Notification.objects.filter(user=self.user, read=False).count()
        self.assertEqual(unread, 0)
        # Notifications for other user remain unread
        other_unread = Notification.objects.filter(user=self.other_user, read=False).count()
        self.assertEqual(other_unread, 3)