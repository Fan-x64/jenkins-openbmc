from locust import HttpUser, task, between

class Website(HttpUser):
    host = "https://127.0.0.1:2443"
    wait_time = between(1, 3)

    @task
    def on_start(self):
        self.client.auth = ('root', '0penBmc')
        self.client.verify = False

    @task(1)
    def get_system_info(self):
        self.client.get("/redfish/v1/Systems/system")

    @task(1)
    def get_power_state(self):
        self.client.get("/redfish/v1/Systems/system")
        
    @task(1)
    def get_power_state(self):
        self.client.get("/redfish/v1/Systems/system")
        
class PublicAPI(HttpUser):
    host = "https://jsonplaceholder.typicode.com"
    wait_time = between(1, 5)

    @task(1)
    def get_JSONPlaceholder(self):
        self.client.get("https://jsonplaceholder.typicode.com/posts")
    
    def get_weather(self):
        self.client.get("https://wttr.in/Novosibirsk?format=j1")