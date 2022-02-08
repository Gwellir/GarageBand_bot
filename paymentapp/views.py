from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from paymentapp.systems.liqpay_system import LiqpayClient


@method_decorator(csrf_exempt, name="dispatch")
class LiqPayCallbackView(View):
    def post(self, request, *args, **kwargs):
        lq_client = LiqpayClient()
        data = request.POST.get("data")
        signature = request.POST.get("signature")

        if lq_client.verify(data, signature):
            print("callback is valid")
            lq_client.process(data)

        return HttpResponse()
