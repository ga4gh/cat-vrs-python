# Cat-VRS Python Getting Started Notebook Series

This series of notebooks is intended to be the fastest way to becoming productive with
the [cat-vrs-python](https://github.com/ga4gh/cat-vrs-python) package. The intent of
each notebook in this series is to be an interactive introduction to functionally
contained in the `cat-vrs-python` package.

A beginning developer level of familiarity with python, jupyter notebooks is assumed in
order to run this notebook series. You should be familiar with installing packages and
running commands in your execution environment.

## Development Environment Setup

We provide you two options for setting up your development environment: using a Python
[virtual environment](#virtual-environment) or leveraging
[VS Code Dev Containers](#dev-containers) (useful for non-macOS users).

### Fork the Repo

Fork the repo at <https://github.com/ga4gh/cat-vrs-python/fork/> and initialize a
development environment.

```shell
git clone --recurse-submodules git@github.com:YOUR_GITHUB_ID/cat-vrs-python.git
cd cat-vrs-python
```

### Virtual Environment

You must first install python@3.12, if not already installed.

Next, run the following:

```shell
make nbready
source venv/3.12/bin/activate
```

#### Virtual Environment: Selecting the Kernel

When opening a notebook with this option, click `Select Kernel`,
`Python Environments...`, and select the first option:
`3.12 (Python 3.12.z) venv/3.12/bin/python`

_Note: Patch version may vary._

### Dev Containers

#### Prerequisites

For your convenience, this section is copied from the
[VS Code Dev Containers Tutorial](https://code.visualstudio.com/docs/devcontainers/tutorial#_prerequisites).

* [Install VS Code](https://code.visualstudio.com/download)

  You must be using VS Code to use the Dev Containers.

  **⚠ Note:** Dev Containers will still work with [Podman](https://podman.io/). You will
  need to configure your VS Code settings.

  Open User Settings in VS Code (`View` > `Command Palette` > `"Preferences: Open User Settings (JSON)"`) and add the following:

  ```json
  ... // your configs
  "dev.containers.dockerPath": "podman"
  ```

* [Install Docker](https://docs.docker.com/get-started/get-docker/)

  Docker is needed to create and manage your containers.

  * Docker Desktop

    Download and install
    [Docker Desktop](https://www.docker.com/products/docker-desktop/), or an
    [alternative Docker option](https://code.visualstudio.com/remote/advancedcontainers/docker-options),
    like Docker on a remote host or Docker compliant CLI.

  * Start Docker

    Run the Docker Desktop application to start Docker. You will know it's running if
    you look in the activity tray and see the Docker whale icon.

    Docker might take a few minutes to start. If the whale icon is animated, it is
    probably still in the process of starting. You can click on the icon to see the
    status.

  * Check Docker

    Once Docker is running, you can confirm that everything is working by opening a new
    terminal window and typing the command:

    ```shell
    docker --version
    ```

* [Install Dev Containers extension](vscode:extension/ms-vscode-remote.remote-containers)

  The Dev Containers extension lets you run Visual Studio Code inside a Docker container.

  [Marketplace Link](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) (if viewing from browser)

#### Creating the Dev Container

Open the VS Code Command Palette: Shift + Command + P (Mac) / Ctrl + Shift + P (Windows/Linux)

Type and select the following inside the Command Palette: `> Dev Containers: Rebuild and Reopen in Container`

The Dev Container will be created and install the dependencies needed.

You should see `Dev Container: Cat-VRS Python Notebooks @ desktop-linux` on the bottom left hand corner of VS Code.

#### Dev Containers: Selecting the Kernel

When opening a notebook with this option, click `Select Kernel`,
`Python Environments...`, and select the first option:
`Python 3.12.z /usr/local/bin/python`

_Note: Patch version may vary._
