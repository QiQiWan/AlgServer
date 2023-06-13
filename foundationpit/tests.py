from django.test import TestCase
from .models import FoundationCalculationTask
from FoundationAlg import AlgService
# Simulink the http client
from django.test import Client
import json
import os
from broadcast_service import broadcast_service
import time
# Create your tests here.

class FoundationCreateTest(TestCase):
    # This test example is used to test the FoundationPitAnalysor
    # First, post a foundation pit model into the link, and wait the foundation creating
    # Second, analyse the api quality and problems which will happen.
    # Third, verify whether the output of the algorithm is reasonable.
    def setUp(self):
        self.cal_ID = ''
        return super().setUp()
    
    def test_hello_world(self):
        cli = Client()
        response = cli.get('/foundationpit/HelloWorld')
        result = json.loads(response.content)
        self.assertEqual(result['data'], 'Hello World')
        # self.assertEqual(response.content['data'], 'Hello World')

    def test_model_calculate(self):
        self._task_generate()
        # broadcast_service.subscribe('polling', self._cal_result_verify)
        # broadcast_service.publish('polling')
        # self._cal_result_verify()
        broadcast_service.subscribe('polling', FoundationCreateTest._print_signal)
        print('waiting...')
        # time.sleep(1200)

    def _task_generate(self):
        cli = Client()
        with open(f'{os.getcwd()}/foundationpit/foundation_pit.json') as f:
            new_fp = f.read()

        response = cli.post(path='/foundationpit/StartCalTask',
                            data=new_fp,
                            content_type='application/json')

        res = json.loads(response.content)
        self.assertEqual(res['code'], 200)
        self.assertEqual(list(res['data'].keys()), ['task_result', 'task_status', 'task_id'])
        self.cal_ID = res['data']['task_id']

        # Verify the json input into the API is equal to the model created in tbe API
        task = FoundationCalculationTask.objects.get(calID=self.cal_ID)
        self.assertEqual(task.foundation_pit, new_fp)
        

    def _cal_result_verify(self):
        """Verify the result after calculate, call the API to query once in 10 seconds. The duration of interface polling is 120 seconds. 
        """
        # broadcast_service.subscribe('polling', self._polling_result_API)
        # broadcast_service.publish('polling')
        
        cli = Client()
        data = '{"id": "%s"}' % self.cal_ID
        for i in range(12):
            response = cli.post(path='/foundationpit/GetCalResult',
                                data=data,
                                content_type='application/json')
            res = json.loads(response.content)
            self.assertEqual(list(res['data'].keys()), ['status', 'data'])
            if (res['data']['status'] == 2):
                print('The model has been calculated!')
                return
            else:
                print(f'Waiting for calculating ... {i + 1}')
                time.sleep(10)
        print('Calculate failed!')


    @staticmethod
    def _print_signal():
        print("Calculate completely!")
            
        
        
    
    
        
