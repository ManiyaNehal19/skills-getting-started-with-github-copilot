from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def test_root_redirects_to_static_index():
    # Arrange
    expected_substring = "Mergington High School"

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert expected_substring in response.text


def test_get_activities_returns_all_activities():
    # Arrange
    expected_activities = activities.copy()

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    new_email = "teststudent@mergington.edu"
    if new_email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(new_email)

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
    assert new_email in activities[activity_name]["participants"]

    # Cleanup
    activities[activity_name]["participants"].remove(new_email)


def test_signup_for_missing_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent"
    email = "user@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_removes_existing_student():
    # Arrange
    activity_name = "Gym Class"
    email = "removetest@mergington.edu"
    if email not in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].append(email)

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_remove_missing_participant_returns_404():
    # Arrange
    activity_name = "Gym Class"
    email = "missing@mergington.edu"
    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
