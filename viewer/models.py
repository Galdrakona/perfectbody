from django.db import models

# class Category(models.Model):
#     name = models.CharField(max_length=100)
#
#     def __str__(self):
#         return self.name
#
# class SubCategory(models.Model):
#     name = models.CharField(max_length=100)
#     category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)
#
#     def __str__(self):
#         return self.name
