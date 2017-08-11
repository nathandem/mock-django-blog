from django.shortcuts import render, get_object_or_404,redirect
from django.utils import timezone
from blog.models import Post, Comment
from blog.forms import PostForm, CommentForm, PersonalityForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (TemplateView,ListView,
                                DetailView, CreateView,
                                UpdateView, DeleteView)

######### fun view, at /personality/) #############

def personality_form(request):
    form = PersonalityForm()
    return render(request, 'personality.html',{'form':form})

############# real blog ###########

class AboutView(TemplateView):
    template_name = 'about.html'


class PostListView(ListView):
    model = Post
    # fields = '__all__', in case we don't want to set up a custom query

    # get_queryset allows for a custom query in generic template views (list, detail, etc)
    def get_queryset(self):
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
        # this QuerySet makes sure the Post objects displayed have a published_date
        # return Post.objects.filter(published_date__isnull=True).order_by('-create_date')


class PostDetailView(DetailView):
    model = Post
    # fields = "__all__", if none, I guess all is displayed



# We inherit from 2 base classes
# LoginRequiredMixin makes sure only authenticated users can access our CreateView, like the auth decorator on function we saw before - should be first class called
class PostCreateView(LoginRequiredMixin,CreateView):
    # login_url & redirect_field_name seem to be for people not loged-in
    login_url = '/login/'
    # redirect_field_name = 'blog/post_detail.html'
    # I don't really get the redirect_field_name, so I comment it out
    form_class = PostForm
    model = Post #needed?
    # expects post_form.html (in templates/blog?)

    # the reason why we don't need to set a success_url is that we've defined get_absolute_url right in our models.py which is triggered when the form is successfully saved!
    # otherwise, we'd have done: success_url=reverse('success-url')


class PostUpdateView(LoginRequiredMixin,UpdateView):
    login_url = '/login/'
    # redirect_field_name = 'blog/post_detail.html'
    form_class = PostForm
    model = Post


class PostDeleteView(LoginRequiredMixin,DeleteView):
    # why no login_url & redirect_field_name here?
    model = Post
    # a success url is needed with this model
    # but with reverse lazy, so that redirect url is triggered as only when the person deletes a post
    # the default get_absolute_url defined in the Post model doesn't work
    success_url = reverse_lazy('post_list')


class DraftListView(LoginRequiredMixin,ListView):
    login_url = '/login/'
    # redirect_field_name = 'blog/post_list.html'
    model = Post

    def get_queryset(self):
        return Post.objects.filter(published_date__isnull=True).order_by('-create_date')


class CommentListView(LoginRequiredMixin,ListView):
    login_url = '/login/'
    # redirect_field_name = 'blog/post_list.html'
    model = Comment

    def get_queryset(self):
        return Comment.objects.filter(approved_comment=False).order_by('-create_date')


# that's the "Publish" button we see in post_detail.html, for posts which generate False on a post.published_date call
@login_required
def post_publish(request,pk):
    post = get_object_or_404(Post,pk=pk)
    post.publish()
    return redirect('post_detail',pk=pk)

################ COMMENTS ##################
# to my understanding, function views are more flexible than CBV, though they are slower for typical, frequent displays where we take things from a DB table and display on an html page
# function views work well for light actions, to which no html page is attached
# here, all the comment views always belong to an html page (from a Post template view)
# note: extensive use of the Post pk to connect the comment fct


# that's the comment_form.html
def add_comment_to_post(request,pk):
    # if object no found, go 404 - but when objects found keep that in the background (we don't display it)
    post = get_object_or_404(Post,pk=pk) # here Post is our model
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post # to connect the comment to the post - make the comment.post (ForeignKey) equals to the current post object (1st var of the function)
            comment.save()
            return redirect('post_detail',pk=post.pk)
    else:
        form = CommentForm()
    return render(request,'blog/comment_form.html',{'form':form})

# these 2 views are materialized in the form by the 2 buttons a superuser can see when some comments are not approved in the post_detail page
@login_required
def comment_approve(request,pk):
    comment = get_object_or_404(Comment,pk=pk)
    comment.approve()
    # when the comment is approved, we go to post_detail with the good pk
    # comment.post.pk means look at the Comment model, its post field (which is a ForeignKey from the Post model), the pk of the Post object the comment is connected to
    return redirect('post_detail',pk=comment.post.pk)

@login_required
def comment_remove(request,pk):
    comment = get_object_or_404(Comment,pk=pk)
    post_pk = comment.post.pk # we save the pk in a seperate var so that we can use it after the comment is deleted
    comment.delete()
    return redirect('post_detail',pk=post_pk)
