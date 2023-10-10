import os
import yaml
import shutil
import argparse
import subprocess
import logging.config

CZECHLIGHT_DIR = "/home/ales/cesnet/czechlight/"

LOG_DIR = os.path.join(CZECHLIGHT_DIR, "logs")
SRC_DIR = os.path.join(CZECHLIGHT_DIR, "source")
BUILD_DIR = os.path.join(CZECHLIGHT_DIR, "build")
INSTALL_DIR = os.path.join(CZECHLIGHT_DIR, "install")

# Create the required directories
required_dirs = [SRC_DIR, BUILD_DIR, INSTALL_DIR, LOG_DIR]
for directory in required_dirs:
    if not os.path.exists(directory):
        os.makedirs(directory)

with open("config/logging.yaml", 'r') as f:
    config = yaml.safe_load(f.read())
    config["handlers"]["fileHandler"]["filename"] = os.path.join(LOG_DIR, "main.log")

logging.config.dictConfig(config)
logger = logging.getLogger(__name__)


def download(repository_url: str, repository_name: str, branch: str, ) -> None:
    """Downloads a repository and switches to the specified branch.

    Args:
        repository_url (str): The URL of the Git repository.
        repository_name (str): The name of the repository.
        branch (str): The branch to switch to.

    Returns:
        None
    """

    logger.info(f"Downloading {repository_name}: "
                f"\n\turl: {repository_url}"
                f"\n\tbranch: {branch}")

    src_dir = os.path.join(SRC_DIR, repository_name)
    if os.path.exists(src_dir):
        shutil.rmtree(src_dir)
        logger.info(f"Removed old {repository_name} directory")

    os.makedirs(src_dir)
    logger.info(f"Created {repository_name} directory")

    log_file = os.path.join(LOG_DIR, f"{repository_name}.log")
    try:
        with open(log_file, 'w') as f:
            logger.info(f"Downloading {repository_name}...")
            subprocess.run(["git", "clone", repository_url, "."],
                           cwd=src_dir, check=True, stdout=f, stderr=f)

            logger.info(f"Checking out {branch}...")
            subprocess.run(["git", "checkout", branch],
                           cwd=src_dir, check=True, stdout=f, stderr=f)

    except subprocess.CalledProcessError as e:
        logger.error(f"Error occurred: {e}")
        logger.error(f"See {log_file} for more details")
        exit(1)

    logger.info(f"Finished downloading {repository_name}")


def clean(repository_name: str) -> None:
    """Cleans up a previously downloaded and installed repository.

    Args:
        repository_name (str): The name of repository to clean up.

    Returns:
        None
    """

    install_dir = INSTALL_DIR
    src_dir = os.path.join(SRC_DIR, repository_name)
    build_dir = os.path.join(BUILD_DIR, repository_name)
    log_file = os.path.join(LOG_DIR, f"{repository_name}.log")

    # Remove the build directory
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
        logger.info(f"Removed {build_dir}")

    # Remove all files that were created by the installation
    if os.path.exists(install_dir):
        logger.info(f"Removing {repository_name} from {install_dir}")
        for root, dirs, files in os.walk(install_dir):
            for file in files + dirs:
                if file.startswith(repository_name):
                    logger.info(f"Removing {os.path.join(root, file)}")
                    path = os.path.join(root, file)
                    if os.path.isfile(path):
                        os.remove(path)
                    elif os.path.isdir(path):
                        shutil.rmtree(path)

    # Remove the source directory
    if os.path.exists(src_dir):
        shutil.rmtree(src_dir)
        logger.info(f"Removed {src_dir}")

    # Remove the log file
    if os.path.exists(log_file):
        os.remove(log_file)
        logger.info(f"Removed {log_file}")

    logger.info(f"Finished cleaning {repository_name}")


def build_and_install(repository_name: str, additional_args: list = None) -> None:
    """Builds and installs a repository using CMake and Ninja.

    Args:
        repository_name (str): The name of the repository to build.
        additional_args (list, optional): Additional arguments to pass to CMake.

    Returns:
        None
    """

    install_dir = INSTALL_DIR
    src_dir = os.path.join(SRC_DIR, repository_name)
    build_dir = os.path.join(BUILD_DIR, repository_name)
    log_file = os.path.join(LOG_DIR, f"{repository_name}.log")

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
            logger.info(f"Building {repository_name}...")
            subprocess.run(["cmake", src_dir, "-GNinja",
                            f"-DCMAKE_INSTALL_PREFIX:PATH={install_dir}",
                            f"-DCMAKE_PREFIX_PATH:PATH={install_dir}"]
                           + additional_args,
                           cwd=build_dir, env=env, check=True, stdout=f, stderr=f)
            logger.info(f"Installing {repository_name}...")
            subprocess.run(["ninja", "install"],
                           cwd=build_dir, env=env, check=True, stdout=f, stderr=f)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error occurred: {e}")
        logger.error(f"See {log_file} for more details")
        exit(1)

    logger.info(f"Finished installation of {repository_name}")


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Utility for downloading and building dependencies")
    arg_parser.add_argument("-a", "--action", type=str, choices=["download", "install", "clean"],
                            help="Action to perform")
    arg_parser.add_argument("--all", action="store_true", help="Perform the action on all dependencies")
    arg_parser.add_argument("--repository", type=str, help="Perform the action on the specified repository")
    args = arg_parser.parse_args()

    # Load the dependencies
    with open("config/repositories.yaml", 'r') as f:
        dependencies = yaml.safe_load(f.read())

    # Perform the specified action
    if args.action == "download":
        if args.all:
            for name, data in dependencies.items():
                download(data["url"], name, data["branch"])
        elif args.dependency:
            download(dependencies[args.dependency]["url"],
                     args.dependency,
                     dependencies[args.dependency]["branch"])
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
                clean(name)
        elif args.dependency:
            clean(args.dependency)
        else:
            arg_parser.error("Either --all or --dependency must be specified")
