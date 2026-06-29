"""Test suite for Mergington High School API using AAA (Arrange-Act-Assert) pattern"""
from urllib.parse import quote


def test_get_root_redirects_to_static(client):
    """Test GET / redirects to static index.html (AAA pattern)"""
    # Arrange
    expected_redirect_url = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_redirect_url


def test_get_activities_returns_all_activities(client):
    """Test GET /activities returns all activities (AAA pattern)"""
    # Arrange
    expected_activity_count = 3

    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert len(data) == expected_activity_count
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_get_activities_includes_activity_details(client):
    """Test GET /activities returns complete activity details (AAA pattern)"""
    # Arrange
    required_fields = ["description", "schedule", "max_participants", "participants"]

    # Act
    response = client.get("/activities")
    data = response.json()
    chess_club = data["Chess Club"]

    # Assert
    assert response.status_code == 200
    for field in required_fields:
        assert field in chess_club


def test_get_activities_participants_list_is_array(client):
    """Test GET /activities participants field is a list (AAA pattern)"""
    # Arrange
    # (fresh_activities fixture already set up)

    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    for activity_name, activity_data in data.items():
        assert isinstance(activity_data["participants"], list)


def test_signup_new_participant_success(client):
    """Test POST /signup successfully registers a new participant (AAA pattern)"""
    # Arrange
    activity_name = "Chess Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert result["message"] == f"Signed up {email} for {activity_name}"


def test_signup_adds_participant_to_activity(client):
    """Test signup actually adds participant to activity list (AAA pattern)"""
    # Arrange
    activity_name = "Programming Class"
    email = "alice@mergington.edu"

    # Act
    client.post(f"/activities/{activity_name}/signup?email={email}")
    activities_data = client.get("/activities").json()

    # Assert
    assert email in activities_data[activity_name]["participants"]


def test_signup_nonexistent_activity_returns_404(client):
    """Test POST /signup with invalid activity returns 404 (AAA pattern)"""
    # Arrange
    invalid_activity = "Nonexistent Club"
    email = "student@mergington.edu"
    expected_detail = "Activity not found"

    # Act
    response = client.post(f"/activities/{invalid_activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == expected_detail


def test_signup_duplicate_participant_returns_400(client):
    """Test POST /signup for duplicate registration returns 400 (AAA pattern)"""
    # Arrange
    activity_name = "Chess Club"
    email = "student@mergington.edu"
    # Sign up once
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act - attempt duplicate signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_multiple_participants_same_activity(client):
    """Test multiple different participants can sign up for same activity (AAA pattern)"""
    # Arrange
    activity_name = "Gym Class"
    emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]

    # Act
    for email in emails:
        client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    activities_data = client.get("/activities").json()
    for email in emails:
        assert email in activities_data[activity_name]["participants"]
    assert len(activities_data[activity_name]["participants"]) == 3


def test_unregister_participant_success(client):
    """Test POST /unregister successfully removes a participant (AAA pattern)"""
    # Arrange
    activity_name = "Chess Club"
    email = "student@mergington.edu"
    # Sign up first
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert result["message"] == f"Unregistered {email} from {activity_name}"


def test_unregister_removes_participant_from_activity(client):
    """Test unregister actually removes participant from list (AAA pattern)"""
    # Arrange
    activity_name = "Programming Class"
    email = "bob@mergington.edu"
    # Sign up first
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    client.post(f"/activities/{activity_name}/unregister?email={email}")
    activities_data = client.get("/activities").json()

    # Assert
    assert email not in activities_data[activity_name]["participants"]


def test_unregister_nonexistent_activity_returns_404(client):
    """Test POST /unregister with invalid activity returns 404 (AAA pattern)"""
    # Arrange
    invalid_activity = "Nonexistent Club"
    email = "student@mergington.edu"
    expected_detail = "Activity not found"

    # Act
    response = client.post(f"/activities/{invalid_activity}/unregister?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == expected_detail


def test_unregister_not_signed_up_returns_400(client):
    """Test POST /unregister for non-participant returns 400 (AAA pattern)"""
    # Arrange
    activity_name = "Chess Club"
    email = "not_signed_up@mergington.edu"
    expected_detail = "This student is not signed up for this activity"

    # Act
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == expected_detail


def test_signup_then_unregister_workflow(client):
    """Test complete workflow: signup then unregister (AAA pattern)"""
    # Arrange
    activity_name = "Programming Class"
    email = "charlie@mergington.edu"

    # Act - Sign up
    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert signup successful
    assert signup_response.status_code == 200
    activities_after_signup = client.get("/activities").json()
    assert email in activities_after_signup[activity_name]["participants"]

    # Act - Unregister
    unregister_response = client.post(f"/activities/{activity_name}/unregister?email={email}")

    # Assert unregister successful and participant removed
    assert unregister_response.status_code == 200
    activities_after_unregister = client.get("/activities").json()
    assert email not in activities_after_unregister[activity_name]["participants"]


def test_multiple_activities_independent_participants(client):
    """Test participants in different activities are independent (AAA pattern)"""
    # Arrange
    activity1 = "Chess Club"
    activity2 = "Gym Class"
    email1 = "student1@mergington.edu"
    email2 = "student2@mergington.edu"

    # Act
    client.post(f"/activities/{activity1}/signup?email={email1}")
    client.post(f"/activities/{activity2}/signup?email={email2}")

    # Assert
    activities_data = client.get("/activities").json()
    assert email1 in activities_data[activity1]["participants"]
    assert email1 not in activities_data[activity2]["participants"]
    assert email2 not in activities_data[activity1]["participants"]
    assert email2 in activities_data[activity2]["participants"]


def test_signup_with_special_characters_in_email(client):
    """Test signup handles email addresses with special characters (AAA pattern)"""
    # Arrange
    activity_name = "Chess Club"
    email = "student+test@mergington.edu"
    encoded_email = quote(email)

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={encoded_email}")

    # Assert
    assert response.status_code == 200
    activities_data = client.get("/activities").json()
    assert email in activities_data[activity_name]["participants"]


def test_signup_with_url_encoded_activity_name(client):
    """Test signup handles URL encoded activity names (AAA pattern)"""
    # Arrange
    activity_name = "Chess Club"
    email = "student@mergington.edu"

    # Act - URL encode the activity name
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    activities_data = client.get("/activities").json()
    assert email in activities_data[activity_name]["participants"]
