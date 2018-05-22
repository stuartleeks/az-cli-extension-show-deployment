# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
import re
from knack.help_files import helps
from azure.cli.core.commands import CliCommandType
from azure.cli.core import AzCommandsLoader
from datetime import datetime, timedelta
from .cli_utils import run_cli_command, prepare_cli_command


helps['group deployment watch'] = """
    type: command
    short-summary: Watch an ARM deployment
    parameters:
        - name: --resource-group -g
        type: string
        short-summary: The name of the resource group
        - name: --deployment -n
        type: string
        short-summary: The name of the deployment to watch
"""

def cli_as_json(cmd):
    cli_cmd = prepare_cli_command(cmd)
    return run_cli_command(cli_cmd, return_as_json=True)


def duration_to_timedelta(duration):
    match = re.match(r'^PT(?P<seconds>\d*.\d*)S$', duration)
    if match:
        seconds = float(match['seconds'])
        return timedelta(seconds = seconds)

    match = re.match(r'^PT(?P<minutes>\d*)M(?P<seconds>\d*.\d*)S$', duration)
    if match:
        minutes = int(match['minutes'])
        seconds = float(match['seconds'])
        return timedelta(minutes = minutes, seconds = seconds)
    
    match = re.match(r'^PT(?P<hours>\d*)H(?P<minutes>\d*)M(?P<seconds>\d*.\d*)S$', duration)
    if match:
        hours = int(match['hours'])
        minutes = int(match['minutes'])
        seconds = float(match['seconds'])
        return timedelta(hours = hours, minutes = minutes, seconds = seconds)
    
    raise ValueError('Unhandled duration format: {}'.format(duration))

def timestamp_to_datetime(timestamp):
    return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f+00:00') # formatting from https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior
    

def watch_deployment(resourcegroupname, deploymentname):
    deployment = cli_as_json(['group', 'deployment', 'show', '-g', resourcegroupname, '-n', deploymentname])
    
    properties = deployment['properties']
    provisioning_state = properties['provisioningState']

    additional_properties = properties['additionalProperties']
    duration_string = additional_properties['duration']
    duration = duration_to_timedelta(duration_string)
    timestamp_string = properties['timestamp']
    timestamp = timestamp_to_datetime(timestamp_string)

    print ('Deployment: {} ({}) - start {}, duration {}'.format(deploymentname, provisioning_state, timestamp, duration))

    operations= cli_as_json(['group', 'deployment', 'operation', 'list', '-g', resourcegroupname, '-n', deploymentname])
    for operation in operations:
        operation_id = operation['operationId']
        operation_properties = operation['properties']
        operation_provisioning_state = operation_properties['provisioningState'];
        operation_timestamp_string = operation_properties['timestamp']
        operation_timestamp = timestamp_to_datetime(operation_timestamp_string)
        operation_target_resource = operation_properties['targetResource']
        if operation_target_resource != None:
            operation_resource_type = operation_target_resource['resourceType']
            operation_resource_name = operation_target_resource['resourceName']
        else:
            operation_resource_type = None
            operation_resource_name = None

        operation_additional_properties = operation_properties['additionalProperties']
        operation_duration_string = operation_additional_properties['duration']
        operation_duration = duration_to_timedelta(operation_duration_string)
        
        print('Operation: {}, {}, {}, {}, {}, {}'.format(operation_id, operation_provisioning_state, operation_resource_type, operation_resource_name, operation_timestamp, operation_duration))


def load_command_table(self, args):
    custom = CliCommandType(operations_tmpl='{}#{{}}'.format(__loader__.name))
    with self.command_group('group deployment', custom_command_type=custom) as g:
        g.custom_command('watch', 'watch_deployment')
    return self.command_table


def load_arguments(self, _):
    with self.argument_context('group deployment watch') as c:
        c.argument('deploymentname', options_list=['--name', '-n']) # TODO - how to add completion?
        c.argument('resourcegroupname', options_list=['--resource-group', '-g']) # TODO - how to add completion?


# TODO
# Get operations
# List operations
# Get child deployments
# refresh
# ensure sorting operations to reduce jumping when refreshing
# colour code output
# dump outputs when complete
# default to latest deployment if not specified
# allow refresh interval to be specified