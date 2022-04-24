from django.urls import path

from apps.loan.views import (ApproveLoanView, LoanApplicationListView,
                             LoanRepaymentScheduleListView,
                             LoanRepaymentSubmitView, LoanRequestView,
                             LoanStatusView)

urlpatterns = [
    path('request/', LoanRequestView.as_view(), name='loan_request'),
    path('<int:loan_id>/status/', LoanStatusView.as_view(), name='loan_status'),
    path('<int:loan_id>/approve/', ApproveLoanView.as_view(), name='loan_approve'),
    path('<int:loan_id>/repayment/', LoanRepaymentScheduleListView.as_view(),
         name='loan_repayment_schedule'),
    path('<int:loan_id>/repayment/submit/', LoanRepaymentSubmitView.as_view(),
         name='loan_repayment_submit'),
    path('list/', LoanApplicationListView.as_view(), name='loan_list'),
]
