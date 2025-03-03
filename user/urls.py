# from django.urls import path
#
# from .payments.callback import PaymeCallBackAPIView
# from .views import GeneratePayLinkAPIView, GenerateClickLinkAPIView
#
# urlpatterns = [
#     path('payme/', GeneratePayLinkAPIView.as_view(), name='generate-pay-link'),
#     path('payments/merchant/', PaymeCallBackAPIView.as_view(), name='payme_callback'),
#     path('process/click/prepare/', GenerateClickLinkAPIView.as_view(), name='prepare'),
#     path('process/click/complete/', GenerateClickLinkAPIView.as_view(), name='complete'),
#     path('click/link/', GenerateClickLinkAPIView.as_view(), name='generate-click-link'),
# ]
