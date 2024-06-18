import json

from locust import HttpUser, between, task, constant_pacing
from locust import events
from datetime import datetime, timedelta

''' This Locust file uses custom shape load test
    which means the load is not a simple linear ramp up or 
    ramp down. 
    Instead a varying production-like load is applied for 
    a long duration.
'''

class MyUser(HttpUser):
    wait_time = constant_pacing(1)

    def on_start(self):
        self.start_time = datetime.now()
        self.run_duration = timedelta(hours=1)

    '''Varies the load factor based on time 
        elapsed since the script has started
        0.5 means 50%
        '''
    def shape_load(self, current_minute):
        if current_minute < 15:
            return 0.5
        elif current_minute < 45:
            return 1.0
        elif current_minute < 55:
            return 0.5
        else:
            return 0.0

    @task
    def get_order_details(self):
        current_minute = (datetime.now() - self.start_time).seconds // 60
        load_factor = self.shape_load(current_minute)
        if load_factor > 0:
            response = self.client.get('/getOrderDetails')
            assert response.status_code == 200
            events.request_success.fire(request_type="GET", name="getOrderDetails", response_time=response.elapsed.total_seconds(), response_length=len(response.content))
        self.environment.runner.quit()

    @task
    def create_order(self):
        current_minute = (datetime.now() - self.start_time).seconds // 60
        load_factor = self.shape_load(current_minute)
        if load_factor > 0:
            headers = {'Content-Type': 'application/json'}
            with open('../data_files/create_order.json', 'r') as file:
                payload = json.load(file)
            response = self.client.post('/createOrder', json=payload, headers=headers)
            assert response.status_code == 201
            events.request_success.fire(request_type="POST", name="createOrder", response_time=response.elapsed.total_seconds(), response_length=len(response.content))
        self.environment.runner.quit()