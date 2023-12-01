#!/bin/bash

CZECHLIGHT_DIR="/home/ales/cesnet/czechlight"
PYTHON_VENV_FILE="/home/ales/cesnet/czechlight-utils/venv/bin/activate"
source "$PYTHON_VENV_FILE"

compiler="gcc"
sanitizer="none"

while getopts "c:s:" opt; do
	case $opt in
	c)
		compiler="$OPTARG"
		;;
	s)
		sanitizer="$OPTARG"
		;;
	\?)
		echo "Invalid option: -$OPTARG" >&2
		exit 1
		;;
	esac
done

build_options="${compiler}-$(if [ "$sanitizer" == "none" ]; then echo "clean"; else echo "$sanitizer"; fi)"

# Set the PATH and LD_LIBRARY_PATH environment variables based on the provided compiler and sanitizer
export PATH="$CZECHLIGHT_DIR/install/$build_options/bin:$CZECHLIGHT_DIR/install/$build_options/sbin:$PATH"
export LD_LIBRARY_PATH="$CZECHLIGHT_DIR/install/$build_options/lib:$LD_LIBRARY_PATH"

# Change the prompt to indicate the environment variables are set
PS1="[czechlight-${compiler}] \[\e[1;32m\]\u@\h \[\e[1;34m\]\w \[\e[0m\]$ "

run-netopeer2-server() {
	sock_file="$CZECHLIGHT_DIR/install/$build_options/run/netopeer2-server.sock"
	pid_file="$CZECHLIGHT_DIR/install/$build_options/run/netopeer2-server.pid"

	# Ensure the directory structure exists for the sock file
	sock_dir=$(dirname "$sock_file")
	if [ ! -d "$sock_dir" ]; then
		mkdir -p "$sock_dir"
		echo "Sock directory created: $sock_dir"
	fi

	# Ensure the directory structure exists for the pid file
	pid_dir=$(dirname "$pid_file")
	if [ ! -d "$pid_dir" ]; then
		mkdir -p "$pid_dir"
		echo "PID directory created: $pid_dir"
	fi

	# Check if the sock_file exists
	if [ -e "$sock_file" ]; then
		echo "Sock file already exists: $sock_file"
	else
		# Create the sock_file if it doesn't exist
		touch "$sock_file"
		echo "Sock file created: $sock_file"
	fi

	# Check if the pid_file exists
	if [ -e "$pid_file" ]; then
		echo "PID file already exists: $pid_file"
	else
		# Create the pid_file if it doesn't exist
		touch "$pid_file"
		echo "PID file created: $pid_file"
	fi

	# Continue with the rest of your custom command
	netopeer2-server -d -U"$sock_file" -p "$pid_file"
}

run-netconf-cli() {
	sock_file="$CZECHLIGHT_DIR/install/$build_options/run/netopeer2-server.sock"
	netconf-cli --socket "$sock_file"
}

build-netconf-cli() {
	echo "Building the NETCONF-CLI with the ${compiler} compiler"
	/home/ales/cesnet/czechlight-utils/main.py -a install -t netconf-cli -c "$compiler"
}

build-dependencies() {
	echo "Building the dependencies with the ${compiler} compiler"
	/home/ales/cesnet/czechlight-utils/main.py -a install -t dependencies -c "$compiler"
}

build-czechlight() {
	echo "Building the CzechLight with the ${compiler} compiler"
	/home/ales/cesnet/czechlight-utils/main.py -a install -t all -c "$compiler"
}
