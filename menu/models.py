import os
import re
from django.db import models
from tables.models import generate_unique_slug

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(primary_key = True, unique = True, blank = True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def save(self, *args, **kwargs):
        self.name = re.sub(r"\s+", " ", self.name).strip().title()
        if not self.slug:
            self.slug = generate_unique_slug(Category, "CAT")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
class Ingredient(models.Model):
    name = models.CharField(max_length = 100, unique=True)
    slug = models.SlugField(primary_key = True, unique = True, blank = True)
    
    class Meta:
        ordering = ["name"]  # alphabetical

    def save(self, *args, **kwargs):
        # Normalize casing and collapse spacing
        self.name = re.sub(r"\s+", " ", self.name).strip().title()
        if not self.slug:
            self.slug = generate_unique_slug(Ingredient, "ING")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Dish(models.Model):
    category = models.ForeignKey(Category, related_name="dishes", on_delete=models.CASCADE)
    slug = models.SlugField(primary_key = True, unique = True, blank = True)
    name = models.CharField(max_length=150, unique=True)
    ingredients = models.ManyToManyField(Ingredient, related_name = "dishes")
    description = models.CharField(max_length=500, default="No description.")
    price = models.DecimalField(max_digits=6, decimal_places=2)
    available = models.BooleanField(default=True)
    img = models.ImageField(upload_to = 'dishes/')
    
    class Meta:
        verbose_name_plural = "Dishes"
    
    def __str__(self):
        return f"Name: {self.name} Category: {self.category}"
    
    def save(self, *args, **kwargs):
        self.name = re.sub(r"\s+", " ", self.name).strip().title()
        if not self.slug:
            self.slug = generate_unique_slug(Dish, "DSH")
        try:
            old_instance = Dish.objects.get(pk=self.pk)
            if old_instance.img and old_instance.img != self.img:
                if os.path.isfile(old_instance.img.path):
                    os.remove(old_instance.img.path)
        except Dish.DoesNotExist:
            # Object is new, nothing to delete
            pass
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        if self.img and os.path.isfile(self.img.path):
            os.remove(self.img.path)
        super().delete(*args, **kwargs)