Feature: Test prometheus

    Scenario: Send get on /metrics
        Given send GET request
          Then status code should 200
    
    Scenario: Check metrics avaiability
        Given sleep for 5 seconds
        And send GET request
          Then rbd_prober_bandwidth_total should be in response with value greater than 0
          And rbd_prober_ops_total should be in response with value greater than 0
          And rbd_prober_response_time_bucket should be in response with value greater than -1
          And rbd_prober_response_time_sum should be in response with value greater than 0
          And rbd_prober_response_time_count should be in response with value greater than 0
