from django.urls import path
from .views import BlogListView, BlogDetailView, TagListView, SearchView

urlpatterns = [
    path('', BlogListView.as_view(), name='blog_list'),
    path('<slug:slug>/', BlogDetailView.as_view(), name='blog_detail'),
    path('tag/<slug:tag_slug>/', TagListView.as_view(), name='tag_list'),
    path('search/', SearchView.as_view(), name='search'),
]