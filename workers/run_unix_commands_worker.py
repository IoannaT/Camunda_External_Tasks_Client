from external_task_client.external_task_client import ExternalTaskClient
import uuid
import subprocess
import logging
import time

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
CAMUNDA_ENGINE_BASE_URL = 'http://localhost:8080/engine-rest'
TOPIC_NAME = ['check_file_system']
SLEEP = 5

def main():
    client = ExternalTaskClient(CAMUNDA_ENGINE_BASE_URL)
    worker_id = uuid.uuid4()

    logging.info("Worker id created and will be used: %s", str(worker_id))

    #create the external task lists by polling periodically the worker. If there are new topics to get then
    #add them to an external task list.

    response = client.fetch_and_lock(worker_id, TOPIC_NAME, 1)

    while response.json() == '[]':
        logging.info('Polling...')
        response = client.fetch_and_lock(worker_id, TOPIC_NAME, 1)

    external_task_id = response.json()[0]['id']
    lockExpirationTime = response.json()[0]['lockExpirationTime']
    logging.info('External Task with id %s locked until %s ms', external_task_id, lockExpirationTime)

    #business logic of worker starts here
    ulimit = subprocess.Popen(['ulimit', '-a'], stdout=subprocess.PIPE)
    print(ulimit.communicate()[0])
    return_code = ulimit.returncode

    if return_code != 0:
        client.handle_bpmn_error(external_task_id, str(worker_id), "Failure", "FS not available")
        rc0 = False
    else:
        rc0 = True

    complete_variables = {'rc0': rc0}
    client.complete(external_task_id, worker_id, complete_variables)


if __name__ == "__main__":
    main()