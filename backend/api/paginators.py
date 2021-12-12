from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPaginator(PageNumberPagination):
    '''Configures basic PageNumberPagination class allowing
    to set to an integer to limit the maximum page size the
    client may request.'''
    page_size_query_param = 'limit'
    page_size = 10
