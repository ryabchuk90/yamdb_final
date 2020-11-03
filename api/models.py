from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime


class ConfirmationCode(models.Model):
    email = models.EmailField(max_length=30, unique=True)
    confirmation_code = models.CharField(max_length=30)
    last_sent = models.DateTimeField(auto_now=True)
    confirmed = models.BooleanField(default=False)


class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор')
    ]
    bio = models.TextField(max_length=500, blank=True)
    role = models.TextField(
        max_length=20, choices=ROLE_CHOICES, default='user')
    email = models.EmailField(
        max_length=35, blank=False, null=False, unique=True)


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=200)
    year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(datetime.datetime.now().year)],
        help_text="Use the following format: <YYYY>")
    rating = models.PositiveIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10)], null=True)
    description = models.TextField()
    genre = models.ManyToManyField(Genre, related_name='titles')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="titles")

    def __str__(self):
        return self.name


class Review(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="review")
    score = models.PositiveIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10)], null=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    title = models.ForeignKey(
        Title, on_delete=models.SET_NULL, null=True, related_name='review')

    def __str__(self):
        return self.text


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments")
    pub_date = models.DateTimeField(auto_now_add=True)
    review = models.ForeignKey(
        Review, on_delete=models.SET_NULL, null=True, related_name='comments')

    def __str__(self):
        return self.text
