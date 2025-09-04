import re
from django.db import models
from django.utils.text import slugify

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(primary_key = True, unique = True, blank = True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def save(self, *args, **kwargs):
        self.name = re.sub(r"/s+", " ", self.name).strip().title()
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
class Ingredient(models.Model):
    name = models.CharField(max_length = 100, unique = True)
    slug = models.SlugField(primary_key = True, unique = True, blank = True)

    def save(self, *args, **kwargs):
        # Normalize casing and collapse spacing
        self.name = re.sub(r"/s+", " ", self.name).strip().title()
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Dish(models.Model):
    category = models.ForeignKey(Category, related_name="dishes", on_delete=models.CASCADE)
    slug = models.SlugField(primary_key = True, unique = True, blank = True)
    name = models.CharField(max_length=150, unique=True)
    ingredients = models.ManyToManyField(Ingredient, related_name = "dishes")
    description = models.CharField(default="No description.")
    price = models.DecimalField(max_digits=6, decimal_places=2)
    available = models.BooleanField(default=True)
    img = models.ImageField(upload_to = 'dishes/')
    
    class Meta:
        verbose_name_plural = "Dishes"
    
    def __str__(self):
        return f"Name: {self.name} Category: {self.category}"
    
    def save(self, *args, **kwargs):
        self.name = re.sub(r"/s+", " ", self.name).strip().title()
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)