from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from .models import Post


def delete_latest_post():
    """Delete the latest (most recently created) post."""
    latest_post = Post.objects.order_by('-created_at').first()
    if latest_post:
        print(f"Deleting latest post: {latest_post.title} (created at {latest_post.created_at})")
        latest_post.delete()
        print(f"Deleted 1 latest post at {timezone.now()}")
    else:
        print(f"No posts available to delete at {timezone.now()}")


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(delete_latest_post, 'interval', minutes=1)
    scheduler.start()
