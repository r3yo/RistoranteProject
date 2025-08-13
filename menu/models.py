from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=False)
    class Meta:
        verbose_name_plural = "Categories"


class Dish(models.Model):
    category = models.ForeignKey(Category, related_name="dishes", on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    ingredients = models.CharField(blank=False)
    description = models.CharField(default="No description.")
    price = models.DecimalField(max_digits=6, decimal_places=2)
    available = models.BooleanField(default=True)
    class Meta:
        verbose_name_plural = "Dishes"
    def __str__(self):
        return f"Name: {self.name} Categoria: {self.category}"
