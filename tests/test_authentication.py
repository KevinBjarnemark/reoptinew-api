import json
from django.urls import reverse
from django.contrib.auth import get_user_model
import pytest

User = get_user_model()


# Check successful user signup
@pytest.mark.django_db
def test_authentication_actions(client):
    """
    Tests login, signup, and account deletion in that order.

    This test mimics real scenarios by using the client to
    send requests, then using the tokens received from the view.
    """
    signup_data = {
        "username": "testuser",
        "password": "securePassword",
        "confirm_password": "securePassword",
        "birth_date": "2000-01-01",
    }

    # Send POST request to the signup endpoint
    response = client.post(reverse('signup'), data=signup_data)
    # Parse the JSON response
    response_data = json.loads(response.content.decode("utf-8"))

    # Check if the response was successful
    assert response.status_code == 201  # Successful response
    assert "access" in response_data  # Access token field exists
    assert "refresh" in response_data  # Refresh token field exists
    # Response message is sent correctly
    assert response_data["message"] == "Account successfully registered."
    # No other fields than the ones declared are sent to the client
    assert set(response_data.keys()) == {"message", "access", "refresh"}

    # Use the access token to log in the user
    access_token = response_data["access"]
    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # Send a GET request to a protected endpoint
    protected_response = client.get(reverse("profile"), headers=auth_headers)
    # Parse the JSON response
    protected_response_data = json.loads(
        protected_response.content.decode("utf-8")
    )

    # Check if the response was successful
    assert protected_response.status_code == 200  # Successful access
    # Ensure user data matches the initial sign up data
    assert protected_response_data["username"] == signup_data["username"]
    assert protected_response_data["birth_date"] == signup_data["birth_date"]

    # Send a DELETE request for account deletion
    client.delete(
        reverse("delete_account"),
        headers={**auth_headers, "Content-Type": "application/json"},
        data=json.dumps({"password": signup_data["password"]}),
    )

    # Make sure the user got deleted
    user_exists = User.objects.filter(
        username=signup_data["username"]
    ).exists()
    assert not user_exists
