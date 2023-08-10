# Falcon bulk actions
Perform bulk actions on Falcon instance using falconpy SDK.

### Purpose
Falcon RTR with its web interface allows to execute commands remotely on a host. This is sufficient for one host but when you want to execute commands on several hosts this is not possible with the web interface.
Using the falconpy SDK allows you to launch actions on multiple machines with a single command.
In my case, I use ```batch_admin_command``` (details [here](https://www.falconpy.io/Service-Collections/Real-Time-Response-Admin.html?highlight=batch_admin_command#batchadmincmd)) to execute ```put``` and ```runscript```. It is perfect for running scripts or commands on all your hosts for your IT administrators or it will allow you to act on all your hosts in the event of a cyber incident.

You can adapt the script to suit your needs.

### Requirements
- Python and Pip (tested with Python 3.11+ and Pip 23+)
- Crowdstrike-falconpy

### Install Python libraries requirements
- ```pip install -r requirements.txt```

### Commands examples
- List of scripts & putfiles : ```python.exe .\falcon_bulk_actions.py --client_id <client_id> --client_secret <client_secret> --base_url eu1 --list_scripts show --list_putfiles show```
- Execute script on host : ```python.exe .\falcon_bulk_actions.py --client_id <client_id> --client_secret <client_secret> --base_url eu1 --machines_name HOSTNAME,*HOSTN*,hos* --scripts_name script1```
- Execute script on Windows : ```python.exe .\falcon_bulk_actions.py --client_id <client_id> --client_secret <client_secret> --base_url eu1 --machines_plateform Windows --scripts_name script1,script2```
- Execute raw commands on Windows : ```python.exe .\falcon_bulk_actions.py --client_id <client_id> --client_secret <client_secret> --base_url eu1 --machines_plateform Windows --raw_commands "[System.Security.Principal.WindowsIdentity]::GetCurrent().Name"```
- Execute raw commands on Linux ```python.exe .\falcon_bulk_actions.py --client_id <client_id> --client_secret <client_secret> --base_url eu1 --machines_plateform Linux --raw_commands "ls -la"```

### Log execution
In order to know if everything went well, a JSON log file is generated at each steps.

Examples :
- Init session : 
```
[
  {
    "nb_true": 1,
    "nb_false": 0,
    "list_false": []
  },
  {
    "devide_id": "DEVICE_ID",
    "hostname": "HOSTNAME",
    "complete": true,
    "stdout": "C:\\",
    "stderr": ""
  }
]
```

- Runscript :
```
[
  {
    "nb_true": 1,
    "nb_false": 0,
    "list_false": []
  },
  {
    "devide_id": "DEVICE_ID",
    "hostname": "HOSTNAME",
    "complete": true,
    "stdout": "Uninstalling...",
    "stderr": ""
  }
]
```