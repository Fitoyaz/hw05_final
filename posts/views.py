from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm

from .models import Group, Post, Comment, Follow


def index(request):
    latest = Post.objects.all()
    paginator = Paginator(latest, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'group.html',
                  {'page': page, 'group': group, 'posts': posts})


@login_required
def new_post(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if request.method == 'POST':
        form = PostForm(request.POST or None,
                        files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
    return render(request, 'new.html', {'form': form})


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    post_list = profile.posts.all()
    counter_post = post_list.count()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = (request.user.is_authenticated and
                 Follow.objects.filter(user=request.user,
                                       author=profile).exists())

    return render(request, 'profile.html',
                  {'profile': profile, 'counter_post': counter_post,
                   'page': page,
                   'following': following})


def post_view(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post)
    form = CommentForm()
    context = {
        'post': post,
        'profile': profile,
        'comments': comments,
        'form': form,
    }
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
        return redirect('post', username=post.author.username, post_id=post.id)

    return render(request, 'new.html', {'form': form, 'post': post})


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def add_comment(request, username, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, id=post_id, author=request.user)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('post', username, post_id)


@login_required
def follow_index(request):
    """Страница постов подписанных авторов."""
    post_follower = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_follower, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html',
                  {'page': page, 'paginator': paginator})


@login_required
def profile_follow(request, username):
    """Подписка на автора."""
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user_id=request.user.id,
                                     author_id=author.id)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Отписка от автора."""
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user_id=request.user.id,
                                   author_id=author.id)
    follow.delete()
    return redirect('profile', username=username)
