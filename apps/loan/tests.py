from django.contrib.auth.models import User
from django.test import TestCase

from apps.loan.models import LoanApplication, LoanRepaymentSchedule

# Create your tests here.


class LoanTestCase(TestCase):
    user = None

    def setUp(self) -> None:
        LoanRepaymentSchedule.objects.all().delete()
        LoanApplication.objects.all().delete()

    def get_user(self):
        if self.user is None:
            self.user = User.objects.create(username='testuser', password='12345')
        return self.user

    def test_loan_application_create_weekly_repayment_schedules(self):
        user = self.get_user()
        loan_term_in_weeks = 10
        laon_application = LoanApplication.objects.create(
            user=user,
            loan_amount=1000,
            loan_term_in_weeks=loan_term_in_weeks,
            loan_emi=100,
            loan_emi_remaining=loan_term_in_weeks
        )
        LoanApplication.create_weekly_repayment_schedules(laon_application)
        self.assertEqual(LoanRepaymentSchedule.objects.count(), loan_term_in_weeks)
