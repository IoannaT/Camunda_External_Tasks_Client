from external_task_client.external_task_client import ExternalTaskClient

def main():

    BASE_URL = 'http://localhost:8080/engine-rest'
    client = ExternalTaskClient(BASE_URL)

    process_id = input('Enter the Process id you want to start: ')
    client.start_process_by_id(process_id)

if __name__ == '__main__':
    main()