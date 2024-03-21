from django.db import models

# Create your models here.
class Author(models.Model):
	username = models.CharField(max_length=100)
	password = models.CharField(max_length=100)
	firstName = models.CharField(max_length=100)
	lastName = models.CharField(max_length=100)

	def __str__(self):
		return self.username

class Category(models.Model):
	name = models.CharField(max_length=100)
	short = models.CharField(max_length=10, default='default_value')

	def __str__(self):
		return self.name

class Region(models.Model):
	name = models.CharField(max_length=100)
	short = models.CharField(max_length=10, default='default_value')

	def __str__(self):
		return self.name

class News(models.Model):
	title = models.CharField(max_length=64)
	category = models.ForeignKey(Category, on_delete=models.CASCADE)
	region = models.ForeignKey(Region, on_delete=models.CASCADE)
	author = models.ForeignKey(Author, on_delete=models.CASCADE)
	date = models.DateField()
	details = models.TextField(max_length=128)

	def __str__(self):
		return self.title
