import time
import random
from locust import HttpUser, task, between


class AIVisibilityLoadTestUser(HttpUser):
    """Locust Load Test User simulating high-throughput user scenarios (100 to 1000 concurrent users)."""

    wait_time = between(0.1, 0.5)

    def on_start(self):
        """Pre-authenticates load test user session."""
        self.user_email = f"loadtest_{random.randint(10000, 99999)}@example.com"
        self.password = "LoadTestPass123!"
        
        # Register user
        self.client.post(
            "/api/v1/auth/register",
            json={"email": self.user_email, "password": self.password},
            name="/auth/register"
        )
        
        # Login and obtain token
        login_res = self.client.post(
            "/api/v1/auth/login",
            json={"email": self.user_email, "password": self.password},
            name="/auth/login"
        )
        if login_res.status_code == 200:
            token = login_res.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {token}"}
        else:
            self.headers = {}

    @task(3)
    def test_health_probes(self):
        """Simulates container health and metrics probe queries."""
        self.client.get("/health", name="/health")
        self.client.get("/ready", name="/ready")

    @task(2)
    def test_list_projects(self):
        """Simulates project listing dashboard query."""
        self.client.get("/api/v1/projects", headers=self.headers, name="/projects")

    @task(1)
    def test_prompt_catalog(self):
        """Simulates static prompt catalog query."""
        self.client.get("/api/v1/prompts", name="/prompts")
