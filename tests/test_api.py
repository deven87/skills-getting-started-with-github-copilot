import pytest


class TestGetActivities:
    def test_get_activities_returns_all_activities(self, client):
        # Arrange
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class",
            "Basketball Team", "Soccer Club", "Art Club",
            "Music Band", "Debate Club", "Science Club"
        ]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        for activity_name in expected_activities:
            assert activity_name in activities
            assert "description" in activities[activity_name]
            assert "schedule" in activities[activity_name]
            assert "max_participants" in activities[activity_name]
            assert "participants" in activities[activity_name]

    def test_get_activities_returns_participants_list(self, client):
        # Arrange
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert isinstance(activities["Chess Club"]["participants"], list)
        assert len(activities["Chess Club"]["participants"]) > 0


class TestSignup:
    def test_signup_successful(self, client):
        # Arrange
        email = "test@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity}"

    def test_signup_already_registered(self, client):
        # Arrange
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_activity_not_found(self, client):
        # Arrange
        email = "test@mergington.edu"
        activity = "Non-existent Activity"

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_adds_participant(self, client):
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club"

        # Act
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert email in activities[activity]["participants"]


class TestUnregister:
    def test_unregister_successful(self, client):
        # Arrange
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])

        # Act
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_not_registered(self, client):
        # Arrange
        email = "notregistered@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_activity_not_found(self, client):
        # Arrange
        email = "michael@mergington.edu"
        activity = "Non-existent Activity"

        # Act
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_removes_participant(self, client):
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"

        # Act
        client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert email not in activities[activity]["participants"]


class TestRedirect:
    def test_root_redirects_to_static(self, client):
        # Arrange
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]