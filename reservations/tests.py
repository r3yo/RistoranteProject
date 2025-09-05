from django.test import TestCase, Client
from django.utils import timezone
from datetime import time, timedelta
from django.urls import reverse
from .models import Reservation, Table, WaitlistEntry, User
from .forms import ReservationForm
from .views import add_to_waitlist

class ReservationFormTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.table = Table.objects.create(number=1, seats=4, slug='table-1')

    def test_form_valid_data_assigns_table_and_time(self):
        data = {
            'date': timezone.localdate() + timedelta(days=1),
            'guests': 4,
            'time': ["19", "20"],  # Must be strings
            'notes': 'Test notes',
            'join_waitlist': False
        }
        form = ReservationForm(data=data, user=self.user)
        self.assertTrue(form.is_valid())
        reservation = form.save()
        self.assertEqual(reservation.table, self.table)
        self.assertEqual(reservation.start_hour, time(19, 0))
        self.assertEqual(reservation.end_hour, time(21, 0))
        self.assertEqual(reservation.user, self.user)

    def test_form_conflict_validation(self):
        # Existing reservation for same user and table
        Reservation.objects.create(
            user=self.user,
            table=self.table,
            date=timezone.localdate() + timedelta(days=1),
            start_hour=time(18, 0),
            end_hour=time(20, 0),
            guests=4
        )
        data = {
            'date': timezone.localdate() + timedelta(days=1),
            'guests': 4,
            'time': ["19", "20"],
        }
        form = ReservationForm(data=data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "You already have a reservation during this time.",
            str(form.errors)
        )

class AvailabilitySearchTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass')

        # Create a table
        self.table = Table.objects.create(number=1, seats=4, slug='table-1')

        # Create a reservation to block hour 18
        Reservation.objects.create(
            user=self.user,
            table=self.table,
            date=timezone.localdate() + timedelta(days=1),
            start_hour=time(18, 0),
            end_hour=time(19, 0),
            guests=4
        )

    def test_availability_excludes_reserved_hours(self):
        # Store the field data in the session as the view expects
        url = reverse('reservations:table-availability')
        session = self.client.session
        session['field_data'] = {
            'date': (timezone.localdate() + timedelta(days=1)).isoformat(),
            'guests': '4',
            'requested_hours': ['18', '19', '20']  # hours we want to check
        }
        session.save()

        response = self.client.get(url)

        # Ensure the response is successful
        self.assertEqual(response.status_code, 200)

        # The reserved hour 18 should NOT appear
        self.assertNotContains(response, '18:00')

        # The unreserved hours should appear
        self.assertContains(response, '19:00')
        self.assertContains(response, '20:00')
        self.assertContains(response, '21:00')

class WaitlistFunctionTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='waitlistuser', password='pass')

    def test_add_to_waitlist_valid_and_duplicate(self):
        date_val = timezone.localdate() + timedelta(days=1)
        start_hour = time(19, 0)
        end_hour = time(20, 0)

        # First addition
        result1 = add_to_waitlist(
            user=self.user,
            date=date_val,
            start_hour=start_hour,
            end_hour=end_hour,
            guests=4
        )
        self.assertTrue(result1)
        self.assertEqual(WaitlistEntry.objects.count(), 1)

        # Second addition with different time
        result2 = add_to_waitlist(
            user=self.user,
            date=date_val,
            start_hour=time(20, 0),
            end_hour=time(21, 0),
            guests=4
        )
        self.assertTrue(result2)
        self.assertEqual(WaitlistEntry.objects.count(), 2)


class ReservationViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='viewuser', password='pass')
        self.table = Table.objects.create(number=1, seats=4, slug='table-1')
        self.client.force_login(self.user)

    def test_reservation_create_view(self):
        url = reverse('reservations:make-reservation')
        data = {
            'date': timezone.localdate() + timedelta(days=1),
            'guests': 4,
            'time': ["19", "22"],
            'notes': 'Test notes',
            'join_waitlist': False
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Reservation.objects.count(), 1)
        self.assertContains(response, 'Reservation created successfully.')