from django.contrib.auth import get_user_model


class AuthBackend:
    def authenticate(self, request, endpoint: str, email: str, password: str, **kwargs):
        try:
            user = get_user_model().objects.get(endpoint=endpoint, email=email)
        except get_user_model().DoesNotExist:
            return None

        if user.check_password(password):
            return user

        return None

    def get_user(self, user_id):
        try:
            return get_user_model().objects.get(pk=user_id)
        except get_user_model().DoesNotExist:
            return None
