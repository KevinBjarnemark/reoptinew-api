# Reoptinew API

**Navigate to the deployed API** [here](https://reoptinew-api-c16dc2520739.herokuapp.com/) 🔥

## Table of Contents

- 🗺️ [Project Map](#map)
- 🎨 [Frontend](#frontend)
- 🧬🍴 [Cloning and Forking the Repository](#cloning-and-forking-the-repository)
- 🏃‍♂️ [Run the App](#run-the-app)
- ☁️ [Deployment, CI/CD Pipeline, and Automatic Testing](#deployment-cicd-pipeline-and-automatic-testing)
- 🛢️ [Databases](#databases)
- 🐞 [Troubleshooting, Debugging, and Logging](#troubleshooting-debugging-and-logging)
- ❌ [Error handling](#error-handling)
- 🛠️ [Technologies](#technologies)
- 🔧 [Testing](#testing)
- ✨ [Credits](#credits)
- 🖊️ [References](#references)

## Project Map 

The "map" below provides an overview of key resources in this project. 

#### External resources

- 🖥️ [Live web app](https://reoptinew-09d333f23d8e.herokuapp.com/)  
- 🎨 [Frontend repository (with documentation)](https://github.com/KevinBjarnemark/reoptinew). 

#### Documentation

- 📉 [First iteration](https://github.com/KevinBjarnemark/reoptinew/blob/main/docs/iteration-1/README.md)  
- 📉 [Sprints](https://github.com/KevinBjarnemark/reoptinew/tree/main/docs/iteration-1/sprints)  
- 📃 [GitHub Projects (Kanban)](https://github.com/users/KevinBjarnemark/projects/10).

## Frontend

The Reoptinew web app uses a decoupled architecture, separating the frontend and backend repositories. The **frontend repository** can be found [**here**](https://github.com/KevinBjarnemark/reoptinew).

## Cloning and Forking the Repository

To avoid repeating ourselves too much we've used the frontend repository as a base for certain information. The cloning and forking have been explained in the [frontend repository's documentation](https://github.com/KevinBjarnemark/reoptinew) and the process should be the same for this repository.

**Note** that Python doesn't create an environment by default, like node does by generating a `node_modules` folder. If you want to containerize this API locally and also ensure it's functionality remains functional over time, follow the steps below.

> ❕ **Info**  
> There are other ways of creating a virtual environment and the below example is just one way of doing it.

- Open your terminal
- Go to your project folder
    > ⚠️ **NOTE**  
    > We'll create the virtual environment one level above the project folder
    ```bash
    cd "path/to/your/project_folder"
    ```
- Create the environment 
    ```bash
    python -m venv venv
    ```
- Activate the environment
    ```bash
    .\venv\scripts\activate
    ```
- Install dependencies
    ```bash
    python -m pip install --upgrade setuptools
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    ```
- Enter the project
    ```bash
    cd reoptinew-api
    ```

## Run the app

After [cloning or forking the repository](#cloning-and-forking-the-repository) on your side, you're almost there. Follow the steps below.

- Configure environment variables
    - The [.env.example](.env.example) file serves as your guide for configuring environment variables. 

- Apply Migrations

> ⚠️ **NOTE**  
> This is an important step as it will not only migrate the database but also **auto-populate** many-to-many fields. Users are restricted from editing these so they have to be added manually (or automatically by running `python manage.py migrate`).

```bash
python manage.py makemigrations
python manage.py migrate
```

After configuring the environment variables and migrating the database, you should be able to run the app with the following command.

> ⚠️ **NOTE**  
> Again, to use a specific IP Address like this is a security feature. Never expose this address in the repository. 

> ❕ **Info**  
> If you don't know your IP Adress you can find it by simply running `ipconfig` in your terminal. Look for the `IPv4 Address`.

```bash
py manage.py runserver <your-ip-address>:8000
```

## Deployment, CI/CD Pipeline, and Automatic Testing

Reoptinew's deployment process is almost exactly the same for the frontend as with the backend. Since this process is already explained in full detail, we advise you to reference the [frontend repository's documentation](https://github.com/KevinBjarnemark/reoptinew). This includes guides how to set everything up including automatic testing both locally and within the GitHub Actions environment.

If you're new to `Heroku`, `deployment`, `CI/CD pipelines`, and `automatic testing`, we suggest you **start by configuring the frontend repository**. This should familiarize you with this the processes involved. When you feel comfortable deploying the frontend, there are only a few differences to be aware of when deploying the API.

#### Key Differences

The `heruko/python` buildpack, a slightly altered [deploy.yml](.github/workflows/deploy.yml) file tailored to `Python` and some environment variables that needs to be configured. That's about it!


##### Environment Variables

At this stage, Heroku is unaware of your environment variables. This is because we've made sure these are kept secure and local, using the [.gitignore](.gitignore) file. Nevertheless, Heruko must have access to some variables such as the `DATABASE_URL` and `CLOUDINARY_URL`.
> ⚠️ **SECURITY NOTE**  
> While we've already secured our varibles by excluding them from the repository, it's worth noting that it's not as simple as just adding them to Heroku. We've added a [.env.production.example](.env.production.example) file to exemplify how to configure the variables on Heoku. You may reference this file and compare it to the [.env.example](.env.example) file to see how they differ.

Add the variables to Heroku by following these steps.

- Click on the `Settings` tab.
- Scroll down and `Reveal Config Vars`
- Add each environment variable 

##### heruko/python buildpack

In the frontend we added the `heroku/node.js` buildpack, this is not needed in the API because node is not used. Instead add the `heruko/python` buildpack.

###### CI/CD Pipeline and Automatic Testing

In the [deploy.yml](.github/workflows/deploy.yml) file, there are some differences compared with the frontend repository. While the Heroku deployment is the same, there are some environment differences. 

For starters, instead of testing with `Jest`, we use `pytest`, example below. 

```yml
- name: Run Django tests
run: pytest
env:
    DJANGO_SETTINGS_MODULE: config.settings
    # Override DATABASE_URL during tests
    DATABASE_URL: "sqlite:///:memory:" 
    DEV_SERVER_HOST: ${{ secrets.DEV_SERVER_HOST }}
    DEV_SERVER_PORT: ${{ secrets.DEV_SERVER_PORT }}
    DEV_SERVER_FRONTEND_PORT: ${{ secrets.DEV_SERVER_FRONTEND_PORT }}
```

If you want to also configure a `Git Hook` to test locally before pushing, you can use a similar pre-push hook, like the one below. Again since we're not using `Node` or `Jest`, the pre-push hook should call `pytest` instead. 

```bash
#!/bin/bash
echo "Running tests before pushing..."

# Activate virtual environment for Python
source venv\Scripts\activate

# Run pytest for Django tests
pytest
PYTHON_STATUS=$?

# Check if any tests failed
if [ $PYTHON_STATUS -ne 0 ]; then
    echo "Tests failed. Push aborted."
    exit 1
else
    echo "All tests passed! Proceeding with push."
    exit 0
fi
```

## Testing

### Manual Testing

#### Test cases

Below are some examples of how you can test specific HTTP endpoints in `cmd`. You can also use other tools such as [Postman](https://www.postman.com/) to test HTTP endpoints.

```bash
# Simple GET request 
curl -X GET -i http://{DEV_SERVER_HOST}:{DEV_SERVER_PORT}/users/profile/<username>/

# POST request (JSON)
curl -X POST -i "http://{DEV_SERVER_HOST}:{DEV_SERVER_PORT}/posts/ratings/<post-id>/" ^
-H "Content-Type: application/json" ^
-H "Authorization: Bearer <access-token>" ^
-d "{\"saves_money\": 0, \"saves_time\": 50, \"is_useful\": 100}"

# POST request (FormData)
curl -X POST "http://{DEV_SERVER_HOST}:{DEV_SERVER_PORT}/users/login/" ^
-H "Content-Type: multipart/form-data" ^
--form "username=<username>" ^
--form "password=<password>" ^
-i
```

##### Examples

```bash
# Create user
curl -X POST "http://{DEV_SERVER_HOST}:{DEV_SERVER_PORT}/users/signup/" ^
-H "Content-Type: multipart/form-data" ^
--form "username=<username>" ^
--form "password=<password>" ^
--form "confirm_password=<password>" ^
--form "birth_date=1995-01-01" ^
-i

# Log in user
curl -X POST "http://{DEV_SERVER_HOST}:{DEV_SERVER_PORT}/users/login/" ^
-H "Content-Type: multipart/form-data" ^
--form "username=<username>" ^
--form "password=<password>" ^
-i

# Fetch all posts
curl -X GET -i "http://{DEV_SERVER_HOST}:{DEV_SERVER_PORT}/posts/posts/" ^
-H "Authorization: Bearer <access-token>" ^

# Create post
curl -X POST "http://{DEV_SERVER_HOST}:{DEV_SERVER_PORT}/posts/posts/" ^
-H "Content-Type: multipart/form-data" ^
-H "Authorization: Bearer <access-token>" ^
--form "action=create" ^
--form "title=Test Title" ^
--form "description=Test description" ^
--form "instructions=Test instructions" ^
--form "default_image_index=1" ^
--form "tags=test" ^
--form "harmful_post=true" ^
--form "harmful_tool_categories=[\"Sharp or Cutting Tools\"]" ^
--form "harmful_material_categories=[\"Radioactive Materials\"]" ^
--form "tools=[{\"quantity\": \"1\", \"name\": \"Screw driver\", \"description\": \"Manual or electric\"}]" ^
--form "materials=[{\"quantity\": \"10\", \"name\": \"wooden boards\", \"description\": \"Any wood type will do\"}]" ^
-i

# Rate post
curl -X POST -i "http://{DEV_SERVER_HOST}:{DEV_SERVER_PORT}/posts/ratings/<post-id>/" ^
-H "Content-Type: application/json" ^
-H "Authorization: Bearer <access-token>" ^
-d "{\"saves_money\": 0, \"saves_time\": 50, \"is_useful\": 100}"
```


> ⚠️ **NOTE**  
> Make sure your `IP address` is the same as the `DEV_SERVER_HOST` environment variable when testing locally.

> ❕ **Keep In Mind**  
> 1. Whenever you see the `multipart/form-data` header in any of the test cases below, the data must be  converted into FormData like we just showed you (example above).  
> 2. Whenever working with user-related endpoints we'll use the username `testUser` and password `securePassword`, you can replace this user if you want. But remember, sometimes the user must exist in order for the endpoint to function as expected.  
> 3. You should have some knowledge about access and refresh tokens. For example, when logging in a user, you will get the refresh token that can be used throughout the testing process. However, these tokens can expire and change as you call certian endpoints.

##### Users

| **Test Case ID** | **Feature** | **Headers** | **HTTP Method & Endpoint** | **Test Steps** | **Expected Result** | **Actual Result** | **Pass/Fail**
|------------------|------------|------------|---------------|--------------------|------------------|-------------| ------------|
| TC-001 | **Sign up** | Content-Type: multipart/form-data | POST /users/api/token/refresh/ | Send a POST request with {"username": testUser", "password": "securePassword", "confirm_password": "securePassword", "birth_date": "1995-01-01"} | HTTP Status: 201 <br> Data: {"message":"Account successfully registered.", "refresh":"{refresh-token}", "access": "{access-token}"} | The server responded with {"message":"Account successfully registered.", "refresh":"{refresh-token}", "access": "{access-token}"} and the HTTP status was 201| ✅ Pass | |
| TC-002 | **Login** | Content-Type: multipart/form-data | POST users/login/ | Send a POST request with { "username": "testUser", "password": "securePassword" } | HTTP status: 201 <br> Data: {"message": "Login successful.", "refresh": "{refresh-token}", "access": "{access-token}"} | The server responded with {"message": "Login successful.", "refresh": "{refresh-token}", "access": "{access-token}"} and the HTTP status was 201 | ✅ Pass | |
| TC-003 | **Logout** | Content-Type: application/json <br> Authorization: Bearer {access-token} | POST users/logout/ | Send a POST request as a logged in user | HTTP Status: 200 <br> Data: {"message":"Successfully logged out."} | The server responded with {"message":"Successfully logged out."} and the HTTP status was 200| ✅ Pass | |
| TC-004 | **Get user's profile** | | GET /users/profile/testUser/ | Send a GET request | HTTP Status: 200 <br> Data: {"id": {profile-id} ,"user_id": {user-id}, "image": "{image-url}", "username": "testUser","followers": [],"following": []} | The server responded with{"id": {profile-id} ,"user_id": {user-id}, "image": "{image-url}", "username": "testUser","followers": [],"following": []}  and the HTTP status was 200| ✅ Pass | |
| TC-005 | **Refresh Token** | Content-Type: application/json | POST /users/api/token/refresh/ | Send a POST request with {"refresh": "{refresh-token}"} | HTTP Status: 200 <br> Data: {"refresh": "{refreshed-token}", access: "{updated-access-token}"} | The server responded with {"refresh": "{refreshed-token}", access: "{updated-access-token}"} and the HTTP status was 200| ✅ Pass | |
| TC-006 | **Follow** | Authorization: Bearer {access-token} | POST users/follow/{user-id}/ | Send a POST request | HTTP Status: 201 <br> Data: {"message":"Followed successfully!","id": {user-id}} | The server responded with {"message":"Followed successfully!","id":{user-id}} and the HTTP status was 201| ✅ Pass | |
| TC-007 | **Unfollow** | Authorization: Bearer {access-token} | DELETE users/follow/{user-id}/ | Send a DELETE request | HTTP Status: 201 <br> Data: {"message":"Unfollowed successfully!"} | The server responded with {"message":"Unfollowed successfully!"} and the HTTP status was 201| ✅ Pass | |
| TC-008 | **Unfollow as a guest** | | DELETE users/follow/{user-id}/ | Send a DELETE request but as a guest | HTTP Status: 401 <br> Data: {"detail":"Authentication credentials were not provided."} | The server responded with {"detail":"Authentication credentials were not provided."} and the HTTP status was 401| ✅ Pass | |
| TC-009 | **Follow as a guest** | | POST users/follow/{user-id}/ | Send a POST request but as a guest | HTTP Status: 401 <br> Data: {"detail":"Authentication credentials were not provided."} | The server responded with {"detail":"Authentication credentials were not provided."} and the HTTP status was 401| ✅ Pass | |
| TC-010 | **Follow Yourself** | Authorization: Bearer {access-token} | POST users/follow/{user-id}/ | Send a POST request but with the currently logged in user's id | HTTP Status: 400 <br> Data: {"error_message":"You cannot follow yourself."} | The server responded with {"error_message":"You cannot follow yourself."} and the HTTP status was 400| ✅ Pass | |

![Separator](docs/assets/separators/separator.png "A gray bar.")

##### Posts

| **Test Case ID** | **Feature** | **Headers** | **HTTP Method & Endpoint** | **Test Steps** | **Expected Result** | **Actual Result** | **Pass/Fail**
|------------------|------------|------------|---------------|--------------------|------------------|-------------| ------------|
| TC-001 | **Create Post** | Content-Type: multipart/form-data <br> Authorization: Bearer {access-token} | POST /posts/posts/ | Send a POST request with { "action": "create", "title": "Test Title", "description": "Test description", "instructions": "Test instructions", "default_image_index": 1, "tags": "test", "harmful_post": true, "harmful_tool_categories": ["Sharp or Cutting Tools"], "harmful_material_categories": ["Radioactive Materials"], "tools": [{"quantity": "1","name": "Screw driver","description": "Manual or electric"}], "materials": [{"quantity": "10","name": "wooden boards","description": "Any wood type will do"}]} | HTTP Status: 201 <br> Data: {"id": "{post-id}", "title": "Test Title", "description": "Test description", "instructions": "Test instructions", "created_at":"{creation-date}","author":{"id": "{user-id}", "username": "testUser", "image":"{image-url}"}, "default_image_index": 1, "harmful_post":true, "tags": "test", "image":null, "ratings": {"saves_money":0, "saves_time": 0, "is_useful": 0},"comments": [], "harmful_tool_categories": ["Sharp or Cutting Tools"], "harmful_material_categories": ["Radioactive Materials"], "tools": [{"quantity": "1", "name": "Screw driver", "description": "Manual or electric"}], "materials":[{"quantity": "10", "name": "wooden boards", "description": "Any wood type will do"}], "likes":{"user_has_liked": false, "count": 0}} | The server responded with {"id": "{post-id}", "title": "Test Title", "description": "Test description", "instructions": "Test instructions", "created_at":"{creation-date}","author":{"id": "{user-id}", "username": "testUser", "image":"{image-url}"}, "default_image_index": 1, "harmful_post":true, "tags": "test", "image":null, "ratings": {"saves_money":0, "saves_time": 0, "is_useful": 0},"comments": [], "harmful_tool_categories": ["Sharp or Cutting Tools"], "harmful_material_categories": ["Radioactive Materials"], "tools": [{"quantity": "1", "name": "Screw driver", "description": "Manual or electric"}], "materials":[{"quantity": "10", "name": "wooden boards", "description": "Any wood type will do"}], "likes":{"user_has_liked": false, "count": 0}} and the HTTP status was 201| ✅ Pass | |
| TC-002 | **Delete Post** | Authorization: Bearer {access-token} | DELETE /posts/post/delete-post/{post-id}/ | Send a DELETE request | HTTP Status: 200 <br> Data: {"message":"Deleted post successfully."} | The server responded with {"message":"Deleted post successfully."} and the HTTP status was 200| ✅ Pass | |
| TC-003 | **Rate Post** | Content-Type: application/json <br> Authorization: Bearer {access-token} | POST posts/ratings/{post-id}/ | Send a POST request with {"saves_money": 0, "saves_time": 50, "is_useful": 100} | HTTP Status: 201 <br> Data: {"message":"Rating submitted successfully!","ratings":{"saves_money":0,"saves_time":50,"is_useful":100}} | The server responded with {"message":"Rating submitted successfully!","ratings":{"saves_money":0,"saves_time":50,"is_useful":100}} and the HTTP status was 201| ✅ Pass | |
| TC-004 | **Rate Post (restriction)** | Content-Type: application/json <br> Authorization: Bearer {access-token} | POST posts/ratings/{post-id}/ | Send a POST request to a post owned by the current user with {"saves_money": 0, "saves_time": 50, "is_useful": 100} | HTTP Status: 403 <br> Data: {"error_message":"You cannot rate your own post."} | The server responded with {"error_message":"You cannot rate your own post."} and the HTTP status was 403| ✅ Pass | |
| TC-005 | **Comment on Post** | Content-Type: application/json <br> Authorization: Bearer {access-token} | POST posts/comments/{post-id}/ | Send a POST request with {"text": "Test comment"} | HTTP Status: 201 <br> Data: {"id":{comment-id},"post":{post-id},"user":{user-id},"text":"Test comment","created_at": {creation-date}} | The server responded with {"id":{comment-id},"post":{post-id},"user":{user-id},"text":"Test comment","created_at": {creation-date}} and the HTTP status was 201| ✅ Pass | |
| TC-006 | **Like Post** | Content-Type: Authorization: Bearer {access-token} | POST posts/like/{post-id}/ | Send a POST request | HTTP Status: 201 <br> Data: {"message":"Post liked successfully!","id":{like-id}} | The server responded with {"message":"Post liked successfully!","id":{like-id}} and the HTTP status was 201| ✅ Pass | |
| TC-007 | **Like Post (already liked)** | Authorization: Bearer {access-token} | POST posts/like/{post-id}/ | Send a POST request to an already liked post | HTTP Status: 400 <br> Data: {"error_message":"You have already liked this post"} | The server responded with {"error_message":"You have already liked this post"} and the HTTP status was 400| ✅ Pass | |
| TC-008 | **Delete Like** | Authorization: Bearer {access-token} | DELETE posts/like/{post-id}/ | Send a DELETE request | HTTP Status: 200 <br> Data: {"message":"Like removed successfully!","post_id":164} | The server responded with {"message":"Like removed successfully!","post_id":164} and the HTTP status was 200| ✅ Pass | |
| TC-009 | **Delete Like (doesn't exist)** | Authorization: Bearer {access-token} | DELETE posts/like/{post-id}/ | Send a DELETE request for a like that doesn't exist | HTTP Status: 500 <br> Data: {"error_message":"Couldn't find like, nothing to remove."} | The server responded with {"error_message":"Couldn't find like, nothing to remove."} and the HTTP status was 500| ✅ Pass | |
| TC-010 | **Fetch All Posts** | Authorization: Bearer {access-token} | GET posts/posts/ | Send a GET request | HTTP Status: 200 <br> Data: [{id, title, description, instructions, created_at, author: {id, username, image}, default_image_index, harmful_post, tags, image, ratings: {saves_money, saves_time, is_useful}, comments: [{id, text, created_at, author: {id, username, image}}], harmful_tool_categories:[], harmful_material_categories:[], tools: [], materials :[],likes: {user_has_liked, count}}] | The server responded with [{id, title, description, instructions, created_at, author: {id, username, image}, default_image_index, harmful_post, tags, image, ratings: {saves_money, saves_time, is_useful}, comments: [{id, text, created_at, author: {id, username, image}}], harmful_tool_categories:[], harmful_material_categories:[], tools: [], materials :[],likes: {user_has_liked, count}}] and the HTTP status was 200| ✅ Pass | |
| TC-011 | **Fetch Single Post** | Authorization: Bearer {access-token} | GET posts/posts/{post-id}/ | Send a GET request | HTTP Status: 200 <br> Data: {id, title, description, instructions, created_at, author: {id, username, image}, default_image_index, harmful_post, tags, image, ratings: {saves_money, saves_time, is_useful}, comments: [{id, text, created_at, author: {id, username, image}}], harmful_tool_categories:[], harmful_material_categories:[], tools: [], materials :[],likes: {user_has_liked, count}} | The server responded with {id, title, description, instructions, created_at, author: {id, username, image}, default_image_index, harmful_post, tags, image, ratings: {saves_money, saves_time, is_useful}, comments: [{id, text, created_at, author: {id, username, image}}], harmful_tool_categories:[], harmful_material_categories:[], tools: [], materials :[],likes: {user_has_liked, count}} and the HTTP status was 200| ✅ Pass | |

![Separator](docs/assets/separators/separator.png "A gray bar.")

##### 🛡️ Age restriction

| **Test Case ID** | **Feature** | **Headers** | **HTTP Method & Endpoint** | **Test Steps** | **Expected Result** | **Actual Result** | **Pass/Fail**
|------------------|------------|------------|---------------|--------------------|------------------|-------------| ------------|
| TC-001 | **Fetch Single Post (user)** | Authorization: Bearer {access-token} | GET posts/posts/{post-id}/ | Send a GET request for a post that is age-restricted as a user under 16 years old | HTTP Status: 400 <br> Data: {"error_message":"You must be at least 16 years old to create, edit, and view a post that is considered to be inappropriate for children."} | The server responded with {"error_message":"You must be at least 16 years old to create, edit, and view a post that is considered to be inappropriate for children."} and the HTTP status was 400| ✅ Pass | |
| TC-002 | **Fetch Single Post (guest)** |  | GET posts/posts/{post-id}/ | Send a GET request for a post that is age-restricted as a guest | HTTP Status: 400 <br> Data: {"error_message":"You must be at least 16 years old to create, edit, and view a post that is considered to be inappropriate for children."} | The server responded with {"error_message":"You must be at least 16 years old to create, edit, and view a post that is considered to be inappropriate for children."} and the HTTP status was 400| ✅ Pass | |

## Databases

Currently, there are three separate databases that Reoptinew relies on. One for testing, another for development, and another for production. 

- **Testing database**

    - Designed to be a "clean sheet" for running automated tests. It provides a temporary environment where all data exists in memory and is completely erased after the tests finish. This ensures no impact on development or production data during the testing process.

- **Development Database**

    - Intended for local development and debugging. It contains data specific to the development process and is configured to be easily replaceable if needed.

- **Production Database**

    - Stores real user data and operates in a secure, live environment.

### Models

You can find the complete data schema for all models in this [Google Drive folder](https://drive.google.com/drive/folders/1WrPCJ0CRQjOo84iZWGu7mcBEgYjKUaZA?usp=sharing). 


![Post model](docs/assets/iteration_1/post-model.webp "A spreadsheet of the post model.")

## Troubleshooting, Debugging, and Logging

Printing to the console with `print()` in production is discouraged due to potential security and performance risks. Reoptinew instead relies on a custom logging system [logging.py](static/utils/logging.py) to ensure clarity, consistency, and controlled output.

- **Detailed Logs:**  
The [throw_error()](static/utils/error_handling.py) function captures all errors with contextual metadata, such as the file and function where the error occurred.

### File for tracking and debugging events 

The [debug.log](logs/debug.log) file is an automatically generated logging file for tracking and debugging the application.  

## Error Handling

Reoptinew’s error-handling system is built on three core principles: 

- **User experience**
- **Security** 
- **Troubleshooting**

### User Experience

The backend ensures that all errors sent to the frontend are clear, user-friendly, and meaningful. Error messages are mapped to custom messages that align with Reoptinew’s branding and interface standards. 

For additional UX details, visit the [**frontend repository**](https://github.com/KevinBjarnemark/reoptinew).

### Security

Reoptinew prioritizes security by implementing a **controlled error system** to eliminate risks associated with exposing raw backend data. 

Key benefits of this system include:

1. **Thorough Validation:**   
    Every piece of information sent to the client is inspected and sanitized.

2. **Backend Logic Protection:**  
    While Reoptinew's backend logic is open-source and fully transparent, the system ensures that runtime details, such as stack traces or low-level error messages, are not exposed to the frontend.

3. **Resilience Against Updates:**  
    Controlled error handling mitigates risks of application failures caused by changes in dependencies or library updates.

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

### Authentication

<details>
    <summary>
        PyJWT
    </summary>

**A Python library for JSON Web Tokens (JWT).**

PyJWT is a library for encoding and decoding JSON Web Tokens. It supports token signing and validation using various algorithms.

</details>

### Cloud services

<details>
    <summary>
        Cloudinary
    </summary>

**A cloud-based service for managing, storing, and delivering media assets like images and videos.**

</details>

### Testing

<details>
    <summary>
        Pytest
    </summary>

**A testing framework for Python applications.**

Pytest is a framework used for writing and running tests in Python. It supports features like fixtures, parameterized tests.

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

## Credits

    As the only developer working on this project, I will reference myself in 
    first-person and point you to some people, tools, and sources that 
    helped me along the way.

### Custom error messages

I've never worked with Django REST Framework (DRF) before, and unexpected challenges appeared when I was trying to customize error messages. My goal was to fully customize all error messages, simplifying complex errors with generic messages. But, I never figured out how to achieve that without allowing unchecked messages to slip through. This was mainly due to the fact that an error thrown in the model (before reaching the validate method) breaks code execution and stop further validation. 

However, [mariodev](https://stackoverflow.com/users/1566605/mariodev) in [this thread](https://stackoverflow.com/questions/26943985/custom-error-messages-in-django-rest-framework-serializer) had a perfect solution for customizing specified error message before reaching the validate() method.

Here's how I used his solution in [serializers.py](apps/users/serializers.py)
```python
# Overwrite default error messages with custom errors
def __init__(self, *args, **kwargs):
    super(SignUpSerializer, self).__init__(*args, **kwargs)
    self.fields['username'].error_messages['required'] = 'You must enter a username.'
    self.fields['username'].error_messages['blank'] = 'Username is missing.'
```

## Extensions

<details>
    <summary>
        Pylint
    </summary>

**Python Linter**

Pylint is a code analysis tool for Python that checks your code for errors, enforces coding standards, and offers suggestions to improve code quality. It supports customizable rules and integrates with most editors, helping maintain clean and maintainable Python code.

**Tip:** You don't need the Pylint package when using the extension (unless you want to include it in a CI/CD pipeline or similar). If you just want a configuration file, you can install Pylint temporarily and generate it with the command below.

```
pylint --generate-rcfile > .pylintrc
```

</details>

<details>
    <summary>
        Black
    </summary>

**Code formatting tool**

Black is a code formatting tool for Python that enforces a consistent style by reformatting your code. It prioritizes readability and avoids manual formatting by following strict and consistent rules. Specifically, I've been using the [VS Code extension](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter). [Here's](pyproject.toml) the configuration file.

</details>

## References

It's worth mentioning **source code references**. These references can be found in the project itself, particularly in the `venv` folder (if you're using a virtual environment). 

- For example, during the implementation of the error handling system, classes from `Lib/site-packages/rest_framework/fields.py` helped with gaining a deeper understanding of the underlying processes within the Django Rest Framework.

- [Django REST Framework docs](https://www.django-rest-framework.org/)
- [Django REST Framework (GitHub docs)](https://github.com/encode/django-rest-framework/tree/master/docs/api-guide)
- [JWT](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/getting_started.html)
