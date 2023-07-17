from collections import defaultdict
from typing import List

from graphene_django import DjangoObjectType
from promise import Promise
from promise.dataloader import DataLoader


def generate_loader_for_one_to_many(Type: DjangoObjectType, attr: str):
    class Loader(DataLoader):
        def batch_load_fn(self, keys: List[str]) -> Promise:
            results_by_id_list = defaultdict(list)
            lookup = {f"{attr}__in": keys}

            for result in Type._meta.model.objects.filter(**lookup).iterator():
                results_by_id_list[getattr(result, attr)].append(result)

            return Promise.resolve([results_by_id_list.get(id, []) for id in keys])

    return Loader
