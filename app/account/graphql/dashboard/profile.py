from django.core.exceptions import ValidationError
from django.db import transaction

from graphene import ResolveInfo
import graphene

from account.graphql.dashboard.types.profile import ProfileNode
from account.models import Profile
from core.decorators import strip_input
from core.relay.connection import DjangoFilterConnectionField


class UpdateProfile(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String()
        mobile = graphene.String()
        birth = graphene.DateTime()

    success = graphene.Boolean()
    profile = graphene.Field(ProfileNode)

    @classmethod
    @strip_input
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input):
        name = input["name"] if "name" in input else None
        mobile = input["mobile"] if "mobile" in input else None
        birth = input["birth"] if "birth" in input else None

        try:
            profile = info.context.user.profile
            profile.name = name
            profile.mobile = mobile
            profile.birth = birth
            profile.save()
        except Profile.DoesNotExist:
            raise ValidationError("Can not find this profile!")

        return UpdateProfile(success=True, profile=profile)


class ProfileMutation(graphene.ObjectType):
    profile_update = UpdateProfile.Field()


class ProfileQuery(graphene.ObjectType):
    profile = graphene.relay.Node.Field(ProfileNode)
    profiles = DjangoFilterConnectionField(
        ProfileNode,
        orderBy=graphene.List(of_type=graphene.String),
        page_number=graphene.Int(),
        page_size=graphene.Int(),
    )
