import requests
import logging


logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
CAMUNDA_ENGINE_BASE_URL = 'http://localhost:8080/engine-rest'
DEFAULT_ERROR_DETAILS = "Something went wrong during execution of the external Task!"
DEFAULT_FAILURE_REASON = "Failure"


class ExternalTaskClient:
    def __init__(self, camunda_engine_base_url=CAMUNDA_ENGINE_BASE_URL):
        self.camunda_engine_base_url = camunda_engine_base_url
        self.convertor = JsonConvertor()

    #start the latest version of the specified BPMN process; no tenant specified
    def start_process_by_id(self, process_key, business_key=1, variables=[]):
        endpoint = f"{str(self.camunda_engine_base_url)}/process-definition/key/{process_key}/start"

        #handle empty variables list. Camunda returns 400 when empty variable array is given
        if variables != []:
            process_body = {
                            "businessKey": business_key,
                            "variables": self.convertor.format_variables(variables)
                        }
        else:
            process_body = {
                "businessKey": business_key
            }

        self.post_with_content(endpoint, process_body)

    #fetch and lock to an external task
    #fetch_and_locks' response contains the created external task id
    def fetch_and_lock(self, worker_id, topics,  max_tasks=1, lockduration=1000, asyncResponseTimeout=2000, variables=[]):
        endpoint = f"{str(self.camunda_engine_base_url)}/external-task/fetchAndLock"
        process_body = {
            "workerId": str(worker_id),
            "maxTasks": max_tasks,
            "asyncResponseTimeout": asyncResponseTimeout,
            "topics": self.convertor.format_topics(topics, lockduration, variables),
            }

        logging.debug(process_body)

        return self.post_with_content(endpoint, process_body)

    def complete(self, external_task_id, worker_id, variables_dict={}):
        endpoint = f"{str(self.camunda_engine_base_url)}/external-task/{external_task_id}/complete"
        complete_body = {
            "workerId": str(worker_id),
            "variables": self.convertor.format_variables(variables_dict)
        }

        self.post_with_no_content(endpoint, complete_body)

    def handle_bpmn_error(self, external_task_id, worker_id, error_code="BPMN ERROR", error_message="Something went wrong"):
        endpoint = f"{str(self.camunda_engine_base_url)}/external-task/{external_task_id}/bpmnError"
        bpmn_error_body = {
            "workerId": str(worker_id),
            "errorCode": error_code,
            "errorMessage": error_message
        }

        self.post_with_no_content(endpoint, bpmn_error_body)

    def handle_failure(self, external_task_id, worker_id, retries, retry_timeout=1000,
                        error_message=DEFAULT_FAILURE_REASON, error_details=DEFAULT_ERROR_DETAILS):

        endpoint = f"{str(self.camunda_engine_base_url)}/external-task/{external_task_id}/failure"
        failure_body = {
            "workerId": str(worker_id),
            "retries": retries,
            "retryTimeout": retry_timeout,
            "errorMessage": error_message,
            "errorDetails": error_details
        }

        self.post_with_no_content(endpoint, failure_body)

    def post_with_content(self, endpoint, body):
        logging.info("%s  SENDING...", endpoint)

        logging.debug(body)

        response = requests.post(endpoint, headers=self.get_header(), json=body)
        logging.info("Status: %d", response.status_code)

        logging.debug(response.json())

        if response.status_code == 200:
             return response
        else:
            raise response.raise_for_status()

    def post_with_no_content(self, endpoint, body):
        logging.info("%s  SENDING...", endpoint)
        response = requests.post(endpoint, headers=self.get_header(), json=body)
        logging.info("Status: %d", response.status_code)

        if response.status_code != 204:
            raise response.raise_for_status()

    def get_header(self):
        return {"Content-Type": "application/json"}



#helper class for client requests
class JsonConvertor:

    #convert the list of topics in json array
    def format_topics(self, topic_names, lockduration, variables):
        topics = []

        for topic in topic_names:
            topics.append({
                "topicName": topic,
                "lockDuration": lockduration,
                "variables": self.format_variables(variables)
            })
        return topics

    def format_variables(self, variables):
        if not self.is_empty(variables):
            return {k: {"value": v} for k, v in variables.items()}
        else:
            return list(variables)

    def is_empty(self, list):
        return True if not list else False
