from django.views.generic import ListView, DetailView
from django.shortcuts import redirect
from django.http import Http404
from django.db.models import Q
from .models import BlogPost, Tag
from .forms import CommentForm

class BlogListView(ListView):
    """View to display a paginated list of published blog posts."""
    model = BlogPost
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        """Return published posts with optimized queries."""
        return BlogPost.objects.filter(published=True).select_related('author').prefetch_related('tags').order_by('-created_at')

    def get_context_data(self, **kwargs):
        """Add recent posts and tags to context."""
        context = super().get_context_data(**kwargs)
        context['recent_posts'] = BlogPost.objects.filter(published=True).order_by('-created_at')[:5]
        context['popular_tags'] = Tag.objects.all().order_by('name')
        return context

class BlogDetailView(DetailView):
    """View to display an individual blog post with comments."""
    model = BlogPost
    template_name = 'blog/blog_detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        """Ensure only published posts are accessible."""
        obj = super().get_object(queryset)
        if not obj.published:
            raise Http404("Post not found")
        return obj

    def get_context_data(self, **kwargs):
        """Add comments and comment form to context."""
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comment_set.filter(approved=True)
        context['form'] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        """Handle comment submission."""
        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.approved = True
            comment.save()
            return redirect('blog_detail', slug=self.object.slug)
        else:
            context = self.get_context_data()
            context['form'] = form
            return self.render_to_response(context)

class TagListView(ListView):
    """View to display posts filtered by a specific tag."""
    model = BlogPost
    template_name = 'blog/tag_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        """Filter posts by tag slug."""
        tag_slug = self.kwargs['tag_slug']
        return BlogPost.objects.filter(published=True, tags__slug=tag_slug).select_related('author').prefetch_related('tags').order_by('-created_at')

    def get_context_data(self, **kwargs):
        """Add tag information to context."""
        context = super().get_context_data(**kwargs)
        tag_slug = self.kwargs['tag_slug']
        try:
            tag = Tag.objects.get(slug=tag_slug)
            context['tag'] = tag
        except Tag.DoesNotExist:
            context['tag'] = None
        return context

class SearchView(ListView):
    """View to handle search queries and display results."""
    model = BlogPost
    template_name = 'blog/search_results.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        """Filter posts by search query."""
        query = self.request.GET.get('q', '')
        return BlogPost.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query),
            published=True
        ).select_related('author').prefetch_related('tags').order_by('-created_at')

    def get_context_data(self, **kwargs):
        """Add search query to context."""
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context