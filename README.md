# CzechLight Utility Scripts

This repository contains a collection of scripts that are used to manage the CzechLight project.

## Setup

Download the repository and install the dependencies (for Python 3.10 environment):

```bash
git clone https://github.com/aleskucera/czechlight-utils.git
cd czechlight-utils
pip3 install -r requirements.txt
```

Then create a **CzechLight** directory for example in your home directory by running:

```bash
mkdir ~/czechlight
```

then update the `CZECHLIGHT_DIR` variable in the `main.py` script to point to the newly created
directory.

## Usage

To use the scripts, you need to have Python 3 installed. Then you can run the scripts as follows:

```bash
python3 main.py --action={{ action }} --all/--repository={{ repository }}
```

The `action` parameter specifies the action to be performed. The `all` parameter specifies whether
the action should be performed on all repositories. To perform the action on a single repository, use
the `repository` parameter.

## Actions

The following actions are currently supported:

- `download`: Downloads the repository/repositories.
- `install`: Builds and installs the repository/repositories.
- `clean`: Removes all the files created by the `download` and `install` actions of the repository/repositories.

## Examples

Typical usage:

```bash
python3 main.py --action=download --all
python3 main.py --action=install --all
python3 main.py --action=clean --all
```

## Ubuntu setup

To setup the environment on Ubuntu, run the following commands:

```bash
sudo apt install libcmocka-dev
sudo apt-get install curl libssl-dev libcurl4-openssl-dev
```

```bash
mkdir /home/ales/cesnet/czechlight/install/run
touch /home/ales/cesnet/czechlight/install/run/netopeer2-server.sock
touch /home/ales/cesnet/czechlight/install/run/netopeer2-server.pid
netopeer2-server -d -U/home/ales/cesnet/czechlight/install/run/netopeer2-server.sock -p /home/ales/cesnet/czechlight/install/run/netopeer2-server.pid
netconf-cli --socket /home/ales/cesnet/czechlight/install/run/netopeer2-server.sock
```