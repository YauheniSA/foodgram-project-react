from rest_framework.pagination import PageNumberPagination


class CustomLimitPagintaion(PageNumberPagination):
    page_size_query_param = 'limit'
