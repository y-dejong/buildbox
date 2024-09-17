# Buildbox

**Buildbox** is a lightweight Python CLI tool designed to instantly containerize your development projects using Podman. By specifying a configuration file (boxfile), Buildbox automates the creation of a container, installation of dependencies, copying of project files, and execution of build commands, making it easier to manage development environments.

## Features
- **Automated Containerization**: Instantly containerizes your project based on a `boxfile` configuration.
- **Podman Integration**: Uses Podman to build and run containers.
- **Flexible Setup**: Supports custom setup scripts, dependency installations, and post-build commands.
- **File Handling**: Copies necessary files and project data into the container.

## Prerequisites
- Python 3.x
- Podman

## Installation
To install **Buildbox**, clone this repository and ensure that the script has executable permissions:
```bash
git clone <repo-url>
cd buildbox
chmod +x buildbox.py
```

Buildbox is currently built for podman containers and dnf package manager, will be adding support for Docker and apt, etc. in the future

Ensure you have Podman installed and properly configured on your system:
```bash
sudo dnf install podman
```

## Usage

### Command Overview

The Buildbox CLI provides two main commands:

1. **setup**: Creates a new containerized environment for your project using the provided `boxfile` and builds a container image.
2. **build**: Runs the build command inside the container.

### Basic Commands

- **Setup a Buildbox**:
   ```bash
   ./buildbox.py setup <project_directory> --name <buildbox_name> --boxfile <path_to_boxfile>
   ```

   Example:
   ```bash
   ./buildbox.py setup ./my_project --name my_buildbox --boxfile ./boxfile
   ```

   - `<project_directory>`: (Optional) The directory containing your project. Defaults to the current directory (`.`).
   - `--name`: (Optional) Custom name for the buildbox container.
   - `--boxfile`: (Optional) Path to a custom `boxfile`. Defaults to `./boxfile` if not provided.

- **Build in the Buildbox**:
   ```bash
   ./buildbox.py build <project_directory>
   ```

   Example:
   ```bash
   ./buildbox.py build ./my_project
   ```

   - `<project_directory>`: (Optional) The directory containing your project. Defaults to the current directory (`.`).

### Boxfile Format

A `boxfile` is used to define the environment and build instructions. Below is the structure of a `boxfile`:

```bash
# Base image to use for container
BASEIMAGE fedora:latest

# Dependencies to install
DEPENDENCIES
dnf
gcc
make

# Setup commands to run before build
SETUP
dnf update -y
dnf install -y git

# Files to copy from host to container
COPY
./source_code
./scripts/setup.sh

# Build steps
BUILD
./scripts/setup.sh
make all

# Post-build steps (currently unused)
POSTBUILD
echo "Build complete"
```

### How It Works

1. **Setup**: The `setup` command reads the `boxfile`, installs the dependencies, copies files into the container, and creates a Podman container image.
2. **Build**: The `build` command runs the build process inside the container using the instructions in the `boxfile`.

### Example Workflow

1. Create a `boxfile` in your project directory:

```bash
BASEIMAGE fedora:latest
DEPENDENCIES
gcc
make
SETUP
dnf install -y gcc make
COPY
./src
BUILD
gcc -o myapp src/main.c
```

2. Run the setup command:

```bash
./buildbox.py setup ./my_project --name myapp_box --boxfile ./my_project/boxfile
```

3. Run the build command:

```bash
./buildbox.py build ./my_project
```

This will containerize the project, install the required dependencies, and compile the application inside the container.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Contributions

Contributions are welcome! Please open a pull request or submit an issue for any bug reports or feature requests.

---

**Buildbox** simplifies the process of containerizing development projects, ensuring consistency across environments and reducing configuration overhead.