from typing import Tuple

from django.db import connection

from organization.models import Organization


class TranslationHelper:
    def __init__(self):
        self.organization = Organization.objects.only("id").get(
            schema_name=connection.schema_name
        )
        self.language_code = self.organization.language_code
        self.language_support = self.organization.language_support

    def validate_translations_from_input(
        self, label: str, translations: list, required: bool = True
    ) -> Tuple[bool, str]:
        has_default_language = False

        if required and (translations is None or len(translations) == 0):
            return False, str(label) + ": The translations is required!"

        for index, translation in enumerate(translations):
            if translation["language_code"] not in self.language_support:
                return (
                    False,
                    str(label)
                    + f": The languageCode of the translation at index {index} is invalid!",
                )
            if translation["language_code"] == self.language_code:
                has_default_language = True

        if not has_default_language:
            return (
                False,
                str(label)
                + f": Missing data in default language! ({self.language_code})",
            )

        return True, None
