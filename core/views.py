from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from itertools import chain
import random

from core.models import Profile, Post, LikePost, Follower


@login_required()
def index(request):
    current_user = User.objects.get(id=request.user.id)
    current_user_profile = Profile.objects.filter(user=current_user)
    user_following_list = []
    feed = []

    user_following = Follower.objects.filter(follower=request.user.username)
    for users in user_following:
        user_following_list.append(users.user)
    for username in user_following_list:
        feed_lists = Post.objects.filter(user=username)
        feed.append(feed_lists)

    feed_list = list(chain(*feed))

    # user suggestion starts
    all_users = User.objects.all()
    user_following_all = []
    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)
    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    final_suggestions_list = [x for x in list(new_suggestions_list) if (x not in list(current_user_profile))]
    random.shuffle(final_suggestions_list)
    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)
    for ids in username_profile:
        profile_lists = Post.objects.filter(user=ids)
        username_profile_list.append(profile_lists)
    suggestions_username_profile_list = list(chain(*username_profile_list))
    context = {"current_user_profile": current_user_profile, "posts": feed_list,
               'suggestions_username_profile_list': suggestions_username_profile_list[:5]}
    return render(request, "index.html", context)


@login_required()
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        if request.FILES.get('image'):
            image = request.FILES.get('image')
        else:
            image = user_profile.profile_img

        bio = request.POST['bio']
        location = request.POST['location']

        user_profile.profile_img = image
        user_profile.location = location
        user_profile.bio = bio
        user_profile.save()
        return redirect('settings')
    context = {'user_profile': user_profile}
    return render(request, 'setting.html', context)


@login_required()
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    if request.method == "POST":
        username = request.POST['query']
        username_object = User.objects.filter(username__icontains=username)
        username_profile = []
        username_profile_list = []
        for users in username_object:
            username_profile.append(users)
        for profile in username_profile:
            profile_lists = Profile.objects.filter(id_user=profile.id)
            username_profile_list.append(profile_lists)
        username_profile_list = list(chain(*username_profile_list))
    username_profile_list = []
    context = {'user_profile': user_profile, 'username_profile_list': username_profile_list}
    return render(request, 'search.html', context)


@login_required()
def follow(request):
    if request.method == "POST":
        follower = request.POST['follower']
        user = request.POST['user']
        user_object = User.objects.get(username=user)

        if Follower.objects.filter(follower=follower, user=user_object).first():
            delete_follower = Follower.objects.get(follower=follower, user=user_object)
            delete_follower.delete()
            return redirect("profile", pk=user)
        else:
            new_follower = Follower.objects.create(follower=follower, user=user_object)
            new_follower.save()
            return redirect("profile", pk=user)
    else:
        return redirect('settings')


@login_required()
def upload(request):
    if request.FILES:
        image = request.FILES.get('upload_image')
        user = request.user
        caption = request.POST['caption']
        new_post = Post.objects.create(image=image, user=user, caption=caption)
        new_post.save()
        messages.info(request, "Image has been posted successfully")
        return redirect('index')
    else:
        return redirect('index')


@login_required()
def like_post(request):
    user = request.user
    post_id = request.GET.get("post_id")
    post = Post.objects.get(id=post_id)
    like_filter = LikePost.objects.filter(post_id=post_id, user=user).first()
    if like_filter is None:
        new_like = LikePost.objects.create(post_id=post, user=user)
        new_like.save()
        post.no_of_likes += 1
        post.save()
        return redirect('/')
    else:
        like_filter.delete()
        post.no_of_likes -= 1
        post.save()
        return redirect('/')


@login_required()
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=user_object)
    count_user_posts = user_posts.count()
    follower = request.user
    if Follower.objects.filter(follower=follower, user=user_object).first():
        button_text = "Unfollow"
    else:
        button_text = "Follow"
    user_followers = Follower.objects.filter(user=user_object).count()
    user_following = Follower.objects.filter(follower=pk).count()
    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'count_user_posts': count_user_posts,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following
    }
    return render(request, 'profile.html', context)


def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, "This email already taken")
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, "This username already taken")
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                # Log user in and redirect to settings page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                # create Profile object for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
        else:
            messages.error(request, "Password Not Matching!")
            return redirect('signup')
    else:
        return render(request, 'signup.html')


def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if not user is None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid!')
            return redirect('signin')
    else:
        return render(request, 'signin.html')


@login_required()
def logout(request):
    auth.logout(request)
    messages.info(request, "You are logged out!")
    return redirect('signin')
