import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

from safedelete.models import SafeDeleteModel, SOFT_DELETE_CASCADE

from core.models import CreateUpdateDateAndSafeDeleteMixin
from role import ProtectedRole
from role.models import Role


class UserManager(BaseUserManager):
    pass


class User(CreateUpdateDateAndSafeDeleteMixin, AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(
        verbose_name="email address", max_length=255, unique=True, db_index=True
    )
    name = models.CharField(max_length=255, db_index=True)
    email_verified = models.BooleanField(default=False)
    roles = models.ManyToManyField(Role)

    objects = UserManager()

    _safedelete_policy = SOFT_DELETE_CASCADE

    USERNAME_FIELD = "email"

    class Meta:
        db_table = settings.APP_NAME + "_account_user"
        ordering = ["email"]

    def __str__(self):
        return str(self.id)

    @property
    def is_hq_user(self) -> bool:
        return self.roles.filter(slug=ProtectedRole.HQUser).exists()

    @property
    def is_admin(self) -> bool:
        return self.roles.filter(slug=ProtectedRole.Admin).exists()

    @property
    def is_collaborator(self) -> bool:
        return self.roles.filter(slug=ProtectedRole.Collaborator).exists()

    @property
    def is_customer(self) -> bool:
        return self.roles.filter(slug=ProtectedRole.Customer).exists()

    @property
    def is_manager(self) -> bool:
        return self.roles.filter(slug=ProtectedRole.Manager).exists()

    @property
    def is_member(self) -> bool:
        return self.roles.filter(slug=ProtectedRole.Member).exists()

    @property
    def is_owner(self) -> bool:
        return self.roles.filter(slug=ProtectedRole.Owner).exists()

    @property
    def is_partner(self) -> bool:
        return self.roles.filter(slug=ProtectedRole.Partner).exists()

    @property
    def is_staff(self) -> bool:
        return self.roles.filter(slug=ProtectedRole.Staff).exists()


class Profile(SafeDeleteModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, models.CASCADE)
    name = models.CharField(max_length=255, db_index=True, blank=True, null=True)
    mobile = models.CharField(max_length=255, db_index=True, blank=True, null=True)
    birth = models.DateField(null=True)

    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        db_table = settings.APP_NAME + "_account_profile"


class PasswordReset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, models.CASCADE)
    token = models.CharField(max_length=255, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = settings.APP_NAME + "_account_password_reset"
        index_together = (("user", "token", "created_at"),)
        ordering = ["id"]

    def __str__(self):
        return str(self.id)
