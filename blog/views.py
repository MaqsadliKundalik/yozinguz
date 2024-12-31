from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Post, Tag, Profile
from .forms import PostForm, ProfileEditForm
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import F, Q
from django.contrib.auth.models import User

def post_list(request):
    tag = request.GET.get('tag')
    if tag:
        post_list = Post.objects.filter(tags__slug=tag).order_by('-created_at')
    else:
        post_list = Post.objects.all().order_by('-created_at')
    
    paginator = Paginator(post_list, 9)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    tags = Tag.objects.all()
    return render(request, 'post_list.html', {
        'posts': posts,
        'tags': tags,
        'current_tag': tag
    })

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    viewed_posts = request.session.get('viewed_posts', [])
    
    if str(post.pk) not in viewed_posts:
        Post.objects.filter(pk=post.pk).update(views=F('views') + 1)
        viewed_posts.append(str(post.pk))
        request.session['viewed_posts'] = viewed_posts
        request.session.modified = True
        post.refresh_from_db()
    
    return render(request, 'post_detail.html', {'post': post})

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            
            tags = form.cleaned_data.get('tags', [])
            post.tags.set(tags)
            
            messages.success(request, 'Post muvaffaqiyatli yaratildi!')
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})

@login_required
def profile_view(request, username=None):
    if username:
        profile_user = get_object_or_404(User, username=username)
    else:
        profile_user = request.user
    
    posts = Post.objects.filter(author=profile_user).order_by('-created_at')
    
    total_views = sum(post.views for post in posts)
    
    total_likes = sum(post.likes.count() for post in posts)
    
    context = {
        'profile_user': profile_user,
        'posts': posts,
        'total_views': total_views,
        'total_likes': total_likes,
    }
    
    return render(request, 'profile.html', context)

@login_required
def profile_edit(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil muvaffaqiyatli yangilandi!')
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=profile)
    
    return render(request, 'profile_edit.html', {
        'form': form
    })

def about(request):
    return render(request, 'about.html')

def faq(request):
    return render(request, 'faq.html')

def contact(request):
    return render(request, 'contact.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!")
            return redirect('post_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if post.author != request.user:
        return HttpResponseForbidden("Siz faqat o'zingizning postlaringizni tahrirlay olasiz.")
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            
            tags = form.cleaned_data.get('tags', [])
            post.tags.set(tags)
            
            messages.success(request, 'Post muvaffaqiyatli yangilandi!')
            return redirect('post_detail', pk=post.pk)
    else:
        initial_tags = ' '.join([tag.name for tag in post.tags.all()])
        form = PostForm(instance=post, initial={'tags': initial_tags})
    
    return render(request, 'edit_post.html', {
        'form': form,
        'post': post
    })

@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if post.author != request.user:
        return HttpResponseForbidden("Siz faqat o'zingizning postlaringizni o'chira olasiz.")
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post muvaffaqiyatli o\'chirildi!')
        return redirect('post_list')
        
    return render(request, 'delete_post.html', {'post': post})

@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'total_likes': post.total_likes()
    })

def search_users(request):
    query = request.GET.get('q', '')
    users = []
    
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(profile__position__icontains=query)
        ).distinct()[:10]

    context = {
        'users': users,
        'query': query
    }
    
    return render(request, 'search_users.html', context)

def search_posts(request):
    query = request.GET.get('q', '')
    tag_slug = request.GET.get('tag', '')
    
    posts = Post.objects.all()
    
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts.filter(tags=tag)
    
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )
    else:
        posts = Post.objects.all()
    
    posts = posts.order_by('-created_at')[:10]
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'partial_posts.html', {'posts': posts})
    
    tags = Tag.objects.all()
    
    context = {
        'posts': posts,
        'query': query,
        'tags': tags,
        'current_tag': tag_slug
    }
    
    return render(request, 'search_posts.html', context)