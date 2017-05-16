from django.conf.urls import include, url
from django.contrib import admin
admin.autodiscover()
from django.views.generic import TemplateView
from askcomrade.server import views, ajax, search, moderate, api, orcid
from askcomrade.apps.posts.views import NewAnswer, NewPost, EditPost, external_post_handler
from askcomrade.apps.users.views import external_logout, external_login, CaptchaView, DigestManager, unsubscribe
from askcomrade.apps.planet.views import BlogPostList

urlpatterns = [
    url(r'^$', views.PostList.as_view(), name="home"),
    url(r'^t/$', views.TagList.as_view(), name="tag-list"),
    url(r'^b/(?P<pk>\d+)/$', views.BadgeView.as_view(), name="badge-view"),
    url(r'^b/list/$', views.BadgeList.as_view(), name="badge-list"),
    url(r'^t/(?P<topic>.+)/$', views.PostList.as_view(), name="topic-list"),
    url(r'^user/list/$', views.UserList.as_view(), name="user-list"),
    url(r'^u/(?P<pk>\d+)/$', views.UserDetails.as_view(), name="user-details"),
    url(r'^u/edit/(?P<pk>\d+)/$', views.EditUser.as_view(), name="user-edit"),
    url(r'^p/(?P<pk>\d+)/$', views.PostDetails.as_view(), name="post-details"),
    url(r'^local/sub/(?P<pk>\d+)/(?P<type>\w+)/$', views.ChangeSub.as_view(), name="change-sub"),
    url(r'^p/new/post/$', views.RateLimitedNewPost.as_view(), name="new-post"),
    url(r'^p/new/external/post/$', external_post_handler, name="new-external-post"),
    url(r'^p/new/answer/(?P<pid>\d+)/$', views.RateLimitedNewAnswer.as_view(post_type="answer"), name="new-answer"),
    url(r'^p/new/comment/(?P<pid>\d+)/$', views.RateLimitedNewAnswer.as_view(post_type="comment"), name="new-comment"),
    url(r'^p/edit/(?P<pk>\d+)/$', EditPost.as_view(), name="post-edit"),
    url(r'^local/messages/$', views.MessageList.as_view(), name="user-messages"),
    url(r'^local/votes/$', views.VoteList.as_view(), name="user-votes"),
    url(r'^local/moderate/post/(?P<pk>\d+)/$', moderate.PostModeration.as_view(), name="post-moderation"),
    url(r'^local/moderate/user/(?P<pk>\d+)/$', moderate.UserModeration.as_view(), name="user-moderation"),
    url(r'^site/login/$', external_login, name="login"),
    url(r'^site/logout/$', external_logout, name="logout"),
    url(r'^accounts/signup/$', CaptchaView.as_view(), name="signup"),
    url(r'^local/email/', views.email_handler, name="email-handler"),
    url(r'^local/search/page/', search.Search.as_view(), name="search-page"),
    url(r'^local/search/title/', search.search_title, name="search-title"),
    url(r'^digest/manage/', DigestManager.as_view() , name="digest_manage"),
    url(r'^digest/unsubscribe/(?P<uuid>\w+)/', unsubscribe , name="digest_unsubscribe"),
    url(r'^local/search/tags/', search.suggest_tags, name="suggest-tags"),
    url(r'^planet/$', BlogPostList.as_view(), name="planet"),
    url(r'^x/vote/$', ajax.vote_handler, name="vote-submit"),
    # url(r'^accounts/social/orcid/import/$', orcid.import_bio, name="orcid-import"),
    url(r'^accounts/', include('allauth.urls')),

    # Redirecting old posts urls from previous versions of Askcomrade
    url(r'^post/redirect/(?P<pid>\d+)/$', views.post_redirect),
    url(r'^post/show/(?P<pid>\d+)/$', views.post_redirect),
    url(r'^post/show/(?P<pid>\d+)/([-\w]+)/$', views.post_redirect),
    url(r'^questions/(?P<pid>\d+)/$', views.post_remap_redirect),
    url(r'^questions/(?P<pid>\d+)/([-\w]+)/$', views.post_remap_redirect),
    url(r'^questions/tagged/(?P<tag>.+)/$',views.tag_redirect),

    # Api.
    url(r'^api/traffic/$', api.traffic, name='api-traffic'),
    url(r'^api/user/(?P<id>\d+)/$', api.user_details, name='api-user'),
    url(r'^api/post/(?P<id>\d+)/$', api.post_details, name='api-post'),
    url(r'^api/vote/(?P<id>\d+)/$', api.vote_details, name='api-vote'),
    url(r'^api/stats/day/(?P<day>\d+)/$', api.daily_stats_on_day, name='api-stats-on-day'),
    url(r'^api/stats/date/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$',
        api.daily_stats_on_date, name='api-stats-on-date'),

    url(r'^admin/', include(admin.site.urls)),

     # Local robots.txt.
    url(r'^robots\.txt$', TemplateView.as_view(template_name="robots.txt", content_type='text/plain'), name='robots'),

]


from askcomrade.server.feeds import LatestFeed, TagFeed, UserFeed, PostFeed, PostTypeFeed, PlanetFeed

# Adding the RSS related urls.
urlpatterns += [
    url(r'^info/rss/$', views.RSS.as_view(), name='rss'),

    url(r'^feeds/latest/$', LatestFeed(), name='latest-feed'),

    url(r'^feeds/tag/(?P<text>[\w\-_\+!]+)/$', TagFeed(), name='tag-feed'),
    url(r'^feeds/user/(?P<text>[\w\-_\+!]+)/$', UserFeed(), name='user-feed'),
    url(r'^feeds/post/(?P<text>[\w\-_\+!]+)/$', PostFeed(), name='post-feed' ),
    url(r'^feeds/type/(?P<text>[\w\-_\+!]+)/$', PostTypeFeed(), name='post-type'),
    url(r'^feeds/planet/$', PlanetFeed(), name='planet-feed'),
]

urlpatterns += [
    url(r'^info/(?P<slug>\w+)/$', views.FlatPageView.as_view(), name='flatpage'),
    url(r'^info/update/(?P<pk>\d+)/$', views.FlatPageUpdate.as_view(), name='flatpage-update'),
]

# Adding the sitemap.
# urlpatterns += [
#     url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': search.sitemaps})
# ]
