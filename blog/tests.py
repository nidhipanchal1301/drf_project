from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from .models import Post



class PostAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass123")
        self.client = APIClient()
        self.client.login(username="tester", password="pass123")
        self.post = Post.objects.create(author=self.user, title="Hello", content="World")

    def test_list_posts(self):
        url = reverse("v1:post-list")  
        resp = self.client.get("/api/v1/posts/")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp.data["results"]) >= 1)

    def test_create_post_requires_auth(self):
        self.client.logout()
        resp = self.client.post("/api/v1/posts/", {"title": "New", "content": "X"})
        self.assertEqual(resp.status_code, 401)  # For unauthenticated

    def test_create_post(self):
        self.client.login(username="tester", password="pass123")
        resp = self.client.post("/api/v1/posts/", {"title": "New", "content": "X"})
        self.assertIn(resp.status_code, (201, 200))
