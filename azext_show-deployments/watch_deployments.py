# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
import re
import functools
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
"""

def color_for_state(state):
    if state == 'Succeeded':
        return '\033[1;30m' # bright black
    if state == 'Failed':
        return '\033[31m' # red
    if state == 'Running':
        return '\033[32m' # green
    return "\033[0m" # reset

def get_deployment_by_name(resource_group_name, deployment_name):
    cli_deployment = cli_as_json(['group', 'deployment', 'show', '-g', resource_group_name, '-n', deployment_name])
    return Deployment(cli_deployment)

def get_latest_deployment(resource_group_name):
    cli_deployments = cli_as_json(['group', 'deployment', 'list', '-g', resource_group_name])
    deployments = sorted(map(Deployment, cli_deployments) , key = lambda o: o.start_time, reverse = True)
    return deployments[0]

def watch_deployment(resource_group_name, deploymentname=None):
    if (deploymentname == None):
        deployment = get_latest_deployment(resource_group_name)
    else:
        deployment = get_deployment_by_name(resource_group_name, deploymentname)
    
    if(deployment == None):
        print ('No deployment found')
        return

    print ('Deployment: {} ({}) - start {}, duration {}'.format(deployment.name, deployment.provisioning_state, deployment.start_time, deployment.duration))
    print()

    cli_operations = cli_as_json(['group', 'deployment', 'operation', 'list', '-g', resource_group_name, '-n', deployment.name])
    operations = sorted(map(Operation, cli_operations) , key = lambda o: o.timestamp)

    headers = ['State', 'ResourceType', 'ResourceName', 'StartTime', 'Duration']
    operation_rows = map(lambda o: [o.provisioning_state, o.resource_type, o.resource_name, o.timestamp, o.duration, color_for_state(o.provisioning_state)], operations)
    operation_rows = [o for o in operation_rows]

    table = Table(headers, operation_rows, use_last_column_for_color=True)
    table.print_table()


def load_command_table(self, args):
    custom = CliCommandType(operations_tmpl='{}#{{}}'.format(__loader__.name))
    with self.command_group('group deployment', custom_command_type=custom) as g:
        g.custom_command('watch', 'watch_deployment')
    return self.command_table


def load_arguments(self, _):
    with self.argument_context('group deployment watch') as c:
        c.argument('deploymentname', options_list=['--name', '-n']) # TODO - how to add completion?
        c.argument('resource_group_name', options_list=['--resource-group', '-g']) # TODO - how to add completion?


# TODO
# List operations
# Get child deployments
# refresh
# dump outputs when complete
# allow refresh interval to be specified