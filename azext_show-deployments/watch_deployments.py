# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
import re
import functools
import time
import os

from knack.help_files import helps
from azure.cli.core.commands import CliCommandType
from azure.cli.core import AzCommandsLoader
from datetime import datetime, timedelta
from .cli_utils import *
from .table_utils import *


helps['group deployment watch'] = """
    type: command
    short-summary: Watch an ARM deployment
    parameters:
      - name: --resource-group -g
        type: string
        short-summary: The name of the resource group
      - name: --name -n
        type: string
        short-summary: The name of the deployment to watch
      - name: --refresh
        type: int
        short-summary: The interval between refreshing the deployment status (in seconds)
"""

COLOR_RED = '\033[1;31m'
COLOR_BRIGHT_BLACK = '\033[1;30m'
COLOR_GREEN = '\033[1;32m'
COLOR_RESET = '\033[0m'

def color_for_state(state):
    if state == 'Succeeded':
        return COLOR_BRIGHT_BLACK
    if state == 'Failed':
        return COLOR_RED
    if state == 'Running':
        return COLOR_GREEN
    return COLOR_RESET

def get_deployment_by_name(resource_group_name, deployment_name):
    cli_deployment = cli_as_json(['deployment', 'group', 'show', '-g', resource_group_name, '-n', deployment_name])
    return Deployment(cli_deployment)

def get_latest_deployment(resource_group_name):
    # TODO - handle resource group not existing
    cli_deployments = cli_as_json(['deployment', 'group', 'list', '-g', resource_group_name])
    deployments = sorted(map(Deployment, cli_deployments) , key = lambda o: o.start_time, reverse = True)
    return deployments[0] if deployments else None

class DeploymentAndOperations:
    def __init__(self, deployment, operations):
        self.deployment = deployment
        self.operations = operations

def dump_deployment_and_operations(deployment_and_operations):
    deployment = deployment_and_operations.deployment
    operations = deployment_and_operations.operations
    print ('Deployment: {} ({}) - start {}, duration {}'.format(deployment.name, deployment.provisioning_state, deployment.start_time, deployment.duration))
    print()

    headers = ['State', 'ResourceType', 'ResourceName', 'StartTime', 'Duration']
    operation_rows = map(lambda o: [o.provisioning_state, o.resource_type, o.resource_name, o.start_time, o.duration, color_for_state(o.provisioning_state)], operations)
    operation_rows = [o for o in operation_rows]

    table = Table(headers, operation_rows, use_last_column_for_color=True)
    table.print_table()
    print(COLOR_RESET) # reset


    headers = ['ResourceName', 'ErrorCode', 'ErrorMessage']
    operations_with_errors = filter(
            lambda o: o.error != None,
            operations
        )
    error_rows = map(lambda o: [o.resource_name, o.error.code, o.error.message, COLOR_RED], operations_with_errors)
    error_rows = [o for o in error_rows]
    if len(error_rows) > 0:
        print ('Errors:')
        table = Table(headers, error_rows, use_last_column_for_color=True)
        table.print_table()
        print(COLOR_RESET) # reset

def get_operations_for_deployment(resource_group_name, deployment_name):
    cli_operations = cli_as_json(['deployment', 'operation', 'group', 'list', '-g', resource_group_name, '-n', deployment_name])
    return sorted(map(Operation, cli_operations) , key = lambda o: o.start_time)

def get_child_deployments_and_operations(resource_group_name, operations):
    # find any operations that relate to child/nested deployments
    child_deployment_names = map( 
        lambda o: o.resource_name,
        filter(
            lambda o: o.resource_type == 'Microsoft.Resources/deployments',
            operations
        )
    )
    if child_deployment_names == None:
        return []
    
    result = []
    for deployment_name in child_deployment_names:
        deployment = get_deployment_by_name(resource_group_name, deployment_name)
        child_operations = get_operations_for_deployment(resource_group_name, deployment_name)
        result += [DeploymentAndOperations(deployment, child_operations)]
        result += get_child_deployments_and_operations(resource_group_name, child_operations)
    
    return result

def watch_deployment(resource_group_name, deploymentname=None, refresh_interval=10):
    refresh_interval = int(refresh_interval)
    if (deploymentname == None):
        deployment = get_latest_deployment(resource_group_name)
    else:
        deployment = get_deployment_by_name(resource_group_name, deploymentname)
    
    if(deployment == None):
        print ('No deployment found')
        return

    deploymentname = deployment.name

    while True:
        operations = get_operations_for_deployment(resource_group_name, deployment.name)
        
        deployments_and_operations = [DeploymentAndOperations(deployment, operations)]
        deployments_and_operations += get_child_deployments_and_operations(resource_group_name, operations)

        os.system('cls' if os.name == 'nt' else 'clear')
        for deployment_and_operations in deployments_and_operations:
            dump_deployment_and_operations(deployment_and_operations)
        
        provisioning_state = deployments_and_operations[0].deployment.provisioning_state
        if provisioning_state != "Running" and provisioning_state != 'Accepted' :
            break
        time.sleep(refresh_interval)

        print()
        print('refreshing...')

        # refresh deployment and then loop round...
        deployment = get_deployment_by_name(resource_group_name, deploymentname)


    headers = ['Output name', 'Type', 'Value']
    output_rows = map(lambda o: [o.name, o.type, o.value], deployment.outputs)
    output_rows = [o for o in output_rows]
    table = Table(headers, output_rows)
    table.print_table()
    print()

def load_command_table(self, args):
    custom = CliCommandType(operations_tmpl='{}#{{}}'.format(__loader__.name))
    with self.command_group('group deployment', custom_command_type=custom) as g:
        g.custom_command('watch', 'watch_deployment')
    with self.command_group('deployment group', custom_command_type=custom) as g:
        g.custom_command('watch', 'watch_deployment')
    return self.command_table


def load_arguments(self, _):
    with self.argument_context('group deployment watch') as c:
        c.argument('deploymentname', options_list=['--name', '-n']) # TODO - how to add completion?
        c.argument('resource_group_name', options_list=['--resource-group', '-g']) # TODO - how to add completion?
        c.argument('refresh_interval', options_list=['--refresh'])

    with self.argument_context('deployment group watch') as c:
        c.argument('deploymentname', options_list=['--name', '-n']) # TODO - how to add completion?
        c.argument('resource_group_name', options_list=['--resource-group', '-g']) # TODO - how to add completion?
        c.argument('refresh_interval', options_list=['--refresh'])
