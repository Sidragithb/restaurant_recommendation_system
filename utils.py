# restaurant_recommendation_system/utils.py
from django.db import IntegrityError
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    """
    Convert Django/DB errors into clean DRF JSON, e.g.
    {
      "phone_number": ["Phone number already registered."]
    }
    """
    # Let DRF handle ValidationError etc.
    response = exception_handler(exc, context)
    if response is not None:
        return response

    # Catch DB unique errors (e.g., duplicate phone_number)
    if isinstance(exc, IntegrityError):
        # You can parse the message if you want, but keep it generic & friendly
        data = {"detail": "A record with the same unique field already exists."}

        # Try to give a nicer field-specific hint
        msg = str(exc).lower()
        if "phone_number" in msg:
            data = {"phone_number": ["Phone number already registered."]}
        elif "email" in msg:
            data = {"email": ["Email already registered."]}
        elif "username" in msg:
            data = {"username": ["Username already exists."]}

        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    # Fallback: generic JSON error
    return Response({"detail": "Server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
