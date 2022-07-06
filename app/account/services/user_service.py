from typing import Tuple
import uuid

from account.models import Profile, User


class UserService:
    def create_user(
        self, email: str, password: str, name: str = ""
    ) -> Tuple[bool, User]:
        user = User(
            email=email,
            name=name,
        )
        user.set_password(password)
        user.save()

        Profile.objects.create(user=user)

        return True, user

    def delete_user(self, id: uuid) -> bool:
        try:
            user = User.objects.only("id").get(pk=id)
        except User.DoesNotExist:
            return False
        else:
            user.delete()

        return True

    def undelete_user(self, id: uuid) -> bool:
        try:
            user = User.deleted_objects.only("id").get(pk=id)
        except User.DoesNotExist:
            return False
        else:
            user.undelete()

        return True
