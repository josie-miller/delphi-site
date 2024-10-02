from django.db import models
from django.contrib.auth.models import User 


class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    subtext = models.TextField()
    content = models.TextField()
    image = models.ImageField(upload_to='blog_images', null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    read_time = models.PositiveIntegerField(default=5) 
    views = models.PositiveIntegerField(default=0)  
    likes = models.PositiveIntegerField(default=0) 

    def __str__(self):
        return self.title

class PredictionResponse(models.Model):
    question_number = models.IntegerField()  
    user = models.CharField(max_length=255)  
    answer = models.CharField(max_length=255)  # answer

    def __str__(self):
        return f"Question {self.question_number} - User: {self.user} - Answer: {self.answer}"

class Comment(models.Model):
    post = models.ForeignKey(BlogPost, related_name="comments", on_delete=models.CASCADE)
    author = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author} on {self.post.title}'