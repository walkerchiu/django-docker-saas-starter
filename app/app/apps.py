from django.apps import AppConfig


class MyAppConfig(AppConfig):
    name = "app"

    def ready(self):
        from account import receivers

        receivers.signin_fail
        receivers.signin_success
