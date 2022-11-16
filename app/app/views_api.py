from django.http import JsonResponse

from rest_framework import status

import configparser


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
