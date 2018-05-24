# az-cli-extension-show-deployment
An extension for the Azure CLI to show ARM deployment progress

[![Build status](https://ci.appveyor.com/api/projects/status/k44c1ciuqrb6v34i/branch/release?svg=true)](https://ci.appveyor.com/project/stuartleeks/az-cli-extension-show-deployment/branch/release)


## Installing

### Install from the web

```bash
az extension add --source https://ci.appveyor.com/api/projects/stuartleeks/az-cli-extension-show-deployment/artifacts/dist/show_deployment-0.0.1-py2.py3-none-any.whl
```

### Download and install
The latest release can be downloaded from https://ci.appveyor.com/api/projects/stuartleeks/az-cli-extension-show-deployment/artifacts/dist/show_deployment-0.0.1-py2.py3-none-any.whl?branch=release

Then run the following (fixing the path to the downloaded file as required)

```bash
az extension add --source ~/Downloads/show_deployment-0.0.1-py2.py3-none-any.whl 
```

## Running

To show the status of the latest deployment to `your-resource-group` run:

```
az group  deployment watch  --resource-group  your-resource-group
```

You can select which deployment to watch by name:

```
az group  deployment watch  --resource-group  your-resource-group --name some-deployment
```


