import importlib 

from azure.cli.core import AzCommandsLoader

# Imported modules must implement load_command_table and load_arguments
module_names = ['watch_deployments']

modules = list(map(importlib.import_module, map(lambda m: '{}.{}'.format('azext_show-deployments', m), module_names)))

class WatchDeploymentCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        super(WatchDeploymentCommandsLoader, self).__init__(cli_ctx=cli_ctx)

    def load_command_table(self, args):
        for m in modules:
            m.load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        for m in modules:
            m.load_arguments(self, command)

COMMAND_LOADER_CLS = WatchDeploymentCommandsLoader
