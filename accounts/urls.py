from django.conf.urls import url
from django.urls import path
from accounts import views
from accounts.views import (
	AccountsListView, CreateAccountView, AccountDetailView, AccountUpdateView,
	AccountDeleteView, AddCommentView)

app_name = 'accounts'

urlpatterns = [
	path('list/', AccountsListView.as_view(), name='list'),
	path('create/', CreateAccountView.as_view(), name='new_account'),
	path('<int:pk>/view/', AccountDetailView.as_view(), name="view_account"),
	path('<int:pk>/edit/', AccountUpdateView.as_view(), name="edit_account"),
	path('<int:pk>/delete/', AccountDeleteView.as_view(), name="remove_account"),
	path('comment/add/', AddCommentView.as_view(), name="add_comment"),

    # url(r'^comment/add/$', views.add_comment, name='add_comment'),
    url(r'^comment/edit/$', views.edit_comment, name='edit_comment'),
    url(r'^comment/remove/$', views.remove_comment, name='remove_comment'),
]
