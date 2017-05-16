from __future__ import print_function, unicode_literals, absolute_import, division
import logging, datetime
from django.db import models
from django.conf import settings
from django.contrib import admin
from django.contrib.sites.models import Site

from django.utils.timezone import utc
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
import bleach
from django.db.models import F
from askcomrade import const
from askcomrade.apps.util import html
from askcomrade.apps import util

logger = logging.getLogger(__name__)

def now():
    return datetime.datetime.utcnow().replace(tzinfo=utc)


class Tag(models.Model):
    name = models.TextField(max_length=50, db_index=True)
    count = models.IntegerField(default=0)

    @staticmethod
    def fixcase(name):
        return name.upper() if len(name) == 1 else name.lower()

    @staticmethod
    def update_counts(sender, instance, action, pk_set, *args, **kwargs):
        "Applies tag count updates upon post changes"

        if action == 'post_add':
            Tag.objects.filter(pk__in=pk_set).update(count=F('count') + 1)

        if action == 'post_remove':
            Tag.objects.filter(pk__in=pk_set).update(count=F('count') - 1)

        if action == 'pre_clear':
            instance.tag_set.all().update(count=F('count') - 1)

    def __unicode__(self):
        return self.name

class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'count')
    search_fields = ['name']


admin.site.register(Tag, TagAdmin)

class PostManager(models.Manager):

    def my_bookmarks(self, user):
        query = self.filter(votes__author=user, votes__type=Vote.BOOKMARK)
        query = query.select_related("root", "author", "lastedit_user")
        query = query.prefetch_related("tag_set")
        return query

    def my_posts(self, target, user):
        if user.is_moderator or user == target:
            query = self.filter(author=target)
        else:
            query = self.filter(author=target).exclude(status=Post.DELETED)

        query = query.select_related("root", "author", "lastedit_user")
        query = query.prefetch_related("tag_set")
        query = query.order_by("-creation_date")
        return query

    def fixcase(self, text):
        return text.upper() if len(text) == 1 else text.lower()

    def tag_search(self, text):
        include, exclude = [], []
        terms = text.split(',') if ',' in text else text.split('+')
        for term in terms:
            term = term.strip()
            if term.endswith("!"):
                exclude.append(self.fixcase(term[:-1]))
            else:
                include.append(self.fixcase(term))

        if include:
            query = self.filter(type__in=Post.TOP_LEVEL, tag_set__name__in=include).exclude(
                tag_set__name__in=exclude)
        else:
            query = self.filter(type__in=Post.TOP_LEVEL).exclude(tag_set__name__in=exclude)

        query = query.filter(status=Post.OPEN)

        query = query.defer('content', 'html')

        query = query.select_related("root", "author", "lastedit_user").prefetch_related("tag_set").distinct()

        return query

    def get_thread(self, root, user):
        is_moderator = user.is_authenticated() and user.is_moderator
        if is_moderator:
            query = self.filter(root=root).select_related("root", "author", "lastedit_user").order_by("type", "-has_accepted", "-vote_count", "creation_date")
        else:
            query = self.filter(root=root).exclude(status=Post.DELETED).select_related("root", "author", "lastedit_user").order_by("type", "-has_accepted", "-vote_count", "creation_date")
        return query

    def top_level(self, user):
        is_moderator = user.is_authenticated() and user.is_moderator
        if is_moderator:
            query = self.filter(type__in=Post.TOP_LEVEL)
        else:
            query = self.filter(type__in=Post.TOP_LEVEL).exclude(status=Post.DELETED)

        return query.select_related("root", "author", "lastedit_user").prefetch_related("tag_set").defer("content", "html")


class Post(models.Model):
    objects = PostManager()
    PENDING, OPEN, CLOSED, DELETED = range(4)
    STATUS_CHOICES = [(PENDING, "Pending"), (OPEN, "Open"), (CLOSED, "Closed"), (DELETED, "Deleted")]
    QUESTION, ANSWER, JOB, FORUM, PAGE, BLOG, COMMENT, DATA, TUTORIAL, BOARD, TOOL, NEWS = range(12)
    TYPE_CHOICES = [
        (QUESTION, "Question"), (ANSWER, "Answer"), (COMMENT, "Comment"),
        (JOB, "Job"), (FORUM, "Forum"), (TUTORIAL, "Tutorial"),
        (DATA, "Data"), (PAGE, "Page"), (TOOL, "Tool"), (NEWS, "News"),
        (BLOG, "Blog"), (BOARD, "Bulletin Board")
    ]

    TOP_LEVEL = {QUESTION, JOB, FORUM, PAGE, BLOG, DATA, TUTORIAL, TOOL, NEWS, BOARD}

    title = models.CharField(max_length=200, null=False)

    author = models.ForeignKey(settings.AUTH_USER_MODEL)

    lastedit_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='editor')

    rank = models.FloatField(default=0, blank=True)

    status = models.IntegerField(choices=STATUS_CHOICES, default=OPEN)

    type = models.IntegerField(choices=TYPE_CHOICES, db_index=True)

    vote_count = models.IntegerField(default=0, blank=True, db_index=True)

    view_count = models.IntegerField(default=0, blank=True)

    reply_count = models.IntegerField(default=0, blank=True)

    comment_count = models.IntegerField(default=0, blank=True)

    book_count = models.IntegerField(default=0)

    changed = models.BooleanField(default=True)

    subs_count = models.IntegerField(default=0)

    thread_score = models.IntegerField(default=0, blank=True, db_index=True)

    creation_date = models.DateTimeField(db_index=True)
    lastedit_date = models.DateTimeField(db_index=True)

    sticky = models.BooleanField(default=False, db_index=True)

    has_accepted = models.BooleanField(default=False, blank=True)

    root = models.ForeignKey('self', related_name="descendants", null=True, blank=True)

    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')

    content = models.TextField(default='')

    html = models.TextField(default='')

    tag_val = models.CharField(max_length=100, default="", blank=True)

    tag_set = models.ManyToManyField(Tag, blank=True, )

    site = models.ForeignKey(Site, null=True)

    def parse_tags(self):
        return util.split_tags(self.tag_val)

    def add_tags(self, text):
        text = text.strip()
        if not text:
            return
        self.tag_val = bleach.clean(text, tags=[], attributes=[], styles={}, strip=True)
        self.tag_set.clear()
        tags = [Tag.objects.get_or_create(name=name)[0] for name in self.parse_tags()]
        self.tag_set.add(*tags)
        #self.save()

    @property
    def as_text(self):
        text = bleach.clean(self.content, tags=[], attributes=[], styles={}, strip=True)
        return text

    def peek(self, length=300):
        return self.as_text[:length]

    def get_title(self):
        if self.status == Post.OPEN:
            return self.title
        else:
            return "(%s) %s" % ( self.get_status_display(), self.title)

    @property
    def is_open(self):
        return self.status == Post.OPEN

    @property
    def age_in_days(self):
        delta = const.now() - self.creation_date
        return delta.days

    def update_reply_count(self):
        "This can be used to set the answer count."
        if self.type == Post.ANSWER:
            reply_count = Post.objects.filter(parent=self.parent, type=Post.ANSWER, status=Post.OPEN).count()
            Post.objects.filter(pk=self.parent_id).update(reply_count=reply_count)

    def delete(self, using=None, keep_parents=False):
        tag_names = [t.name for t in self.tag_set.all()]

        Tag.objects.filter(name__in=tag_names).update(count=F('count') - 1)

        Tag.objects.filter(count=0).delete()
        super(Post, self).delete(using=using)

    def save(self, *args, **kwargs):
        self.html = html.parse_html(self.content)
        self.tag_val = html.strip_tags(self.tag_val)

        if self.is_toplevel and self.type != Post.QUESTION:
            required_tag = self.get_type_display()
            if required_tag not in self.tag_val:
                self.tag_val += "," + required_tag

        if not self.id:

            if self.parent and not self.title:
                self.title = self.parent.title

            if self.parent and self.parent.type in (Post.ANSWER, Post.COMMENT):
                self.type = Post.COMMENT

            if self.type is None:
                self.type = self.COMMENT if self.parent else self.FORUM

            self.title = self.parent.title if self.parent else self.title
            self.lastedit_user = self.author
            self.status = self.status or Post.PENDING
            self.creation_date = self.creation_date or now()
            self.lastedit_date = self.creation_date

            if self.type == Post.ANSWER:
                self.parent.lastedit_date = self.lastedit_date
                self.parent.lastedit_user = self.lastedit_user
                self.parent.save()

        self.update_reply_count()

        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return "%s: %s (id=%s)" % (self.get_type_display(), self.title, self.id)

    @property
    def is_toplevel(self):
        return self.type in Post.TOP_LEVEL

    def get_absolute_url(self):
        url = reverse("post-details", kwargs=dict(pk=self.root_id))
        return url if self.is_toplevel else "%s#%s" % (url, self.id)

    @staticmethod
    def update_post_views(post, request, minutes=settings.POST_VIEW_MINUTES):
        ip1 = request.META.get('REMOTE_ADDR', '')
        ip2 = request.META.get('HTTP_X_FORWARDED_FOR', '').split(",")[0].strip()

        ip1 = '' if ip1.lower() == 'localhost' else ip1
        ip2 = '' if ip2.lower() == 'localhost' else ip2
        ip = ip1 or ip2 or '0.0.0.0'

        now = const.now()
        since = now - datetime.timedelta(minutes=minutes)

        if not PostView.objects.filter(ip=ip, post=post, date__gt=since):
            PostView.objects.create(ip=ip, post=post, date=now)
            Post.objects.filter(id=post.id).update(view_count=F('view_count') + 1)
        return post

    @staticmethod
    def check_root(sender, instance, created, *args, **kwargs):
        if created:
            if not (instance.root or instance.parent):
                instance.root = instance.parent = instance

            elif instance.parent:
                instance.root = instance.parent.root

            elif instance.root:
                raise Exception('Root may not be set on creation')

            if instance.parent.type in (Post.ANSWER, Post.COMMENT):
                instance.type = Post.COMMENT

            assert instance.root and instance.parent

            if not instance.is_toplevel:
                instance.title = "%s: %s" % (instance.get_type_display()[0], instance.root.title[:80])
                if instance.type == Post.ANSWER:
                    Post.objects.filter(id=instance.root.id).update(reply_count=F("reply_count") + 1)

            instance.save()


class ReplyToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    post = models.ForeignKey(Post)
    token = models.CharField(max_length=256)
    date = models.DateTimeField(auto_created=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.token = util.make_uuid()
        super(ReplyToken, self).save(*args, **kwargs)


class ReplyTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'token', 'date')
    ordering = ['-date']
    search_fields = ('post__title', 'user__name')

admin.site.register(ReplyToken, ReplyTokenAdmin)


class EmailSub(models.Model):
    SUBSCRIBED, UNSUBSCRIBED = 0, 1
    TYPE_CHOICES = [
        (SUBSCRIBED, "Subscribed"), (UNSUBSCRIBED, "Unsubscribed"),

    ]
    email = models.EmailField()
    status = models.IntegerField(choices=TYPE_CHOICES)

admin.site.register(EmailSub)


class EmailEntry(models.Model):
    DRAFT, PENDING, PUBLISHED = 0, 1, 2
    post = models.ForeignKey(Post, null=True)
    text = models.TextField(default='')
    creation_date = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField(choices=((DRAFT, "Draft"), (PUBLISHED, "Published")))

admin.site.register(EmailEntry)



class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'author')
    # fieldsets = (
    #     (None, {'fields': ('title',)}),
    #     ('Attributes', {'fields': ('type', 'status', 'sticky',)}),
    #     ('Content', {'fields': ('content', )}),
    # )
    search_fields = ('title', 'author__name')

admin.site.register(Post, PostAdmin)


class PostView(models.Model):
    ip = models.GenericIPAddressField(default='', null=True, blank=True)
    post = models.ForeignKey(Post, related_name="post_views")
    date = models.DateTimeField(auto_now=True)

admin.site.register(PostView)


class Vote(models.Model):
    UP, DOWN, BOOKMARK, ACCEPT = range(4)
    TYPE_CHOICES = [(UP, "Upvote"), (DOWN, "DownVote"), (BOOKMARK, "Bookmark"), (ACCEPT, "Accept")]
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    post = models.ForeignKey(Post, related_name='votes')
    type = models.IntegerField(choices=TYPE_CHOICES, db_index=True)
    date = models.DateTimeField(db_index=True, auto_now=True)

    def __str__(self):
        return u"Vote: %s, %s, %s" % (self.post_id, self.author_id, self.get_type_display())


class VoteAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'type', 'date')
    ordering = ['-date']
    search_fields = ('post__title', 'author__name')


admin.site.register(Vote, VoteAdmin)


class SubscriptionManager(models.Manager):
    def get_subs(self, post):
        return self.filter(post=post.root).select_related("user")

from askcomrade.const import LOCAL_MESSAGE, MESSAGING_TYPE_CHOICES


class Subscription(models.Model):
    class Meta:
        unique_together = (("user", "post"),)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), db_index=True)
    post = models.ForeignKey(Post, verbose_name=_("Post"), related_name="subs", db_index=True)
    type = models.IntegerField(choices=MESSAGING_TYPE_CHOICES, default=LOCAL_MESSAGE, db_index=True)
    date = models.DateTimeField(_("Date"), db_index=True)

    objects = SubscriptionManager()

    def __str__(self):
        return "%s to %s" % (self.user.name, self.post.title)

    def save(self, *args, **kwargs):

        if not self.id:
            self.date = self.date or const.now()

        super(Subscription, self).save(*args, **kwargs)

    @staticmethod
    def get_sub(post, user):

        if user.is_authenticated():
            try:
                return Subscription.objects.get(post=post, user=user)
            except:
                return None

        return None

    @staticmethod
    def create(sender, instance, created, *args, **kwargs):
        user = instance.author
        root = instance.root
        if Subscription.objects.filter(post=root, user=user).count() == 0:
            sub_type = user.profile.message_prefs
            if sub_type == const.DEFAULT_MESSAGES:
                sub_type = const.EMAIL_MESSAGE if instance.is_toplevel else const.LOCAL_MESSAGE
            sub = Subscription(post=root, user=user, type=sub_type)
            sub.date = datetime.datetime.utcnow().replace(tzinfo=utc)
            sub.save()
            Post.objects.filter(pk=root.id).update(subs_count=F('subs_count') + 1)

    @staticmethod
    def finalize_delete(sender, instance, *args, **kwargs):
        Post.objects.filter(pk=instance.post.root_id).update(subs_count=F('subs_count') - 1)


class SubscriptionAdmin(admin.ModelAdmin):
    search_fields = ('user__name', 'user__email')
    list_select_related = ["user", "post"]


admin.site.register(Subscription, SubscriptionAdmin)

from django.db.models.signals import post_save, post_delete, m2m_changed

post_save.connect(Post.check_root, sender=Post)
post_save.connect(Subscription.create, sender=Post, dispatch_uid="create_subs")
post_delete.connect(Subscription.finalize_delete, sender=Subscription, dispatch_uid="delete_subs")
m2m_changed.connect(Tag.update_counts, sender=Post.tag_set.through)

