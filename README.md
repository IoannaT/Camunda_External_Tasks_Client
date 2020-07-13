# Camunda_External_Tasks_Client
External Client for External Tasks in Camunda

This Camunda project provides the basic functionality of External Client, in order to start building up your first External Workers. 

Prerequisites:
Camunda Engine should be up and running. The project utilizes a default local-hosted Camunda Engine URL. 
If you are using a remote one, you will need to modify the start_process.py variables.

An example BPMN processes is included. You can use your own BPMN workflow, but make sure to store it under directory bpmn_processes.
Start a process by running start_process.py; a Process key should be provided. 

Example worker run_unix_command_worker can be used or extended according to your needs.
