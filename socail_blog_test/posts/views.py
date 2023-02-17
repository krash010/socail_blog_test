from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from urllib import request
from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView
from django.urls import reverse_lazy
import urllib.request
from django.shortcuts import redirect
from django.views.decorators.cache import cache_page

from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm, FollowForm

@cache_page(20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_group = Post.objects.filter(group=group).order_by("-pub_date").all()
    paginator = Paginator(posts_group, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, "page": page, 'paginator': paginator})

@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
    else:
        form = PostForm()
    contex = {'form': form}
    return render(request, 'new.html', contex)


def profile(request, username):
    profil = get_object_or_404(User, username=username)
    usfol = get_object_or_404(User, username=request.user)
    profil_post = Post.objects.filter(author=profil).order_by("-pub_date").all()
    paginator = Paginator(profil_post, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = Follow.objects.filter(user=usfol, author=profil)
    return render(request, 'profile.html', {'profil': profil, 'page': page, 'paginator': paginator, 'following': following, 'username': username})
 
 
def post_view(request, username, post_id):
        pview = get_object_or_404(User, username=username)
        pview_get = Post.objects.filter(author=pview).get(id=post_id)
        pview_all = Post.objects.filter(author=pview).count()
        items = pview_get.comments.all()
        form = CommentForm()
        return render(request, 'post_view.html', {'pview_get': pview_get, 'pview': pview, 'pview_all': pview_all, 'items': items, 'username': username, 'form': form})


def post_edit(request, username, post_id):
        pedit = get_object_or_404(User, username=username)
        pedit_get = get_object_or_404(Post, author__username=pedit, id=post_id)
        if username != request.user.username:
            return redirect('post', username=username, post_id=post_id)
        else:
            if request.method == 'POST':
                form = PostForm(request.POST or None, files=request.FILES or None, instance=pedit_get)
                if form.is_valid():
                    post = form.save(commit=False)
                    post.save()
                    return redirect('post', username=username, post_id=post_id)
            else:
                form = PostForm(instance=pedit_get)
            contex = {'form': form, 'username': username, 'post_id': post_id, 'pedit_get': pedit_get}
            return render(request, 'new.html', contex)
        

def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию, 
    return render(
        request, 
        "misc/404.html", 
        {"path": request.path}, 
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post_com = get_object_or_404(User, username=username)
    post_com_id = get_object_or_404(Post, author__username=post_com, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.post = post_com_id
            post.save()
            return redirect('post', username=username, post_id=post_id)
    else:
        form = CommentForm()
    contex = {'form': form, 'post': post_com, 'post_id': post_com_id.id, 'username': username}
    return render(request, 'comments.html', contex)


@login_required
def follow_index(request):
    findx = get_object_or_404(User, username=request.user)
    fing = findx.follower.values_list('author')
    findx_get = Post.objects.filter(author__in=fing).order_by("-pub_date")
    paginator = Paginator(findx_get, 10)  # показывать по 10 записей на странице.
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    return render(request, "follow.html", {'page': page, 'paginator': paginator, 'findx': findx})

@login_required
def profile_follow(request, username):
    usfol = get_object_or_404(User, username=request.user)
    aufol = get_object_or_404(User, username=username)
    if username != request.user.username:
        form = FollowForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = usfol
            post.author = aufol
            post.save()
            return redirect('profile', username=username)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    usfol = get_object_or_404(User, username=request.user)
    aufol = get_object_or_404(User, username=username)
    Follow.objects.filter(user=usfol, author=aufol).delete()
    return redirect('profile', username=username)