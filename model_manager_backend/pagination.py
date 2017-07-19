from rest_framework.pagination import PageNumberPagination as DefaultPageNumberPagination


class PageNumberPagination(DefaultPageNumberPagination):

    page_size_query_param = "page_size"
    max_page_size = 9999

    def get_page_size(self, request):
        if self.page_size_query_param and self.max_page_size and request.query_params.get(self.page_size_query_param) == 'max':
            return self.max_page_size
        return super(PageNumberPagination, self).get_page_size(request)

