from django.conf import settings

from graphql.backend.core import GraphQLCoreBackend


def measure_depth(selection_set, level=1):
    max_depth = level
    for field in selection_set.selections:
        if field.selection_set:
            new_depth = measure_depth(field.selection_set, level=level + 1)
            if new_depth > max_depth:
                max_depth = new_depth
    return max_depth


class DepthAnalysisBackend(GraphQLCoreBackend):
    def document_from_string(self, schema, document_string):
        document = super().document_from_string(schema, document_string)
        ast = document.document_ast
        for definition in ast.definitions:
            if len(definition.selection_set.selections) > settings.GRAPHENE_MAX_BREADTH:
                raise Exception("Query is too complex")

            depth = measure_depth(definition.selection_set)
            if depth > settings.GRAPHENE_MAX_DEPTH:
                raise Exception("Query is too nested")

        if not settings.PLAYGROUND:
            ast = document.document_ast
            for definition in ast.definitions:
                if (
                    len(definition.selection_set.selections)
                    > settings.GRAPHENE_MAX_BREADTH
                ):
                    raise Exception("Query is too complex")

                depth = measure_depth(definition.selection_set)
                if depth > settings.GRAPHENE_MAX_DEPTH:
                    raise Exception("Query is too nested")

        return document
