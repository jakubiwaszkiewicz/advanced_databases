from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 2)  # short wait for faster requests

    @task
    def get_available_cars(self):
        self.client.get("/api/available-cars", params={
            "location_id": 2,
            "start_date": "2025-03-01",
            "end_date": "2025-03-10"
        })
