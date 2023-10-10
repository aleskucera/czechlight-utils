#!/usr/bin/env bash

SCRIPT_DIR="$(dirname $(realpath $0))"

PREFIX_DIR="/home/tomas/zdrojaky/cesnet/build/prefixes"
BUILD_DIR="/home/tomas/zdrojaky/cesnet/build/_builddirs"
SYSREPO_DIR_NAME="_sysrepo"
CESNET_DIR="${SCRIPT_DIR}/.."
DEPENDENCIES="${CESNET_DIR}/dependencies"

source "${SCRIPT_DIR}/lib/prefix.sh"
source "${SCRIPT_DIR}/lib/sr_cleanup.sh"
source "${SCRIPT_DIR}/lib/build_prefix.sh"
source "${SCRIPT_DIR}/lib/cmake.sh"
source "${SCRIPT_DIR}/lib/direnv.sh"

LOGFILE_OUT="$(mktemp)"
LOGFILE_ERR="$(mktemp)"

set -Ee


help() {
	cat << EOF >&2
Usage: czechlight.sh OPTION

Available options:
    build-stack [REGEXP]                Builds depdency stack for all configurations in its own prefixes.
                                        If REGEXP is specified then only those configurations matching the REGEXP are build.
    sr-purge                            Cleans all sysrepo state.
    cmake SOURCE [BUILD [CONFIG]]       Runs cmake with CONFIG from SOURCE directory inside BUILD directory.
                                        If BUILD is not specified then current working directory is presumed.
                                        Also writes .envrc for the direnv tool.
                                        If -c is not specified then the configuration is detected from the name of the
                                        BUILD directory (configuration is a substring of the BUILD directory name).
    build SOURCE [BUILD] [CONFIG]]      Same as above but also runs build.

Valid configurations:
    gcc-clean, gcc-tsan, gcc-asan, clang-clean, clang-tsan, clang-asan
EOF
}

# $1 ... exitcode
help_and_exit() {
	help
	exit $1
}

if [[ $# == 0 ]]; then
	help_and_exit 1
fi

OPTION="$1"
shift

case "$OPTION" in
	build-stack)
		build_all_prefixes $1
		;;
	cmake)
		set -x
		cmake_init "${1}" "${2}" "${3}"
		;;
	sr-purge)
		clean_sysrepo_state
		;;

esac
