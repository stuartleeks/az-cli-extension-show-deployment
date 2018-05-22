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
        - name: --deployment -n
        type: string
        short-summary: The name of the deployment to watch
"""

def watch_deployment(resourcegroupname, deploymentname):
    deployment = cli_as_json(['group', 'deployment', 'show', '-g', resourcegroupname, '-n', deploymentname])
    
    properties = deployment['properties']
    provisioning_state = properties['provisioningState']

    additional_properties = properties['additionalProperties']
    duration_string = additional_properties['duration']
    duration = duration_to_timedelta(duration_string)
    timestamp_string = properties['timestamp']
    timestamp = timestamp_to_datetime(timestamp_string)
    starttime = timestamp - duration

    print ('Deployment: {} ({}) - start {}, duration {}'.format(deploymentname, provisioning_state, starttime, duration))
    print()

    cli_operations = cli_as_json(['group', 'deployment', 'operation', 'list', '-g', resourcegroupname, '-n', deploymentname])
    operations = map(Operation, cli_operations) 
    operations = sorted(operations, key = lambda o: o.timestamp)


    headers = ['State', 'ResourceType', 'ResourceName', 'StartTime', 'Duration']
    operation_rows = map(lambda o: [o.provisioning_state, o.resource_type, o.resource_name, o.timestamp, o.duration], operations)
    operation_rows = [o for o in operation_rows]

    table = Table(headers, operation_rows)
    table.print_table()


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
# List operations
# Get child deployments
# refresh
# colour code output
# dump outputs when complete
# default to latest deployment if not specified
# allow refresh interval to be specified