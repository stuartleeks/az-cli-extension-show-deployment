# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
from knack.help_files import helps
from azure.cli.core.commands import CliCommandType
from azure.cli.core import AzCommandsLoader
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

def watch_deployment(resourcegroupname, deploymentname): #resource_group_name, deployment_name):
    cli_cmd = prepare_cli_command(['group', 'deployment', 'show', '-g', resourcegroupname, '-n', deploymentname])
    deploymentjson = run_cli_command(cli_cmd)
    deployment = json.loads(deploymentjson)
    return deployment['id']


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
# Check deployment status
# Write deployment name, status, duration (if running!)
# Get operations
# List operations
# Get child deployments
# refresh
# colour code output
# dump outputs when complete
# default to latest deployment if not specified
# allow refresh interval to be specified