from locust import HttpUser, task, between

class TestUser(HttpUser):
    wait_time = between(1, 3)

    def login(self):
        res = self.client.post(
            "/auth/login",
            json={"username": "string", "password": "string"}
        )
        if res.status_code == 200:
            try:
                self.token = res.json()["data"]["accessToken"]
            except Exception:
                self.token = None
                print("토큰 파싱 실패:", res.text)
        else:
            self.token = None
            print("로그인 실패:", res.status_code, res.text)

    def on_start(self):
        self.login()

    @task
    def do_something(self):
        if not hasattr(self, "token") or self.token is None:
            # 토큰 없으면 재시도 (너무 자주 하면 안 됨)
            self.login()
            if not self.token:
                return
        self.client.post(
            "/stream",
            headers={"Authorization": f"Bearer {self.token}"},
        )
