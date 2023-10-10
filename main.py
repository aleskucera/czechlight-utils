import os
import shutil
import argparse
import subprocess
import logging.config

import yaml

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CZECHLIGHT_DIR = "/home/ales/cesnet/czechlight/"

LOG_DIR = os.path.join(CZECHLIGHT_DIR, "logs")
BUILDS_DIR = os.path.join(CZECHLIGHT_DIR, "builds")
INSTALL_DIR = os.path.join(CZECHLIGHT_DIR, "install")
DEPENDENCIES_DIR = os.path.join(CZECHLIGHT_DIR, "dependencies")

with open("config/logging.yaml", 'r') as f:
    config = yaml.safe_load(f.read())
    config["handlers"]["fileHandler"]["filename"] = os.path.join(LOG_DIR, "main.log")

logging.config.dictConfig(config)
logger = logging.getLogger(__name__)


def download_dependency(url: str, branch: str, name: str):
    logger.info(f"Downloading {name}: "
                f"\n\turl: {url}"
                f"\n\tbranch: {branch}")

    # Create the build directory
    dependency_dir = os.path.join(DEPENDENCIES_DIR, name)
    if os.path.exists(dependency_dir):
        shutil.rmtree(dependency_dir)
        logger.info(f"Removed old {name} directory")

    os.makedirs(dependency_dir)
    logger.info(f"Created {name} directory")

    # Download the repository
    try:
        log_file = os.path.join(LOG_DIR, f"{name}.log")
        with open(log_file, 'w') as f:
            logger.info(f"Downloading {name}...")
            subprocess.run(["git", "clone", url, "."],
                           cwd=dependency_dir, check=True, stdout=f, stderr=f)

            logger.info(f"Checking out {branch}...")
            subprocess.run(["git", "checkout", branch],
                           cwd=dependency_dir, check=True, stdout=f, stderr=f)

    except subprocess.CalledProcessError as e:
        logger.error(f"Error occurred: {e}")
        logger.error(f"See {log_file} for more details")
        exit(1)

    logger.info(f"Finished downloading {name}")


def clean_dependency(name: str):
    build_dir = os.path.join(BUILDS_DIR, name)
    install_dir = INSTALL_DIR
    src_dir = os.path.join(DEPENDENCIES_DIR, name)
    log_file = os.path.join(LOG_DIR, f"{name}.log")

    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
        logger.info(f"Removed {build_dir}")

    if os.path.exists(install_dir):
        logger.info(f"Removing {name} from {install_dir}")
        for root, dirs, files in os.walk(install_dir):
            for file in files + dirs:
                if file.startswith(name):
                    logger.info(f"Removing {os.path.join(root, file)}")
                    path = os.path.join(root, file)
                    if os.path.isfile(path):
                        os.remove(path)
                    elif os.path.isdir(path):
                        shutil.rmtree(path)

    if os.path.exists(src_dir):
        shutil.rmtree(src_dir)
        logger.info(f"Removed {src_dir}")

    if os.path.exists(log_file):
        os.remove(log_file)
        logger.info(f"Removed {log_file}")

    logger.info(f"Finished cleaning {name}")


def build_and_install(name: str, additional_args: list = None):
    build_dir = os.path.join(BUILDS_DIR, name)
    install_dir = INSTALL_DIR
    dependency_dir = os.path.join(DEPENDENCIES_DIR, name)
    log_file = os.path.join(LOG_DIR, f"{name}.log")

    if additional_args is None:
        additional_args = list()

    # Set the build variables
    env = os.environ.copy()
    env["CC"] = "gcc"
    env["CXX"] = "g++"
    env["CMAKE_BUILD_TYPE"] = "Debug"
    env["CMAKE_EXPORT_COMPILE_COMMANDS"] = "YES"

    # Set the installation variables
    env["PATH"] = f"{install_dir}/bin:{env['PATH']}"
    if 'LD_LIBRARY_PATH' not in env:
        env["LD_LIBRARY_PATH"] = f"{install_dir}/lib"
    else:
        env["LD_LIBRARY_PATH"] = f"{install_dir}/lib:{env['LD_LIBRARY_PATH']}"

    if 'PKG_CONFIG_PATH' not in env:
        env["PKG_CONFIG_PATH"] = f"{install_dir}/lib/pkgconfig"
    else:
        env["PKG_CONFIG_PATH"] = f"{install_dir}/lib/pkgconfig:{env['PKG_CONFIG_PATH']}"

    # Create the build directory
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
        logger.info(f"Removed old {build_dir}")
    os.makedirs(build_dir)
    logger.info(f"Created {build_dir}")

    try:
        with open(log_file, 'w') as f:
            logger.info(f"Building {name}...")
            subprocess.run(["cmake", dependency_dir, "-GNinja",
                            f"-DCMAKE_INSTALL_PREFIX:PATH={install_dir}",
                            f"-DCMAKE_PREFIX_PATH:PATH={install_dir}"]
                           + additional_args,
                           cwd=build_dir, env=env, check=True, stdout=f, stderr=f)
            logger.info(f"Installing {name}...")
            subprocess.run(["ninja", "install"],
                           cwd=build_dir, env=env, check=True, stdout=f, stderr=f)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error occurred: {e}")
        exit(1)

    logger.info(f"Finished installation of {name}")


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Utility for downloading and building dependencies")
    arg_parser.add_argument("-a", "--action", type=str, choices=["download", "install", "clean"],
                            help="Action to perform")
    arg_parser.add_argument("--all", action="store_true", help="Perform the action on all dependencies")
    arg_parser.add_argument("--repository", type=str, help="Perform the action on the specified repository")
    args = arg_parser.parse_args()

    with open("config/dependencies.yaml", 'r') as f:
        dependencies = yaml.safe_load(f.read())

    if args.action == "download":
        if args.all:
            for name, data in dependencies.items():
                download_dependency(data["url"], data["branch"], name)
        elif args.dependency:
            download_dependency(dependencies[args.dependency]["url"],
                                dependencies[args.dependency]["branch"],
                                args.dependency)
        else:
            arg_parser.error("Either --all or --dependency must be specified")

    if args.action == "install":
        if args.all:
            for name, data in dependencies.items():
                build_and_install(name, data["build_args"])
        elif args.dependency:
            build_and_install(args.dependency, dependencies[args.dependency]["build_args"])
        else:
            arg_parser.error("Either --all or --dependency must be specified")

    if args.action == "clean":
        if args.all:
            for name, data in dependencies.items():
                clean_dependency(name)
        elif args.dependency:
            clean_dependency(args.dependency)
        else:
            arg_parser.error("Either --all or --dependency must be specified")
