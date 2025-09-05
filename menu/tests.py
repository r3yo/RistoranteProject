from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal
from .models import Dish, Category, Ingredient
from django.contrib.auth.models import User, Group

class MenuViewTests(TestCase):
    def setUp(self):
        # Create a manager user
        self.manager = User.objects.create_user(username="manager", password="pass")
        group, _ = Group.objects.get_or_create(name="Managers")
        self.manager.groups.add(group)
        self.manager.save()

        # Create a category with explicit slug
        self.category = Category.objects.create(
            name="Starters"
        )

        # Create an ingredient with explicit slug
        self.ingredient = Ingredient.objects.create(
            name="Tomato"
        )

        # Create a dish with explicit slug
        img_file = SimpleUploadedFile(
            "dish.jpg", 
            b"file_content", 
            content_type="image/jpeg"
        )
        
        self.dish = Dish.objects.create(
            name="Bruschetta",
            category=self.category,
            price=Decimal("5.00"),
            available=True,
            img=img_file,
            description="Test description"  # Added required description
        )
        
        # Set ManyToMany ingredients
        self.dish.ingredients.add(self.ingredient)

        self.client = Client()

    def test_create_dish_requires_manager(self):
        url = reverse("menu:add-dish")
        # Not logged in
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # redirected to login

    def test_update_dish(self):
        url = reverse("menu:update-dish", kwargs={"pk": self.dish.slug})
        self.client.login(username="manager", password="pass")

        response = self.client.post(url, {
            "name": "Updated Bruschetta",
            "category": self.category.pk,  # Use primary key (which is the slug)
            "price": "6.00",
            "ingredients": [self.ingredient.pk],  # Use primary key (which is the slug)
            "description": "Updated description",
            "available": True
            # Note: img not changed
        }, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.dish.refresh_from_db()
        self.assertEqual(self.dish.name, "Updated Bruschetta")
        self.assertEqual(self.dish.price, Decimal("6.00"))

    def test_delete_dish(self):
        url = reverse("menu:delete-dish", kwargs={"pk": self.dish.slug})
        self.client.login(username="manager", password="pass")
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Dish.objects.filter(pk=self.dish.pk).exists())

    def test_dish_detail_view(self):
        url = reverse("menu:dish-detail", kwargs={"pk": self.dish.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bruschetta")

    def test_menu_list_view(self):
        url = reverse("menu:menu-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.category.name)