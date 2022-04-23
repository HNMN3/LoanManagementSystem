from enum import Enum

from django.db import models


class LoanStatus(Enum):
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


class LoanRepaymentSchedule(models.Model):
    loan_id = models.ForeignKey(LoanApplication, on_delete=models.CASCADE)
    loan_emi_paid = models.BooleanField(default=False)
    loan_emi_due_date = models.DateField()
    loan_emi_paid_on = models.DateField(default=None, null=True, blank=True)
    laon_emi_amount = models.FloatField()
    loan_emi_paid_amount = models.FloatField(default=None, null=True, blank=True)
