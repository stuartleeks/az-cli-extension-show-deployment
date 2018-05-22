# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
 
from knack.help_files import helps

from azure.cli.core import AzCommandsLoader

helps['group deployment watch'] = """
    type: command
    short-summary: Say hello world.
"""

def watchDeployment():
    print('Hello World!!')


class WatchDeploymentCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        custom_type = CliCommandType(operations_tmpl='azext_show-deployments#{}')
        super(WatchDeploymentCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                       custom_command_type=custom_type)

    def load_command_table(self, args):
        with self.command_group('group deployment') as g:
            g.custom_command('watch', 'watchDeployment')
        return self.command_table

    def load_arguments(self, _):
        pass

COMMAND_LOADER_CLS = WatchDeploymentCommandsLoader
