from graphene_django.filter import DjangoFilterConnectionField
import graphene


class DjangoFilterConnectionField(DjangoFilterConnectionField):
    @classmethod
    def resolve_queryset(
        cls,
        connection,
        iterable,
        info,
        args,
        filtering_args,
        filterset_class,
    ):
        qs = super().resolve_queryset(
            connection, iterable, info, args, filtering_args, filterset_class
        )

        total_count = qs.count()

        page_number = args.get("page_number", 1)
        page_size = args.get("page_size", 25)

        start = (page_number - 1) * page_size
        end = start + page_size

        sliced_qs = qs[start:end]
        sliced_qs.total_count = total_count

        return sliced_qs


class ExtendedConnection(graphene.relay.Connection):
    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, node=None, name=None, **options):
        result = super().__init_subclass_with_meta__(node=node, name=name, **options)
        cls._meta.fields["total_count"] = graphene.Field(
            type_=graphene.Int,
            name="totalCount",
            description="Number of items in the queryset.",
            required=True,
            resolver=cls.resolve_total_count,
        )
        return result

    def resolve_total_count(self, *_) -> int:
        return getattr(self.iterable, "total_count", self.iterable.count())
