from django.utils import timezone
from rest_framework import permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.loan.models import LoanApplication, LoanRepaymentSchedule, LoanStatus
from apps.loan.serializers import (LoanRepaymentScheduleSerializer,
                                   LoanSerializer, LoanStatusSerializer,
                                   LoanSubmitRepaymentSerializer)


class LoanBaseApiView(APIView):
    """
    This is the base class for all loan related views. It provides the access policy for the views.
    It also provides the pagination for the views.
    """
    pagination_class = PageNumberPagination

    def get_paginated_response(self, queryset, serializer, request):
        page = self.pagination_class()
        page_data = page.paginate_queryset(queryset, request)
        serializer = serializer(page_data, many=True)
        return page.get_paginated_response(serializer.data)

    def filter_with_access_policy(self, queryset, request):
        if request.user.is_superuser:
            return queryset
        return queryset.filter(user=request.user)


class LoanRequestView(LoanBaseApiView):
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


class LoanApplicationListView(LoanBaseApiView):
    permissions = [permissions.IsAuthenticated]

    def get(self, request):
        loan_applications = LoanApplication.objects.all()
        loan_applications = self.filter_with_access_policy(loan_applications, request)
        return self.get_paginated_response(loan_applications, LoanSerializer, request)


class LoanStatusView(LoanBaseApiView):
    permissions = [permissions.IsAuthenticated]

    def get(self, request, loan_id: int):
        loan_application = LoanApplication.objects.filter(loan_id=loan_id)
        loan_application = self.filter_with_access_policy(loan_application, request)
        if not loan_application.exists():
            return Response(status=404, data={'error': 'Loan Application not found'})
        serializer = LoanStatusSerializer(loan_application.first())
        return Response(serializer.data)


class LoanRepaymentScheduleListView(LoanBaseApiView):
    permissions = [permissions.IsAuthenticated]

    def get(self, request, loan_id: int):
        loan_application = LoanApplication.objects.filter(loan_id=loan_id)
        loan_application = self.filter_with_access_policy(loan_application, request)
        if not loan_application.exists():
            return Response(status=404, data={'error': 'Loan Application not found'})
        loan_application = loan_application.first()
        loan_repayment_schedules = LoanRepaymentSchedule.objects.filter(loan_id=loan_id)
        return self.get_paginated_response(loan_repayment_schedules, LoanRepaymentScheduleSerializer,
                                           request)


class LoanRepaymentSubmitView(LoanBaseApiView):
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

        serializer = LoanSubmitRepaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=400, data={'error': serializer.errors})

        loan_emi_paid_amount = serializer.validated_data['loan_emi_paid_amount']
        if loan_emi_paid_amount < loan_application.loan_emi:
            return Response(status=400, data={'error': 'Loan EMI paid amount is less than weekly EMI'})

        loan_repayment_schedules = LoanRepaymentSchedule.objects.filter(loan_id=loan_application,
                                                                        loan_emi_paid=False)
        if not loan_repayment_schedules.exists():
            return Response(status=404, data={'error': 'Loan Repayment Schedule not found'})
        loan_repayment_schedule = loan_repayment_schedules.order_by('loan_emi_due_date').first()
        assert loan_repayment_schedule is not None
        loan_repayment_schedule.loan_emi_paid = True
        loan_repayment_schedule.loan_emi_paid_on = timezone.now()
        loan_repayment_schedule.loan_emi_paid_amount = loan_emi_paid_amount
        loan_repayment_schedule.save()

        loan_application.loan_emi_remaining -= 1
        if loan_application.loan_emi_remaining == 0:
            loan_application.status = LoanStatus.PAID.value
        loan_application.save()

        return Response(status=200, data={
            'success': f'Loan EMI: {loan_repayment_schedule.loan_emi_due_date} paid successfully'
        })


class ApproveLoanView(APIView):
    permission_classes = (permissions.IsAdminUser,)

    def post(self, request, loan_id: int):
        loan_application = LoanApplication.objects.filter(loan_id=loan_id)
        if not loan_application.exists():
            return Response(status=404, data={'error': 'Loan Application not found'})
        lona_application_obj = loan_application.first()
        assert lona_application_obj is not None
        if lona_application_obj.status != LoanStatus.PENDING.value:
            return Response(status=400, data={'error': f'Loan Application '
                                              f'is not in {LoanStatus.PENDING.value} status'})
        LoanApplication.create_weekly_repayment_schedules(lona_application_obj)
        loan_application.update(status=LoanStatus.APPROVED.value)

        return Response(status=200, data={'message': 'Loan Approved'})
