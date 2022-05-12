from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpRequest


def paginate(request: HttpRequest, post_list):
    """Выполняет функцию 'пажинации'.
    --------
        Параметры:
            request: HttpRequest
                обьект запроса.
    --------
        Константы:
            LIMIT_POSTS
                константа, хранящая кол-во постов, разммещаемых
                на странице. Импортируется из settings.
    """
    paginator = Paginator(post_list, settings.LIMIT_POSTS)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
