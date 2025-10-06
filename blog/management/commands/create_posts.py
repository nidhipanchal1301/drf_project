from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blog.models import Post, Tag, Comment

class Command(BaseCommand):
    help = "Create posts with multiple tags and multiple comments"

    def add_arguments(self, parser):
        parser.add_argument(
            "--total_posts", type=int, default=5,
            help="Number of posts to create (default 5)"
        )
        parser.add_argument(
            "--tags", type=int, default=500,
            help="Number of tags to assign per post (default 500)"
        )
        parser.add_argument(
            "--comments", type=int, default=500,
            help="Number of comments to create per post (default 500)"
        )

    def handle(self, *args, **options):
        total_posts = options["total_posts"]
        total_tags = options["tags"]
        total_comments = options["comments"]

        # Create or get tags
        tags = []
        for i in range(1, total_tags + 1):
            tag, _ = Tag.objects.get_or_create(name=f"Django{i}")
            tags.append(tag)

        # Get first user
        author = User.objects.first()
        if not author:
            self.stdout.write(self.style.ERROR("No user found! Please create a user first."))
            return

        # Create posts with tags and comments
        for i in range(total_posts):
            post = Post.objects.create(
                author=author,
                title=f"Auto Generated Post {i+1}",
                content=f"This is content for auto post {i+1} with {len(tags)} tags and {total_comments} comments."
            )
            post.tags.set(tags)  # assign all tags at once

            # Create comments for this post
            for j in range(1, total_comments + 1):
                Comment.objects.create(
                    post=post,
                    author=author,
                    content=f"This is auto-generated comment {j} for post {i+1}"
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Created Post {post.id} with {post.tags.count()} tags and {total_comments} comments."
                )
            )
