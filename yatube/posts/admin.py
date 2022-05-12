from django.contrib import admin

from .models import Comment, Follow, Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group'
    )
    list_editable = ('group', 'text')
    search_fields = ('text',)
    list_filter = ('pub_date', 'group')
    empty_value_display = '-пусто-'


@admin.register(Group)
class PostGroup(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'slug',
        'description'
    )
    list_editable = ('title', 'slug', 'description')
    search_fields = ('title',)
    list_filter = ('title',)
    empty_value_display = '-пусто-'


@admin.register(Comment)
class PostComment(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'created',
        'author',
        'post'
    )
    list_editable = ("text",)
    search_fields = ("text",)
    list_filter = ("created", "author")
    empty_value_display = '-пусто-'


@admin.register(Follow)
class PostFollow(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'author'
    )
    search_fields = ("author",)
    list_filter = ("user", "author")
    empty_value_display = '-пусто-'
