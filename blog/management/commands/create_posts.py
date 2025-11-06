from django.core.management.base import BaseCommand

from django.contrib.auth import get_user_model

from blog.models import Post, Tag, Comment



class Command(BaseCommand):
    help = "Create_posts"

    def add_arguments(self, parser):
        parser.add_argument(
            "--total_posts", type=int, default=1500,
            help="Number of posts to create (default 1500)"
        )
        parser.add_argument(
            "--total_tags", type=int, default=500,
            help="Number of tags to create (default 500)"
        )
        parser.add_argument(
            "--total_comments", type=int, default=500,
            help="Total number of comments to create across all posts (default 500)"
        )

    def handle(self, *args, **options):
        total_posts = options["total_posts"]
        total_tags = options["total_tags"]
        total_comments = options["total_comments"]

        User = get_user_model()
        author = User.objects.first()
        if not author:
            self.stdout.write(self.style.ERROR("No user found! Please create a user first."))
            return

        # Create or get all tags
        tags = []
        for i in range(1, total_tags + 1):
            tag, _ = Tag.objects.get_or_create(name=f"Django{i}")
            tags.append(tag)

        # Create posts
        posts_to_create = [
            Post(
                author=author,
                title=f"Generat Post {i+1}",
                content=f"This is content for auto post {i+1} with {total_tags} tags."
            )
            for i in range(total_posts)
        ]
        posts = Post.objects.bulk_create(posts_to_create)
        for post in posts:
            post.tags.set(tags)

        comments_to_create = []
        comments_per_post = max(1, total_comments // total_posts)
        extra_comments = total_comments % total_posts

        for idx, post in enumerate(posts):
            for j in range(1, comments_per_post + 1):
                comments_to_create.append(
                    Comment(post=post, author=author, content=f"Auto comment {j} for post {post.id}")
                )
            if idx < extra_comments:
                comments_to_create.append(
                    Comment(post=post, author=author, content=f"Extra auto comment for post {post.id}")
                )

        Comment.objects.bulk_create(comments_to_create)

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {total_posts} posts with {total_tags} tags each and {total_comments} comments total."
            )
        )
