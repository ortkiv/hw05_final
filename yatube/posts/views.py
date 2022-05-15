from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.forms import SlugField
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post
from .utils import paginate

User = get_user_model()


def index(request: HttpRequest) -> HttpResponse:
    """Возвращает объект ответа HttpResponse
    и собирает главную страницу index.html.

    Основное предназначение - прочитать обьект запроса
    и возвратить обьект ответа в ввиде HttpResponse
    и собрать главную страницу index.html.
    --------
        Параметры:
            request: HttpRequest
                обьект запроса.
    """
    post_list = Post.objects.select_related('author', 'group')
    page_obj = paginate(request, post_list)
    return render(request, "posts/index.html", {"page_obj": page_obj})


def group_posts(request: HttpRequest, slug: SlugField) -> HttpResponse:
    """Возвращает объект ответа HttpResponse
    и собирает страницу с записями по группам group_list.html.

    Основное предназначение - прочитать обьект запроса
    и возвратить обьект ответа в ввиде HttpResponse
    и собрать страницу group_list.html.
    --------
        Параметры:
            request: HttpRequest
                обьект запроса
            slug: SlugField
                slug-строка содержащая название запрашиваемой группы.
    """
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author', 'group')
    page_obj = paginate(request, post_list)
    return render(
        request,
        "posts/group_list.html",
        {"group": group, "page_obj": page_obj}
    )


def profile(request: HttpRequest, username: str) -> HttpResponse:
    """Возвращает объект ответа HttpResponse
    и собирает страницу с записями конкретного
    пользователя profile.html.

    Основное предназначение - прочитать обьект запроса
    и возвратить обьект ответа в ввиде HttpResponse
    и собрать страницу profile.html.

    --------
        Параметры:
            request: HttpRequest
                обьект запроса
            username: str
                строка содержащая логин пользователя
                запрашиваемой страницы.
    """
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related("author", "group")
    following = author.following.select_related("user", "author")
    page_obj = paginate(request, post_list)
    return render(
        request,
        "posts/profile.html",
        {"author": author, "page_obj": page_obj, "following": following}
    )


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    """Возвращает объект ответа HttpResponse
    и собирает страницу конкретной записи post_detail.html.

    Основное предназначение - прочитать обьект запроса
    и возвратить обьект ответа в ввиде HttpResponse
    и собрать страницу post_detail.html.
    --------
        Параметры:
            request: HttpRequest
                обьект запроса
            post_id: int
                переменная, содержащая primary key
            запрашиваемого поста.
    """
    post = get_object_or_404(Post, pk=post_id)
    form_comment = CommentForm()
    comments = post.comments.all
    return render(
        request, "posts/post_detail.html",
        {"post": post, "form_comment": form_comment, "comments": comments}
    )


@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    """Возвращает объект ответа HttpResponse
    и собирает страницу создания новой записи create.html.

    Основное предназначение - прочитать обьект запроса
    и возвратить обьект ответа в ввиде HttpResponse
    и собрать страницу create.html.
    --------
        Параметры:
            request: HttpRequest
                обьект запроса.
    """
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(request, "posts/create_post.html", {"form": form})

    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect("posts:profile", request.user)


@login_required
def post_edit(request: HttpRequest, post_id: int) -> HttpResponse:
    """Возвращает объект ответа HttpResponse
    и собирает страницу редактирования записи.

    Основное предназначение - прочитать обьект запроса
    и возвратить обьект ответа в ввиде HttpResponse
    и собрать страницу редактирования записию
    --------
        Параметры:
            request: HttpRequest
                обьект запроса.
            post_id: int
                переменная, содержащая primary key
            запрашиваемого поста.
    """
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect("posts:post_detail", post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        post = form.save()
        return redirect("posts:post_detail", post_id)
    return render(
        request,
        "posts/create_post.html",
        {
            "is_edit": True,
            "form": form,
            "post_id": post_id
        }
    )


@login_required
def add_comment(request: HttpRequest, post_id: int) -> HttpResponse:
    """Добавляет коментарий к запрашиваемому посту
    --------
        Параметры:
            request: HttpRequest
                обьект запроса
                post_id: int
                переменная, содержащая primary key
            коментируемого поста.
    """
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request: HttpRequest) -> HttpResponse:
    """Возвращает объект ответа HttpResponse
    и собирает главную страницу follow_index.html.

    Основное предназначение - прочитать обьект запроса
    и возвратить обьект ответа в ввиде HttpResponse
    и собрать страницу follow_index.html.
    --------
        Параметры:
            request: HttpRequest
                обьект запроса.
    """
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = paginate(request, post_list)
    return render(
        request, "posts/follow.html", {"page_obj": page_obj})


@login_required
def profile_follow(request, username):
    """Подписка на автора."""
    if username != request.user.username:
        author = get_object_or_404(User, username=username)
        if Follow.objects.filter(user=request.user, author=author).exists():
            return redirect("posts:profile", username)
        Follow.objects.create(user=request.user, author=author)
        return redirect("posts:profile", username)
    return redirect("posts:profile", username)


@login_required
def profile_unfollow(request, username):
    """Отписка от автора."""
    author = get_object_or_404(User, username=username)
    follow = get_object_or_404(Follow, user=request.user, author=author)
    follow.delete()
    return redirect("posts:profile", username)
