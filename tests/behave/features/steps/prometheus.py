from behave import given, then
import requests
from prometheus_client.parser import text_string_to_metric_families

import urllib
import time


@given('send GET request')
def send_get_request(context):
    context.response = requests.get(urllib.parse.urljoin(context.rbd_prober_url, 'metrics'))


@then('status code should {status_code:d}')
def check_status_code(context, status_code):
    assert context.response.status_code == status_code


@then('{metric} should be in response with value greater than {value:d}')
def check_metric_in_response(context, metric, value):
    found = False
    for family in text_string_to_metric_families(context.response.text):
        for sample in family.samples:
            if sample.name == metric:
                found = True
                assert sample.value > value
    assert found is True


@given('sleep for {seconds:d} seconds')
def sleep(context, seconds):
    time.sleep(seconds)
