#!/usr/bin/env python3

import os
import yaml
import shutil
import argparse
import logging.config

from src.utils import install, clean, load_env, download_dependency

CZECHLIGHT_DIR = "/home/ales/cesnet/czechlight/"
CLANG_VERSION = 17


def main():
    # ------------------------------------------------
    # ================ BASIC CONFIG ==================
    # ------------------------------------------------

    root_dir = os.path.dirname(os.path.realpath(__file__))
    logging_config = os.path.join(root_dir, "config", "logging.yaml")
    dependency_config = os.path.join(root_dir, "config", "dependencies.yaml")
    netconf_cli_config = os.path.join(root_dir, "config", "netconf-cli.yaml")

    # Load the dependency configuration
    with open(dependency_config, 'r') as f:
        dependencies = yaml.safe_load(f.read())
    dependency_names = list(dependencies.keys())

    # Load the netconf-cli configuration
    with open(netconf_cli_config, 'r') as f:
        netconf_cli = yaml.safe_load(f.read())

    # ------------------------------------------------
    # ================ ARGUMENT PARSING ==============
    # ------------------------------------------------

    arg_parser = argparse.ArgumentParser(description="Utility for downloading and building dependencies")
    arg_parser.add_argument("-a", "--action", type=str, choices=["install", "clean"],
                            help="Action to perform")
    arg_parser.add_argument("-t", "--target", type=str,
                            choices=["all", "dependencies", "netconf-cli"] + dependency_names,
                            help="The target to perform the action on")
    arg_parser.add_argument("-c", "--compiler", type=str, choices=["gcc", "clang"], default="gcc",
                            help="The compiler to use")
    arg_parser.add_argument("-s", "--sanitizer", type=str, choices=["none", "address", "thread", "undefined"],
                            default="none", help="The sanitizer to use")
    arg_parser.add_argument("-j", "--jobs", type=int, default=1, help="The number of jobs to use")
    args = arg_parser.parse_args()

    # ------------------------------------------------
    # ================ DIRECTORY SETUP ===============
    # ------------------------------------------------

    compiler = args.compiler
    sanitizer = "clean" if args.sanitizer == "none" else args.sanitizer
    build_options = f"{compiler}-{sanitizer}"

    log_dir = os.path.join(CZECHLIGHT_DIR, "logs")
    dependency_dir = os.path.join(CZECHLIGHT_DIR, "dependencies")
    build_dir = os.path.join(CZECHLIGHT_DIR, "build", build_options)
    install_dir = os.path.join(CZECHLIGHT_DIR, "install", build_options)

    # Create the required directories
    required_dirs = [log_dir, dependency_dir, build_dir, install_dir]
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)

    # ------------------------------------------------
    # ================ LOGGING CONFIG ================
    # ------------------------------------------------

    with open(logging_config, 'r') as f:
        config = yaml.safe_load(f.read())
        config["handlers"]["fileHandler"]["filename"] = os.path.join(log_dir, "main.log")

    logging.config.dictConfig(config)
    logger = logging.getLogger(__name__)

    # ------------------------------------------------
    # ================ ENVIRONMENT ===================
    # ------------------------------------------------

    env = load_env(args.compiler, args.sanitizer, install_dir)

    # ------------------------------------------------
    # ================ MAIN LOGIC ====================
    # ------------------------------------------------

    # # Perform the specified action
    # if args.action == "download":
    #     if args.target == "all":
    #         for name, data in dependencies.items():
    #             download_dependency(data["url"], name, data["branch"], dependency_dir, log_dir)
    #     elif args.target == "dependencies":
    #         for name, data in dependencies.items():
    #             download_dependency(data["url"], name, data["branch"], src_dir, log_dir)
    #     elif args.target in dependency_names:
    #         download_dependency(dependencies[args.target]["url"],
    #                             args.target,
    #                             dependencies[args.target]["branch"],
    #                             src_dir, log_dir)
    #     else:
    #         arg_parser.error("Download action can be performed only on dependencies.")

    if args.action == "clean":
        if args.target == "all":
            for name, data in dependencies.items():
                clean(name, dependency_dir, build_dir, log_dir)
            clean("netconf-cli", CZECHLIGHT_DIR, build_dir, log_dir)

            # Remove the contents of the installation directory
            if os.path.exists(install_dir):
                logger.info(f"Removing from {install_dir}...")
                shutil.rmtree(install_dir)
                os.makedirs(install_dir)
        elif args.target == "dependencies":
            for name, data in dependencies.items():
                clean(name, dependency_dir, build_dir, log_dir)
        elif args.target in dependency_names:
            clean(args.target, dependency_dir, build_dir, log_dir)
        elif args.target == "netconf-cli":
            clean("netconf-cli", CZECHLIGHT_DIR, build_dir, log_dir)
        else:
            arg_parser.error("Invalid clean target.")

    elif args.action == "install":
        if args.target == "all":
            for name, data in dependencies.items():
                install(name, dependency_dir, build_dir, install_dir, log_dir, env, data["build_args"], args.jobs)
            install("netconf-cli", CZECHLIGHT_DIR, build_dir, install_dir, log_dir, env, netconf_cli["build_args"],
                    args.jobs)
        elif args.target == "dependencies":
            for name, data in dependencies.items():
                install(name, dependency_dir, build_dir, install_dir, log_dir, env, data["build_args"], args.jobs)
        elif args.target in dependency_names:
            install(args.target, dependency_dir, build_dir, install_dir, log_dir, env,
                    dependencies[args.target]["build_args"],
                    args.jobs)
        elif args.target == "netconf-cli":
            install("netconf-cli", CZECHLIGHT_DIR, build_dir, install_dir, log_dir, env, netconf_cli["build_args"],
                    args.jobs)
        else:
            arg_parser.error("Invalid build target.")


if __name__ == "__main__":
    main()
