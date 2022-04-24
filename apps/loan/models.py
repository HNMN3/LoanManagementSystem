from datetime import datetime, timedelta
from enum import Enum

from django.db import models


class LoanStatus(Enum):
    """
    Enum for loan status.
    """

    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    PAID = 'PAID'


class LoanApplication(models.Model):
    loan_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    loan_amount = models.FloatField()
    loan_term_in_weeks = models.IntegerField()
    status = models.CharField(max_length=20, default=LoanStatus.PENDING.value)
    loan_emi = models.FloatField()
    loan_emi_remaining = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    @property
    def loan_user(self):
        return self.user.username

    @classmethod
    def create_weekly_repayment_schedules(cls, loan_application_obj: 'LoanApplication') -> None:
        """
        Create weekly repayment schedules for a loan application.

        Args:
            loan_application_obj (LoanApplication): Loan application object.
        """
        loan_term_in_weeks = loan_application_obj.loan_term_in_weeks
        loan_emi = loan_application_obj.loan_emi
        loan_emi_due_date = datetime.today()

        for i in range(loan_term_in_weeks):
            loan_emi_due_date = loan_emi_due_date + timedelta(weeks=1)
            LoanRepaymentSchedule.objects.create(
                loan_id=loan_application_obj,
                loan_emi_paid=False,
                loan_emi_due_date=loan_emi_due_date,
                laon_emi_amount=loan_emi
            )


class LoanRepaymentSchedule(models.Model):
    loan_id = models.ForeignKey(LoanApplication, on_delete=models.CASCADE)
    loan_emi_paid = models.BooleanField(default=False)
    loan_emi_due_date = models.DateField()
    loan_emi_paid_on = models.DateField(default=None, null=True, blank=True)
    laon_emi_amount = models.FloatField()
    loan_emi_paid_amount = models.FloatField(default=None, null=True, blank=True)
