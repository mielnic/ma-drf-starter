# Django/DRF starter project

This is my Django/DRF backend boilerplate for new projects.

It includes:

- Django 5.1 with Django Rest Framework
- Custom user model with e-mail only user.
- Django environ for envirmonment variables.
- Django CORS headers.
- Django Unfold for admin module.
- Psycopg for PostgreSQL
- Tivix Django-cron fixed for django 5.1, with database lock enabled.
- Custom log app, with file logging and database logging accesible from the admin interfase.
- Simple JWT, customized for HTTP ONLY tokens.

**User App**
- Self sign in API with:
    - Open registration (anyone can sign-up).
    - Domain restricted registration (only @domain emails can sign-up).
    - Parked registration (user can sign up, but remains inactive until enabled by an administrator).
- Sign-up verification issued by email.
- Verification API.
- Password Recovery:
    - PW reset request API.
    - Recover link sent by email.
    - New password API.