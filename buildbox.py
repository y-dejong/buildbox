import argparse
import os
import subprocess
import tempfile

def parse_cli_args():
    parser = argparse.ArgumentParser(description="Buildbox, instantly containerize your development projects")
    parser.add_argument("--name", type=str, help="Name of the buildbox")
    parser.add_argument("--boxfile", type=str, help="Name of boxfile when creating a new buildbox (default ./boxfile)")
    parser.add_argument("command", help="buildbox command", nargs=1)
    parser.add_argument("positional", help="Directory or dependencies, based on command", nargs="*")

    args = parser.parse_args()
    return args

def parse_boxfile(filename):
    box_data = {
        "setup": [],
        "prebuild": [],
        "build": [],
        "run": [],
        "dependencies": []
    }
    current_list_name = None

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                pass
            elif line.startswith(("SETUP", "PREBUILD", "BUILD", "RUN", "DEPENDENCIES")):
                current_list_name = line.split()[0].lower()
            elif line.startswith(("BASEIMAGE ", "NAME ")):
                params = line.split(maxsplit=1)
                box_data[params[0].lower()] = params[1]

            elif current_list_name is not None:
                box_data[current_list_name].append(line)

    print(box_data)
    return box_data

def create_podman_image(config, buildscript, runscript):
    dockerfile_contents = f"""FROM {config["baseimage"] if "baseimage" in config else "fedora:latest"}

# Install dependencies
{"RUN dnf install -y " + " ".join(config["dependencies"]) if len(config["dependencies"]) > 0 else ""}

# Additional commands from buildbox
{"\n".join(f"RUN {command}" for command in config["setup"])}

# Copy scripts
{f"COPY {buildscript} /root/build.sh" if buildscript else ""}
{f"COPY {runscript} /root/run.sh" if runscript else ""}

# Set working directory
WORKDIR /root/workspace
"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as script:
        script.write(dockerfile_contents)
        scriptname = script.name

    print("Generated dockerfile: " + scriptname)

    if "name" in config:
        image_name = "bb_" + config["name"]
    else:
        image_name = "bb_" + os.path.basename(config["project_dir"]) # TODO: Get last part of path

    try:
        configdir = os.path.expanduser("~/.config/buildbox")
        os.makedirs(configdir, exist_ok=True)
        subprocess.run(["podman", "build", "-t", image_name, "-f", scriptname, "--output", os.path.join(configdir, config["name"]), config["project_dir"]], check=True)
        # TODO add csv entry
        print("Created image")
    except subprocess.CalledProcessError as e:
        print(f"Error building image: {e}")

def main():
    args = vars(parse_cli_args())

    print(args["command"])
    if args["command"][0] == "create":

        if len(args["positional"]) > 0 and os.path.isdir(args["positional"][0]):
            project_dir = args["positional"][0]
            args["dependencies"] = args["positional"][1:]
        else:
            project_dir = "."
            args["dependencies"] = args["positional"]

        if args["boxfile"]:
            if os.path.isfile(args["boxfile"]):
                config = parse_boxfile(args["boxfile"])
            else:
                print(f"Boxfile not found: {args['boxfile']}")
                return
        elif os.path.isfile(os.path.join(project_dir, "boxfile")):
            config = parse_boxfile(os.path.join(project_dir, "boxfile"))
        else:
            print("No boxfile found, using default")
            config = {
                "setup": [],
                "prebuild": [],
                "build": [],
                "run": [],
                "dependencies": []
            }
        # TODO set defaults like name, base image

        if args["name"]:
            print("Name given in cli args")
            config["name"] = args["name"]
        if "name" not in config:
            print("Getting name from project dir")
            config["name"] = os.path.basename(os.path.abspath(project_dir))
        config["project_dir"] = project_dir

        config["dependencies"] += args["dependencies"]

        if len(config["build"]) > 0:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as script:
                script.writelines(f"{line}\n" for line in config["build"])
                buildscript_name = script.name
        else:
            buildscript_name = None

        if len(config["run"]) > 0:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as script:
                script.writelines(f"{line}\n" for line in config["run"])
                runscript_name = script.name
        else:
            runscript_name = None

        create_podman_image(config, buildscript_name, runscript_name)

    if args["command"][0] == "build":
        count = 0
        while subprocess.run(["podman", "container", "exists", "bb_" + args["positional"][0] + str(count)]) == 1:
            count += 1

        subprocess.run(["podman", "run", "--rm", "-i", f"bb_{args['positional'][0]}", f"-v{'.'}:{'/root/workspace'}:z",
                        "source", "/root/build.sh"])

if __name__ == "__main__":
    main()
