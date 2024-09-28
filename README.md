This is a fully functional e-commerce platform built using Python and Django. The project allows users to browse products, add items to their cart, and complete purchases. Admin users can manage products, categories, and orders through a user-friendly dashboard.

--->Features
User authentication (registration, login, password reset)
Product catalog with search and filtering options
Shopping cart functionality
Secure checkout process with payment integration
Order management for users and admin
Admin dashboard for managing products, categories, and orders


--->Technologies Used
Python 3.12.2
Django 5.0.4
PostgreSQL / SQLite (depending on setup)
HTML, CSS, and JavaScript
Bootstrap for responsive design

-->Installation
download python from official website.
pip install django.
1.Clone the repository
2.Install the requirements
3.Set up the database:python manage.py migrate
4.Create a superuser (for admin access):python manage.py createsuperuser
5.Run the development server:python manage.py runserver

--->Usage
Navigate through the product catalog to browse items.
Add products to your cart and proceed to checkout.
Admin can log in at /admin to manage products and orders.
