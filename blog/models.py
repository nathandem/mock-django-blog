from django.db import models
from django.utils import timezone
from django.core.urlresolvers import reverse

class Post(models.Model):
    # only a superuser (authorized) can be an author
    author = models.ForeignKey('auth.User') # no related_name arg to this ForeignKey because we won't reference it in our methods
    title = models.CharField(max_length=64)
    text = models.TextField()
    create_date = models.DateTimeField(default=timezone.now) # Django just wants timezone.now - not timezone.now(), as opposed to in the publish method
    published_date = models.DateTimeField(blank=True,null=True)
    # seems like data validations work in the background
    # blank=True means the field can be left empty
    # null=True means empty rows in the field will be filled by ""null"" - note: if all fields accept null for empty values, CharField and TextField don't
    # it's common to add blank=True and null=True together

    # that a logic method to handle published_date - not in the field def because it's not during the creation of the object
    def publish(self):
        self.published_date = timezone.now()
        self.save() # a self.save() is always needed whenever we act on a model

    def approve_comments(self):
        return self.comments.filter(approved_comment=True) # that's a normal QuerySet, we filter against the approved_comment field
        # self.comments.filter() > "comments" a the ForeignKey of this model
        # assume there's a related_name="comments"

    # surprizing that we even create display logic as deep as in the model!
    # enables not to set up GET and POST templates/actions in views.py
    def get_absolute_url(self):
        return reverse("post_detail",kwargs={"pk":self.pk})
        # after the post is created, go "post_detail" of the current primary key (see urls.py for the specifics of how pk and post_detail are positioned)

    def __str__(self):
        return self.title

class Comment(models.Model):
    # ForeignKey means 1 to many relation. The side with the ForeignKey is the many, the other the one = one post may have many comments.
    post = models.ForeignKey('blog.Post', related_name="comments") # avoid to do post.comment_set.all() to get the Comment objects
    author = models.CharField(max_length=56)
    text = models.TextField()
    create_date = models.DateTimeField(default=timezone.now)
    approved_comment = models.BooleanField(default=False)
    # write here how an auth.User can approve a comment
    # 1) the approve() method change the approved_comment field to True
    # - it's possible as we're working object by object
    # 2) a User with proper authorization and loged-in can run this method
    # how?

    def approve(self):
        self.approved_comment = True
        self.save()

    # this method tells where users posting their comments should be sent to
    def get_absolute_url(self):
        return reverse("post_list")

    def __str__(self):
        return self.text

# no User class because User mgt is quite simple here
# otherwise we could have done sth which extends the built-in User class in a OneToOne basis (like in the learn user lecture project)
