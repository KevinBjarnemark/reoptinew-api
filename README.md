# Reoptinew API

## Table of Contents

- 🎨 [Frontend](#frontend)
- 🛢️ [Databases](#databases)
- 🛠️ [Technologies](#technologies)

## Frontend

The Reoptinew web app uses a decoupled architecture, separating the frontend and backend repositories. The **frontend repository** can be found [**here**](https://github.com/KevinBjarnemark/reoptinew).

## Databases

> ⚠️ **NOTE**  
> If you need to access the production database locally, you can do so altough it is **strongly discouraged**. Fortunately, since environment variables are managed by Heroku, any accidental changes will be overwritten by Heroku's configuration during deployment. Always restore the `DEVELOPMENT_DATABASE` variable to its original value after making local changes to avoid unintended consequences.

Currently, there are three separate databases that Reoptinew relies on. One for testing, another for development, and another for production. 

- **Testing database**

    - Designed to be a "clean sheet" for running automated tests. It provides a temporary environment where all data exists in memory and is completely erased after the tests finish. This ensures no impact on development or production data during the testing process.

- **Development Database**

    - Intended for local development and debugging. It contains data specific to the development process and is configured to be easily replaceable if needed.

- **Production Database**

    - Stores real user data and operates in a secure, live environment.

### Models

You can find the complete data schema for all models in this [Google Drive folder](https://drive.google.com/drive/folders/1WrPCJ0CRQjOo84iZWGu7mcBEgYjKUaZA?usp=sharing). 

![Post model](docs/assets/iteration_1/post_model.webp "A spreadsheet of the post model.")

## Technologies

See [requirements.txt](requirements.txt) for the full third party packages list.


### Programming languages

<details>
    <summary>
        Python
    </summary>

**A popular language famous for its readability and efficiency in back-end development.** 

</details>

### Frameworks

<details>
    <summary>
        Django
    </summary>

**A web framework that simplifies the creation of secure and scalable web applications.**

</details>

<details>
    <summary>
        Django REST Framework (DRF):
    </summary>

**An extension of Django for building feature-rich, RESTful APIs.**

</details>

### Cloud services

<details>
    <summary>
        Cloudinary
    </summary>

**A cloud-based service for managing, storing, and delivering media assets like images and videos.**

</details>

### Environment Management

<details>
    <summary>
        python-decouple
    </summary>

**A lightweight library for separating configuration settings from source code, improving maintainability and security.**

</details>

### Additional libraries

<details>
    <summary>
        dj-database-url
    </summary>

**A utility to configure database connections using a single database URL, simplifying the transition between development, testing, and production environments.**

</details>

<details>
    <summary>
        psycopg2-binary
    </summary>

**A PostgreSQL adapter for Python, enabling seamless integration with PostgreSQL databases.**

</details>

<details>
    <summary>
        pillow
    </summary>

**A library for image processing in Python, supporting tasks like image resizing, format conversion, and filtering.**

</details>

<details>
    <summary>
        django-cors-headers
    </summary>

**A middleware for handling Cross-Origin Resource Sharing (CORS) in Django, ensuring secure communication between the front-end and back-end.**

</details>

<details>
    <summary>
        django-cloudinary-storage
    </summary>

**A package for integrating Cloudinary with Django, providing a way to manage media files in the cloud.**

</details>
