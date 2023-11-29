import os
import shutil
import subprocess

import logging

logger = logging.getLogger(__name__)


def download_dependency(repository_url: str, repository_name: str, branch: str, dest_dir: str, log_dir: str) -> None:
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

    src_dir = os.path.join(dest_dir, repository_name)
    if os.path.exists(src_dir):
        shutil.rmtree(src_dir)
        logger.info(f"Removed old {repository_name} directory")

    os.makedirs(src_dir)
    logger.info(f"Created {repository_name} directory")

    log_file = os.path.join(log_dir, f"{repository_name}.log")
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


def clean_dependency(repository_name: str, src_dir: str, build_dir: str, log_dir: str) -> None:
    """Cleans up a previously downloaded and installed repository.

    Args:
        repository_name (str): The name of repository to clean up.
        src_dir (str): The directory where the source code is located.
        build_dir (str): The directory where the build files are located.
        log_dir (str): The directory where the log files are located.

    Returns:
        None
    """

    src_dir = os.path.join(src_dir, repository_name)
    build_dir = os.path.join(build_dir, repository_name)
    log_file = os.path.join(log_dir, f"{repository_name}.log")

    # Remove the build directory
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
        logger.info(f"Removed {build_dir}")

    # Remove all the files that contain 'sr' in the /dev/shm directory
    if repository_name == "sysrepo" and os.path.exists("/dev/shm"):
        logger.info(f"Removing from /dev/shm...")
        for root, dirs, files in os.walk("/dev/shm"):
            for file in files + dirs:
                if repository_name in file:
                    path = os.path.join(root, file)
                    logger.info(f"Removing {path}")
                    if os.path.isfile(path):
                        os.remove(path)
                    elif os.path.islink(path):
                        os.unlink(path)
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
