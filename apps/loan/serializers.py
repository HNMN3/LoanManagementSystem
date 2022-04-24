from rest_framework import serializers

from apps.loan.models import LoanApplication, LoanRepaymentSchedule

default_extra_kwargs = {
    'loan_id': {'read_only': True},
    'loan_user': {'read_only': True},
    'created_at': {'read_only': True},
    'updated_at': {'read_only': True},
    'status': {'read_only': True},
    'loan_emi': {'read_only': True},
    'loan_emi_remaining': {'read_only': True},
}


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanApplication
        fields = ('loan_id', 'loan_user', 'loan_amount', 'loan_term_in_weeks',
                  'status', 'loan_emi', 'loan_emi_remaining', 'created_at', 'updated_at')
        extra_kwargs = default_extra_kwargs


class LoanStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanApplication
        fields = ('loan_id', 'status')
        extra_kwargs = default_extra_kwargs


class LoanRepaymentScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanRepaymentSchedule
        fields = ('loan_id', 'loan_emi_paid', 'loan_emi_due_date',
                  'loan_emi_paid_on', 'laon_emi_amount', 'loan_emi_paid_amount',)


class LoanSubmitRepaymentSerializer(serializers.Serializer):
    loan_emi_paid_amount = serializers.FloatField()
