from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from patients.models import Owner, Patient
from appointments.models import Appointment
from billing.models import Invoice

User = get_user_model()

class VetCareWorkflowTests(TestCase):
    def setUp(self):
        # 1. Staff Setup
        self.admin = User.objects.create_user(username='admin_test', password='password123', role='ADMIN')
        self.receptionist = User.objects.create_user(username='rec_test', password='password123', role='RECEPTIONIST')

        # 2. Owner & Patient Setup
        self.owner = Owner.objects.create(first_name='Ali', last_name='Khan', phone='03001234567')
        self.patient = Patient.objects.create(owner=self.owner, name='Max', species=Patient.Species.DOG)

    def test_patient_owner_relationship(self):
        """Owner and patient link properly"""
        self.assertEqual(self.patient.owner.get_full_name(), 'Ali Khan')
        self.assertEqual(self.owner.patients.count(), 1)

    def test_daily_queue_token_auto_increment(self):
        """Daily queue tokens increment sequentially (#1, #2)"""
        today = timezone.now().date()
        appt1 = Appointment.objects.create(
            patient=self.patient,
            scheduled_date=today,
            status=Appointment.Status.WAITING,
            reason="Checkup 1"
        )
        self.assertEqual(appt1.token_number, 1)

        appt2 = Appointment.objects.create(
            patient=self.patient,
            scheduled_date=today,
            status=Appointment.Status.WAITING,
            reason="Checkup 2"
        )
        self.assertEqual(appt2.token_number, 2)

    def test_invoice_calculation(self):
        """Invoices calculate balance and status properly"""
        invoice = Invoice.objects.create(
            patient=self.patient,
            owner=self.owner,
            billed_by=self.receptionist,
            subtotal=2000.00,
            discount=200.00,
            paid_amount=1500.00
        )
        # Total = 2000 - 200 = 1800 | Balance = 1800 - 1500 = 300
        self.assertEqual(invoice.total_amount, 1800.00)
        self.assertEqual(invoice.balance_due, 300.00)
        self.assertEqual(invoice.status, Invoice.Status.PARTIALLY_PAID)

# Create your tests here.
