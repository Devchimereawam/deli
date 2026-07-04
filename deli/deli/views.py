from django.http import JsonResponse


def health(request):

    return JsonResponse({

        "status": "healthy",

        "service": "Deli",

        "version": "1.0.0"

    })