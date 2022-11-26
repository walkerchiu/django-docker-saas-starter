from collections import defaultdict
from typing import List

from graphene_django import DjangoObjectType
from promise import Promise
from promise.dataloader import DataLoader

from account.models import Profile, User


def generate_loader_for_one_to_many(Type: DjangoObjectType, attr: str):
    class Loader(DataLoader):
        def batch_load_fn(self, keys: List[str]) -> Promise:
            results_by_ids = defaultdict(list)
            lookup = {f"{attr}__in": keys}

            for result in Type._meta.model.objects.filter(**lookup).iterator():
                results_by_ids[getattr(result, attr)].append(result)

            return Promise.resolve([results_by_ids.get(id, []) for id in keys])

    return Loader


def generate_loader_for_one_to_one(Type: DjangoObjectType, attr: str):
    class ProfileByIdLoader(DataLoader):
        def batch_load_fn(self, keys: List[str]):
            profiles = Profile.objects.in_bulk(keys)
            return Promise.resolve([profiles.get(key) for key in keys])

    class UserByIdLoader(DataLoader):
        def batch_load_fn(self, keys: List[str]):
            user = User.objects.in_bulk(keys)
            return Promise.resolve([user.get(key) for key in keys])

    class Loader(DataLoader):
        def batch_load_fn(self, keys: List[str]):
            def with_users(users: list):
                user_ids = [user.id for user in users]
                return ProfileByIdLoader().load_many(user_ids)

            return UserByIdLoader().load_many(keys).then(with_users)

    return Loader
