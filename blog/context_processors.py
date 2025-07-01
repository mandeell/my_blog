from .models import BlogPost, Tag

def blog_context(request):
    return {
        'recent_posts': BlogPost.objects.filter(published=True).order_by('-created_at')[:5],
        'popular_tags': Tag.objects.all().order_by('name'),
    }