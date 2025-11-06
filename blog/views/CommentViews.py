from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from django.shortcuts import get_object_or_404

from ..models import Comment, Post

from ..serializers import CommentSerializer

from django.db.models import Prefetch

from django.core.mail import send_mail

from django.conf import settings



class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
    
        queryset = (
            Comment.objects.select_related('author', 'post')
            .distinct()
            .order_by("created_at")
        )
        return queryset


    def perform_create(self, serializer):
        post_id = self.request.data.get("post")
        post = get_object_or_404(Post, pk=post_id)
        comment = serializer.save(author=self.request.user, post=post)

        post_author = post.author
        commenter = self.request.user

        print("Attempting to send emails...")

        try:
            post_url = f"http://127.0.0.1:8000/api/blog/posts/{post.id}/"

            if post_author.email and post_author != commenter:
                subject = f"New Comment on Your Post '{post.title}'"
                message = (
                    f"Hi {post_author.username},\n\n"
                    f"{commenter.username} commented on your post:\n"
                    f"\"{comment.content}\"\n\n"
                    f"View Post: {post_url}\n\n"
                    f"Thank you,\nYour Blog Team"
                )
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [post_author.email],
                    fail_silently=False,
                )
                print("Email sent to post author!")

            if commenter.email:
                subject = "Your comment was posted successfully!"
                message = (
                    f"Hi {commenter.username},\n\n"
                    f"Your comment on the post '{post.title}' has been posted successfully.\n"
                    f"Thank you for your participation!\n\n"
                    f"View Post: {post_url}\n\n"
                    f"Best regards,\nYour Blog Team"
                )
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [commenter.email],
                    fail_silently=False,
                )
                print("Confirmation email sent to commenter!")

        except Exception as e:
            print("Email sending failed:", e)
