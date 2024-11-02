from django.db import models


class Category(models.Model):
    title = models.CharField('title', max_length=255)
    description = models.TextField('description')

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['title']

    def __str__(self):
        return self.title
