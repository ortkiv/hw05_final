from django.urls import reverse

URL_TEMPLATES = {
    reverse("posts:index"): "posts/index.html",
    reverse(
        "posts:group_list",
        kwargs={"slug": "slug"}): "posts/group_list.html",
    reverse(
        "posts:profile",
        kwargs={"username": "auth"}): "posts/profile.html",
    reverse(
        "posts:post_detail",
        kwargs={"post_id": 1}): "posts/post_detail.html",
    reverse(
        "posts:post_edit",
        kwargs={"post_id": 1}): "posts/create_post.html",
    reverse("posts:post_create"): "posts/create_post.html",
    "/unexisting_page/": "core/404.html"
}
