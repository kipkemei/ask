from __future__ import print_function, unicode_literals, absolute_import, division
import logging
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from askcomrade.apps import util
import bleach
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from datetime import timedelta
from django.core.mail import send_mail
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager
from askcomrade import const
from django.db.models.signals import post_save
from askcomrade.apps.messagez.models import Message, MessageBody
from askcomrade.apps.util import html
from askcomrade.const import now
import random
from django.dispatch import receiver


ALLOWED_TAGS = bleach.ALLOWED_TAGS + settings.ALLOWED_TAGS
ALLOWED_STYLES = bleach.ALLOWED_STYLES + settings.ALLOWED_STYLES
ALLOWED_ATTRIBUTES = dict(bleach.ALLOWED_ATTRIBUTES)
ALLOWED_ATTRIBUTES.update(settings.ALLOWED_ATTRIBUTES)

logger = logging.getLogger(__name__)

class Tag(models.Model):
    name = models.TextField(max_length=50, db_index=True)

MESSAGE_PREF_MAP = dict(
    local=const.LOCAL_MESSAGE, default=const.DEFAULT_MESSAGES,
    email=const.EMAIL_MESSAGE, all=const.ALL_MESSAGES,
)
MESSAGE_PREFS = MESSAGE_PREF_MAP.get(settings.DEFAULT_MESSAGE_PREF, const.LOCAL_MESSAGE)





class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, **kwargs):
        user = self.create_user(**kwargs)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class LocalManager(UserManager):
    def get_users(self, sort, limit, q, user):
        sort = const.USER_SORT_MAP.get(sort, None)
        days = const.POST_LIMIT_MAP.get(limit, 0)

        if q:
            query = self.filter(name__icontains=q)
        else:
            query = self

        if days:
            delta = const.now() - timedelta(days=days)
            query = self.filter(profile__last_login__gt=delta)

        if user.is_authenticated() and user.is_moderator:
            query = query.select_related("profile").order_by(sort)
        else:
            query = query.exclude(status=User.BANNED).select_related("profile").order_by(sort)

        return query


class AbstractEmailUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), max_length=255, unique=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        abstract = True
        ordering = ['email']

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def email_user(self, subject, message, from_email=None, **kwargs):
        # send_mail(subject, message, from_email, [self.email], **kwargs)
        send_mail(subject, message, from_email, self.email, **kwargs)


class AbstractNamedUser(AbstractEmailUser):
    name = models.CharField(_('name'), max_length=255)

    REQUIRED_FIELDS = ['name']

    class Meta:
        abstract = True
        ordering = ['name', 'email']

    def __str__(self):
        return '{name} <{email}>'.format(
            name=self.name,
            email=self.email,
        )

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name


class User(AbstractNamedUser):





    USER, MODERATOR, ADMIN, BLOG = range(4)
    TYPE_CHOICES = [(USER, "User"), (MODERATOR, "Moderator"), (ADMIN, "Admin"), (BLOG, "Blog")]

    NEW_USER, TRUSTED, SUSPENDED, BANNED = range(4)
    STATUS_CHOICES = ((NEW_USER, 'New User'), (TRUSTED, 'Trusted'), (SUSPENDED, 'Suspended'), (BANNED, 'Banned'))

    USERNAME_FIELD = 'email'

    objects = LocalManager()

    email = models.EmailField(verbose_name='Email', db_index=True, max_length=255, unique=True)
    name = models.CharField(verbose_name='Name', max_length=255, default="", blank=False)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    type = models.IntegerField(choices=TYPE_CHOICES, default=USER)
    status = models.IntegerField(choices=STATUS_CHOICES, default=NEW_USER)
    new_messages = models.IntegerField(default=0)
    badges = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    activity = models.IntegerField(default=0)
    flair = models.CharField(verbose_name='Flair', max_length=15, default="")
    site = models.ForeignKey(Site, null=True)

    @property
    def is_moderator(self):
        if self.is_authenticated():
            return self.type == User.MODERATOR or self.type == User.ADMIN
        else:
            return False

    @property
    def is_administrator(self):
        if self.is_authenticated():
            return self.type == User.ADMIN
        else:
            return False

    @property
    def is_trusted(self):
        return self.status == User.TRUSTED

    @property
    def is_suspended(self):
        return self.status == User.SUSPENDED or self.status == User.BANNED

    def get_full_name(self):
        return self.name or self.email

    def get_short_name(self):
        return self.name or self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.email.split("@")[0]

        super(User, self).save(*args, **kwargs)

    @property
    def scaled_score(self):
        return self.score * 10

    def __str__(self):
        return "%s: %s (%s)" % (self.name, self.email, self.id)

    def get_absolute_url(self):
        url = reverse("user-details", kwargs=dict(pk=self.id))
        return url


class EmailList(models.Model):
    email = models.EmailField(verbose_name='Email', db_index=True, max_length=255, unique=True)
    type = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    date = models.DateTimeField(auto_created=True)



class Profile(models.Model):
    LOCAL_MESSAGE, EMAIL_MESSAGE = const.LOCAL_MESSAGE, const.EMAIL_MESSAGE
    NO_DIGEST, DAILY_DIGEST, WEEKLY_DIGEST, MONTHLY_DIGEST = range(4)
    TYPE_CHOICES = const.MESSAGING_TYPE_CHOICES

    DIGEST_CHOICES = [(NO_DIGEST, 'Never'), (DAILY_DIGEST, 'Daily'),
                      (WEEKLY_DIGEST, 'Weekly'), (MONTHLY_DIGEST, 'Monthly')]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uuid = models.CharField(null=False, db_index=True, unique=True, max_length=255)
    last_login = models.DateTimeField()
    date_joined = models.DateTimeField()
    location = models.CharField(default="", max_length=255, blank=True)
    website = models.URLField(default="", max_length=255, blank=True)
    scholar = models.CharField(default="", max_length=255, blank=True)
    twitter_id = models.CharField(default="", max_length=255, blank=True)
    my_tags = models.TextField(default="", max_length=255, blank=True)
    info = models.TextField(default="", null=True, blank=True)
    message_prefs = models.IntegerField(choices=TYPE_CHOICES, default=MESSAGE_PREFS)
    flag = models.IntegerField(default=0)
    watched_tags = models.CharField(max_length=100, default="", blank=True)
    tags = models.ManyToManyField(Tag, blank=True, )
    digest_prefs = models.IntegerField(choices=DIGEST_CHOICES, default=WEEKLY_DIGEST)
    opt_in = models.BooleanField(default=False)

    def parse_tags(self):
        return util.split_tags(self.tag_val)

    def clear_data(self):
        self.website = self.twitter_id = self.info = self.location = ''
        self.save()

    def add_tags(self, text):
        text = text.strip()
        self.tag_val = bleach.clean(text, tags=[], attributes=[], styles={}, strip=True)
        self.tags.clear()
        tags = [Tag.objects.get_or_create(name=name)[0] for name in self.parse_tags()]
        self.tags.add(*tags)

    def save(self, *args, **kwargs):
        self.info = bleach.clean(self.info, tags=ALLOWED_TAGS,
                                 attributes=ALLOWED_ATTRIBUTES, styles=ALLOWED_STYLES)
        self.location = self.location.strip()
        if not self.id:
            try:
                self.uuid = util.make_uuid()
            except:
                x = random.getrandbits(256)
                return x
            self.date_joined = self.date_joined or now()
            self.last_login = self.date_joined

        super(Profile, self).save(*args, **kwargs)

    def __str__(self):
        return "%s" % self.user.name

    @property
    def filled(self):
        has_location = bool(self.location.strip())
        has_info = bool(self.info.strip())
        return has_location and has_info

    @staticmethod
    def auto_create(sender, instance, created, *args, **kwargs):
        pass
        # "Should run on every user creation."
        # if created:
        #     prof = Profile(user=instance)
        #     prof.save()

from django.db.models.signals import post_save

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=settings.AUTH_USER_MODEL)
post_save.connect(save_user_profile, sender=settings.AUTH_USER_MODEL)


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'name')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ['email', 'password', 'name', 'type', 'is_active', 'is_admin', 'is_staff']

    def clean_password(self):
        return self.initial["password"]


class ProfileInline(admin.StackedInline):
    model = Profile
    fields = ["location", "website", "scholar", "twitter_id", "message_prefs", "my_tags", "watched_tags", "info"]


class AskcomradeUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('name', 'id', 'email', 'type', 'is_admin', 'is_staff')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'status', 'type')}),
        ('Permissions', {'fields': ('is_admin', 'is_staff')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'type', 'password1', 'password2')}
        ),
    )
    search_fields = ('email', 'name',)
    ordering = ('id', 'name', 'email',)
    filter_horizontal = ()
    inlines = [ProfileInline]

admin.site.register(User, AskcomradeUserAdmin)


# post_save.connect(Profile.auto_create, sender=User)

NEW_USER_WELCOME_TEMPLATE = "messages/new_user_welcome.html"


def user_create_messages(sender, instance, created, *args, **kwargs):

    user = instance
    if created:
        authors = User.objects.filter(is_admin=True) or [user]
        author = authors[0]
        title = "Welcome!"
        content = html.render(name=NEW_USER_WELCOME_TEMPLATE, user=user)
        body = MessageBody.objects.create(author=author, subject=title,
                                          text=content, sent_at=now())
        message = Message(user=user, body=body, sent_at=body.sent_at)
        message.save()

post_save.connect(user_create_messages, sender=User, dispatch_uid="user-create_messages")


