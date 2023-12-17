from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie

from rest_framework import status

import configparser


class CSRFView(View):
    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return HttpResponse("204", status=204)


def version(request):
    if request.method == "GET":
        config = configparser.ConfigParser()
        config.read("version.ini", encoding="utf-8-sig")

        result = {
            "tag": config["default"]["tag"],
            "datetime": config["default"]["datetime"],
            "hash": config["default"]["hash"],
        }

        return JsonResponse(result, status=status.HTTP_200_OK)

    return JsonResponse(
        {"method": [request.method]}, status=status.HTTP_405_METHOD_NOT_ALLOWED
    )
