# CzechLight Utility Scripts

This repository contains a collection of scripts that are used to manage the CzechLight project.

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