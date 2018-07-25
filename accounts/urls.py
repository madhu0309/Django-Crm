from django.conf.urls import url
from django.urls import path
from accounts import views
from accounts.views import AccountsListView, CreateAccountView

app_name = 'accounts'

urlpatterns = [
	path('list/', AccountsListView.as_view(), name='list'),
	path('create/', CreateAccountView.as_view(), name='new_account'),

    url(r'^(?P<account_id>\d*)/view/$', views.view_account, name="view_account"),
    url(r'^(?P<edid>\d*)/edit/$', views.edit_account, name="edit_account"),
    url(r'^(?P<aid>\d*)/delete/$', views.remove_account, name="remove_account"),

    url(r'^comment/add/$', views.add_comment, name='add_comment'),
    url(r'^comment/edit/$', views.edit_comment, name='edit_comment'),
    url(r'^comment/remove/$', views.remove_comment, name='remove_comment'),
]
