# Falcon bulk actions
Perform bulk actions on Falcon instance using falconpy SDK.

### Purpose
Falcon RTR with its web interface allows to execute commands remotely on a host. This is sufficient for one host but when you want to execute commands on several hosts this is not possible with the web interface.
Using the falconpy SDK allows you to launch actions on multiple machines with a single command.
In my case, I use ```batch_admin_command``` (details [here](https://www.falconpy.io/Service-Collections/Real-Time-Response-Admin.html?highlight=batch_admin_command#batchadmincmd)) to execute ```put``` and ```runscript```. It is perfect for running scripts or commands on all your hosts for your IT administrators or it will allow you to act on all your hosts in case of a cyber incident.

### Requirements
- Python and Pip (tested with Python 3.11+ and Pip 23+)
- [crowdstrike-falconpy](https://github.com/CrowdStrike/falconpy) 

### Install Python libraries requirements
- ```pip install -r requirements.txt```

### Commands infos

- You need to create API acces on your Falcon tenant (detail [here](https://www.crowdstrike.com/blog/tech-center/get-access-falcon-apis/)) with scopes "Hosts" in read, "RTR" in read/write and "RTRA" in write
- You need to define your ```base_url``` (detail [here](https://www.falconpy.io/Usage/Environment-Configuration.html#base-url))
- You can list your falcon RTR "custom scripts" (```--list_scripts show```), "put files" (```--list_putfiles show```) or both
- You can choose to run script on platform (```--machines_plateform```), machine (```--machines_name```) or both
- For querying platform and/or hostname you can choose condition for your parameters: AND ```+```, OR ```,``` detail ([here](https://falconpy.io/Usage/Falcon-Query-Language.html#filtering-using-multiple-properties-and-conditions)). Try your query when you choose platform and hostname
- If you run Linux script on Windows, don't worry it's detected and not executed. Logic works on all platforms
- In this script I using only the commands ```put```, ```runscript -CloudFile```, ```runscript -HostPath```, ```runscript -Raw```

You can adapt script to implement more RTR commands ;-)

### Commands examples
- List of scripts & putfiles :
  
```python.exe .\falcon_bulk_actions.py --client_id <client_id> --client_secret <client_secret> --base_url <base_url> --list_scripts show --list_putfiles show```

- Execute script on specific hosts :
  
```python.exe .\falcon_bulk_actions.py --client_id <client_id> --client_secret <client_secret> --base_url <base_url> --condition + --machines_name HOSTNAME,*HOST,HOST* --scripts_name script1```

- Execute script on hosts who match patterns :
  
```python.exe .\falcon_bulk_actions.py --client_id <client_id> --client_secret <client_secret> --base_url <base_url> --condition , --machines_name HOSTNAME,*HOST,HOST* --scripts_name script1```

- Execute script on specific Windows hosts :
  
```python.exe .\falcon_bulk_actions.py --client_id <client_id> --client_secret <client_secret> --base_url <base_url> --condition + --machines_plateform Windows --machines_name HOST* --scripts_name script1```

- Execute putfiles on Linux hosts :
  
```python.exe .\falcon_bulk_actions.py --client_id <client_id> --client_secret <client_secret> --base_url <base_url> --condition + --machines_plateform Linux --putfiles_name script1.sh,script2.sh```

- Execute raw commands on Windows hosts :
  
```python.exe .\falcon_bulk_actions.py --client_id <client_id> --client_secret <client_secret> --base_url <base_url> --condition + --machines_plateform Windows --raw_commands "[System.Security.Principal.WindowsIdentity]::GetCurrent().Name"```

- Execute raw commands on Linux hosts :
  
```python.exe .\falcon_bulk_actions.py --client_id <client_id> --client_secret <client_secret> --base_url <base_url> --condition + --machines_plateform Linux --raw_commands "ls -la"```

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