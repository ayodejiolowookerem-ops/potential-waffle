import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestRootEndpoint:
    def test_get_root_redirects_to_static_index(self):
        # Arrange: No special setup needed

        # Act: Make GET request to root without following redirects
        response = client.get("/", follow_redirects=False)

        # Assert: Should redirect to static index
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    def test_get_activities_returns_all_activities(self):
        # Arrange: No special setup needed

        # Act: Make GET request to activities
        response = client.get("/activities")

        # Assert: Should return 200 and contain expected activities
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        # Verify structure of one activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignupEndpoint:
    def test_signup_successful(self):
        # Arrange: Use an activity and email not already signed up
        activity = "Gym Class"
        email = "newstudent@mergington.edu"

        # Act: Make POST request to signup
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert: Should return 200 and success message
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert f"Signed up {email} for {activity}" in data["message"]

        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]

    def test_signup_duplicate_participant(self):
        # Arrange: Use an activity and email already signed up
        activity = "Chess Club"
        email = "michael@mergington.edu"  # Already in the data

        # Act: Make POST request to signup
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert: Should return 400 with error message
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Student already signed up for this activity" in data["detail"]

    def test_signup_nonexistent_activity(self):
        # Arrange: Use a non-existent activity
        activity = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act: Make POST request to signup
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert: Should return 404 with error message
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]


class TestRemoveParticipantEndpoint:
    def test_remove_participant_successful(self):
        # Arrange: First sign up a participant, then remove
        activity = "Basketball Team"
        email = "teststudent@mergington.edu"
        # Sign up first
        client.post(f"/activities/{activity}/signup?email={email}")

        # Act: Make DELETE request to remove participant
        response = client.delete(f"/activities/{activity}/participants/{email}")

        # Assert: Should return 200 and success message
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert f"Removed {email} from {activity}" in data["message"]

        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity]["participants"]

    def test_remove_participant_not_signed_up(self):
        # Arrange: Try to remove a participant not signed up
        activity = "Tennis Club"
        email = "notsignedup@mergington.edu"

        # Act: Make DELETE request to remove participant
        response = client.delete(f"/activities/{activity}/participants/{email}")

        # Assert: Should return 400 with error message
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Student not signed up for this activity" in data["detail"]

    def test_remove_participant_nonexistent_activity(self):
        # Arrange: Use a non-existent activity
        activity = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act: Make DELETE request to remove participant
        response = client.delete(f"/activities/{activity}/participants/{email}")

        # Assert: Should return 404 with error message
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]