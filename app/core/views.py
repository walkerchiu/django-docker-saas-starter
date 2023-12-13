import re

from django.conf import settings
from django.db import connection
from django.http.request import HttpRequest

from graphene_django.views import GraphQLView


class ErrorGraphQLView(GraphQLView):
    def execute_graphql_request(
        self,
        request: HttpRequest,
        data,
        query,
        variables,
        operation_name,
        show_graphiql,
    ):
        # print(request.geolocation)

        result = super().execute_graphql_request(
            request, data, query, variables, operation_name, show_graphiql
        )
        print(request)
        print(request.META.get("HTTP_X_FORWARDED_FOR"))
        print(request.META.get("REMOTE_ADDR"))
        print(request.headers)
        print(data)
        print(query)
        print(variables)
        print(operation_name)
        print(show_graphiql)
        print(connection.schema_name)
        result = super().execute_graphql_request(
            request, data, query, variables, operation_name, show_graphiql
        )
        print(result)

        if not settings.PLAYGROUND and result.errors:
            for error in result.errors:
                try:
                    raise error.original_error
                except Exception as e:
                    for arg in e.args:
                        try:
                            if "IntegrityError" in arg and "is not present" in str(
                                error
                            ):
                                string = re.search("Key \\((.*)\\)=", str(error)).group(
                                    1
                                )
                                if string:
                                    string = re.search("(.*)_", string).group(1)
                                result.errors = ["Can not find this " + string + "!"]
                        except TypeError:
                            pass
        return result
