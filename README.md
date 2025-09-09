# Restaurant

A Django web application for managing restaurant operations, featuring real-time notifications, user-friendly forms, and image support.

## Features
- Django framework  
- Real-time support with Channels  
- Beautiful forms with Crispy Forms & Bootstrap 4  
- Handy mixins with Django Braces  
- Image support with Pillow

## Setup

### 1. Install Python 3.x
Check if Python is installed:
```bash
python --version
# or
python3 --version
```
If you don’t have `pip`, download it from (https://pip.pypa.io/en/stable/installing/)

### 2. Install Pipenv
```bash
pip install pipenv
```

### 3. Import or clone the project
```bash
git clone https://github.com/r3yo/ristoranteproject.git
cd ristoranteproject
```

### 4. Create virtual environment and install Django
```bash
pipenv install django
pipenv shell
```

### 5. Install other dependencies
Inside the pipenv shell, run:
```bash
pipenv install daphne channels django-crispy-forms crispy-bootstrap4 django-braces pillow
```

### 6. Apply migrations
```bash
python manage.py migrate
```

### 7. Create a superuser (optional)
```bash
python manage.py createsuperuser
```

## Running the Project

- **Django development server**
```bash
python manage.py runserver
```

## Notes
- Pillow is required for `ImageField`.  
- Channels enables real-time features.  
- Django Braces provides useful class-based view mixins.
