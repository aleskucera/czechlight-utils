import os
import shutil
import logging
import subprocess

logger = logging.getLogger(__name__)

CLANG_VERSION = 17


def install(repository_name: str, src_dir: str, build_dir: str, install_dir: str,
            log_dir: str, env: dict, cmake_args: list = None, num_jobs: int = 4) -> None:
    """Builds and installs a repository using CMake and Ninja.

    Args:
        repository_name (str): The name of the repository to build.
        src_dir (str): The directory where the source code is located.
        build_dir (str): The directory where the build files are located.
        install_dir (str): The directory where the installation files are located.
        log_dir (str): The directory where the log files are located.
        env (dict): The environment variables.
        cmake_args (list, optional): Additional arguments to pass to CMake.
        num_jobs (int, optional): The number of jobs to run simultaneously.

    Returns:
        None
    """

    src_dir = os.path.join(src_dir, repository_name)
    build_dir = os.path.join(build_dir, repository_name)
    log_file = os.path.join(log_dir, f"{repository_name}.log")

    if cmake_args is None:
        cmake_args = list()

    # Remove the previous build directory
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
        logger.info(f"Removed old {build_dir}")

    # Create the build directory
    os.makedirs(build_dir)
    logger.info(f"Created {build_dir}")

    try:
        with open(log_file, 'w') as f:
            logger.info(f"Building {repository_name}...")
            subprocess.run(
                ["cmake", src_dir, "-GNinja",
                 f"-DCMAKE_INSTALL_PREFIX:PATH={install_dir}",
                 f"-DCMAKE_PREFIX_PATH:PATH={install_dir}",
                 "-DCMAKE_EXPORT_COMPILE_COMMANDS=1",
              "-DBOOST_ROOT=/usr"]
              # ]
                + cmake_args,
                cwd=build_dir, env=env, check=True, stdout=f, stderr=f)
            logger.info(f"Installing {repository_name}...")
            subprocess.run(["ninja", "install", f"-j{num_jobs}"],
                           cwd=build_dir, env=env, check=True, stdout=f, stderr=f)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error occurred: {e}")
        logger.error(f"See {log_file} for more details")
        exit(1)

    logger.info(f"Finished installation of {repository_name}")


def clean(repository_name: str, src_dir: str, build_dir: str, log_dir: str) -> None:
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
    # if os.path.exists(src_dir):
    #     shutil.rmtree(src_dir)
    #     logger.info(f"Removed {src_dir}")

    # Remove the log file
    if os.path.exists(log_file):
        os.remove(log_file)
        logger.info(f"Removed {log_file}")

    logger.info(f"Finished cleaning {repository_name}")


def download_dependency(repository_url: str, repository_name: str, branch: str,
                        commit: str, dest_dir: str, log_dir: str) -> None:
    """Downloads a repository and switches to the specified branch.

    Args:
        repository_url (str): The URL of the Git repository.
        repository_name (str): The name of the repository.
        branch (str): The branch to switch to.
        commit (str): The commit to switch to.
        dest_dir (str): The directory where the repository will be downloaded.
        log_dir (str): The directory where the log files will be stored.

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

            logger.info(f"Checking out {commit}...")
            subprocess.run(["git", "checkout", commit],
                           cwd=src_dir, check=True, stdout=f, stderr=f)

    except subprocess.CalledProcessError as e:
        logger.error(f"Error occurred: {e}")
        logger.error(f"See {log_file} for more details")
        exit(1)

    logger.info(f"Finished downloading {repository_name}")


def load_env(compiler: str, sanitizer: str, install_dir: str) -> dict:
    """Loads environment variables from a file.

    Args:
        compiler (str): The compiler to use.
        sanitizer (str): The sanitizer to use.
        install_dir (str): The path to the installation directory.

    Returns:
        dict: A dictionary containing the environment variables.
    """

    env = os.environ.copy()
    env["CC"] = "gcc" if compiler == "gcc" else f"clang-{CLANG_VERSION}"
    env["CXX"] = "g++" if compiler == "gcc" else f"clang++-{CLANG_VERSION}"
    env["CMAKE_BUILD_TYPE"] = "Debug"
    env["CMAKE_EXPORT_COMPILE_COMMANDS"] = "YES"

    if sanitizer == "none":
        env["CFLAGS"] = "-g"
        env["CXXFLAGS"] = "-g"
        env["LDFLAGS"] = ""

    elif sanitizer == "tsan":
        env["CFLAGS"] = "-fsanitize=thread -g"
        env["CXXFLAGS"] = "-fsanitize=thread -g"
        env["LDFLAGS"] = "-fsanitize=thread"

    elif sanitizer == "asan":
        env["CFLAGS"] = "-fsanitize=address -fsanitize=undefined -g"
        env["CXXFLAGS"] = "-fsanitize=address -fsanitize=undefined -g"
        env["LDFLAGS"] = "-fsanitize=address -fsanitize=undefined"

    env["PATH"] = f"{install_dir}/bin:{install_dir}/share:{env['PATH']}"
    if 'LD_LIBRARY_PATH' not in env:
        env["LD_LIBRARY_PATH"] = f"{install_dir}/lib"
    else:
        env["LD_LIBRARY_PATH"] = f"{install_dir}/lib:{env['LD_LIBRARY_PATH']}"

    if 'PKG_CONFIG_PATH' not in env:
        env["PKG_CONFIG_PATH"] = f"{install_dir}/lib/pkgconfig"
    else:
        env["PKG_CONFIG_PATH"] = f"{install_dir}/lib/pkgconfig:{env['PKG_CONFIG_PATH']}"

    return env
