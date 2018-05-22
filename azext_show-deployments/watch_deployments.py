# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
 
from knack.help_files import helps

from azure.cli.core.commands import CliCommandType
from azure.cli.core import AzCommandsLoader

helps['group deployment watch'] = """
    type: command
    short-summary: Say hello world.
"""

def watch_deployment(resourcegroupname, deploymentname): #resource_group_name, deployment_name):
    print('Hello World!!')
    print(resourcegroupname)
    print(deploymentname)
    print('TODO - implement!')


def load_command_table(self, args):
    custom = CliCommandType(operations_tmpl='{}#{{}}'.format(__loader__.name))
    with self.command_group('group deployment', custom_command_type=custom) as g:
        g.custom_command('watch', 'watch_deployment')
    return self.command_table

def load_arguments(self, _):
    with self.argument_context('group deployment watch') as c:
        c.argument('deploymentname', options_list=['--name', '-n']) # TODO - how to add completion?
        c.argument('resourcegroupname', options_list=['--resource-group', '-g']) # TODO - how to add completion?


