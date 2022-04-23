from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.loan.models import LoanApplication, LoanRepaymentSchedule, LoanStatus
from apps.loan.serializers import (LoanRepaymentScheduleSerializer,
                                   LoanSerializer, LoanStatusSerializer)


class LoanRequestView(APIView):
    permissions = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = LoanSerializer(data=request.data)
        if serializer.is_valid():
            loan_amount = serializer.validated_data['loan_amount']
            loan_term_in_weeks = serializer.validated_data['loan_term_in_weeks']
            loan_emi = loan_amount / loan_term_in_weeks
            loan_emi_remaining = loan_term_in_weeks
            serializer.save(user=request.user, status=LoanStatus.PENDING.value,
                            loan_emi_remaining=loan_emi_remaining, loan_emi=loan_emi)
            return Response(serializer.data)
        return Response(serializer.errors)


class LoanApplicationListView(APIView):
    permissions = [permissions.IsAuthenticated]

    def get(self, request):
        loan_applications = LoanApplication.objects.filter(user=request.user)
        serializer = LoanSerializer(loan_applications, many=True)
        return Response(serializer.data)


class LoanStatusView(APIView):
    permissions = [permissions.IsAuthenticated]

    def get(self, request, loan_id: int):
        loan_status = LoanApplication.objects.filter(loan_id=loan_id, user=request.user)
        if not loan_status.exists():
            return Response(status=404, data={'error': 'Loan Application not found'})
        serializer = LoanStatusSerializer(loan_status.first())
        return Response(serializer.data)


class LoanRepaymentScheduleListView(APIView):
    permissions = [permissions.IsAuthenticated]

    def get(self, request, loan_id: int):
        loan_status = LoanApplication.objects.filter(loan_id=loan_id, user=request.user)
        if not loan_status.exists():
            return Response(status=404, data={'error': 'Loan Application not found'})
        loan_status = loan_status.first()
        loan_repayment_schedules = LoanRepaymentSchedule.objects.filter(loan_id=loan_id)
        serializer = LoanRepaymentScheduleSerializer(loan_repayment_schedules, many=True)
        return Response(serializer.data)


class LoanRepaymentSubmitView(APIView):
    permissions = [permissions.IsAuthenticated]

    def post(self, request, loan_id: int):
        loan_application = LoanApplication.objects.filter(loan_id=loan_id, user=request.user)
        if not loan_application.exists():
            return Response(status=404, data={'error': 'Loan Application not found'})
        loan_application = loan_application.first()
        assert loan_application is not None
        if loan_application.status == LoanStatus.PAID.value:
            return Response(status=400, data={'error': 'Loan already paid'})
        if loan_application.status == LoanStatus.REJECTED.value:
            return Response(status=400, data={'error': 'Your loan is rejected'})
        if loan_application.status == LoanStatus.PENDING.value:
            return Response(status=400, data={'error': 'Loan Application is not approved yet'})
        loan_emi_paid_amount = request.data['loan_emi_paid_amount']
        if loan_emi_paid_amount < loan_application.loan_emi:
            return Response(status=400, data={'error': 'Loan EMI paid amount is less than EMI'})

        loan_repayment_schedules = LoanRepaymentSchedule.objects.filter(loan_id=loan_id,
                                                                        loan_emi_paid=False)
        if not loan_repayment_schedules.exists():
            return Response(status=404, data={'error': 'Loan Repayment Schedule not found'})
        loan_repayment_schedule = loan_repayment_schedules.first()
        assert loan_repayment_schedule is not None
        loan_repayment_schedule.loan_emi_paid = True
        loan_repayment_schedule.loan_emi_paid_on = timezone.now()
        loan_repayment_schedule.loan_emi_paid_amount = loan_emi_paid_amount
        loan_repayment_schedule.save()

        loan_application.loan_emi_remaining -= 1
        if loan_application.loan_emi_remaining == 0:
            loan_application.status = LoanStatus.PAID.value
        loan_application.save()

        return Response(status=200)


class LoanApplicationListAdminView(APIView):
    permissions = [permissions.IsAdminUser]

    def get(self, request):
        loan_applications = LoanApplication.objects.all()
        serializer = LoanSerializer(loan_applications, many=True)
        return Response(serializer.data)


class ApproveLoanView(APIView):
    permission_classes = (permissions.IsAdminUser,)

    def post(self, request, loan_id: int):
        loan_status = LoanApplication.objects.filter(loan_id=loan_id)
        if not loan_status.exists():
            return Response(status=404, data={'error': 'Loan Application not found'})
        lona_application_obj = loan_status.first()
        if lona_application_obj is not None and lona_application_obj.status != LoanStatus.PENDING.value:
            return Response(status=400, data={'error': f'Loan Application '
                                              f'is not in {LoanStatus.PENDING.value} status'})
        loan_status.update(status=LoanStatus.APPROVED.value)
        return Response(status=200, data={'message': 'Loan Approved'})
