from django.db import models

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    subtext = models.TextField()
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
