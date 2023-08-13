#!/usr/bin/env python3

"""
Python script use to perform bulk actions on Falcon instance using "crowdstrike-falconpy" SDK. 
"""

from json import dump
from datetime import datetime
from argparse import ArgumentParser
from falconpy import Hosts, RealTimeResponse, RealTimeResponseAdmin

parser = ArgumentParser()
parser.add_argument("--client_id", help="Client ID")
parser.add_argument("--client_secret", help="Client Secret")
parser.add_argument("--base_url", help="Base URL")
parser.add_argument("--list_scripts", help="Show")
parser.add_argument("--list_putfiles", help="Show")
parser.add_argument("--condition", help="Query condition: AND='+' OR=','")
parser.add_argument("--machines_name", help="Name of hosts")
parser.add_argument("--machines_plateform", help="Name of OS plateform (Windows/Linux/Mac)")
parser.add_argument("--scripts_name", help="List of scripts name")
parser.add_argument("--putfiles_name", help="List of put files name")
parser.add_argument("--raw_commands", help="List of raw commands")
args = parser.parse_args()

# Auth for SDK objects
falcon_hosts = Hosts(client_id=args.client_id, client_secret=args.client_secret, base_url=args.base_url)
falcon_rtr   = RealTimeResponse(client_id=args.client_id, client_secret=args.client_secret, base_url=args.base_url)
falcon_rtra  = RealTimeResponseAdmin(client_id=args.client_id, client_secret=args.client_secret, base_url=args.base_url)

# Datetime for logging
now = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

def write_logs(log_data: str | list, log_file_name: str) -> None:
    """Write logs file"""
    if isinstance(log_data, list):
        log_content = log_data
        if "error" not in log_file_name.lower():
            log_content = extract_log_infos(log_content)
    else:
        log_content = []
        log_content.append(log_data)
    with open(file=log_file_name, mode="w", encoding='UTF-8') as f:
        dump(obj=log_content, fp=f, indent=2, separators=(",", ": "))

def extract_log_infos(log_content: list) -> list:
    """Extract log infos"""
    nb_true = 0
    nb_false = 0
    list_false = []
    for log in log_content:
        if log["complete"]:
            nb_true = nb_true + 1
        else:
            nb_false = nb_false + 1
            list_false.append(log["hostname"])
    # Add global execution infos
    infos_execution = {}
    infos_execution["nb_true"] = nb_true
    infos_execution["nb_false"] = nb_false
    infos_execution["list_false"] = list_false
    log_content.insert(0, infos_execution)
    return log_content

def handle_error(errors: dict) -> None:
    """Handle API errors"""
    for error in errors:
        # Display the API error detail
        error_log = {}
        if "code" in error:
            error_log["error_code"] = error["code"]
        error_log["error_message"] = error["message"]
        write_logs(error_log, f"error_{now}.json")

def get_hosts(condition: str, machines_name: str | None, machine_plateform: str | None) -> dict:
    """Get hosts list"""
    hosts_list = []
    params_filter = []

    if machines_name is not None:
        for host in machines_name.split(","):
            params_filter.append(f"hostname:'{host}'")
    
    if machine_plateform is not None:
        for plateform in machine_plateform.split(","):
            params_filter.append(f"platform_name:'{plateform}'")

    # Retrieve a host list
    host_search_result = falcon_hosts.query_devices_by_filter(filter=condition.join(params_filter))
    host_details_found = get_hosts_details(host_search_result)
    if host_details_found:
        for host in host_details_found:
            hosts_list.append(host)

    return hosts_list

def get_hosts_details(hosts_search_result: dict) -> dict:
    """Gets hosts details"""
    # Confirm we received a success response back from the CrowdStrike API
    if hosts_search_result["status_code"] == 200:
        hosts_found = hosts_search_result["body"]["resources"]
        # Confirm our search produced results
        if hosts_found:
            # Retrieve the details for all matches
            hosts_detail = falcon_hosts.get_device_details(ids=hosts_found)["body"]["resources"]
            hosts = []
            for detail in hosts_detail:
                # Save info
                host_detail = {}
                host_detail["devide_id"] = detail["device_id"]
                host_detail["hostname"] = detail["hostname"]
                hosts.append(host_detail)
            return hosts
        else:
            write_logs({"message": f"No hosts found matching your query within your Falcon tenant."}, f"error_{now}.json")
    else:
        # Retrieve the details of the error response
        handle_error(hosts_search_result["body"]["errors"])

def get_scripts() -> None:
    """Get scripts list"""
    # Retrieve a list of custom scripts
    list_scripts = falcon_rtra.list_scripts()

    # Confirm we received a success response back from the CrowdStrike API
    if list_scripts["status_code"] == 200:
        scripts_found = list_scripts["body"]["resources"]
        if scripts_found:
            # Retrieve the details of all putfiles
            handle_response_scripts_and_files_infos(falcon_rtra.get_scripts_v2(ids=scripts_found)["body"]["resources"], "Custom scripts")
        else:
            write_logs({"message": "No scripts found within your Falcon tenant."}, f"error_{now}.json")
    else:
        # Retrieve the details of the error response
        handle_error(list_scripts["body"]["errors"])

def get_put_files() -> None:
    """Get putfiles list"""
    # Retrieve a list of put files
    list_put_file = falcon_rtra.list_put_files()

    # Confirm we received a success response back from the CrowdStrike API
    if list_put_file["status_code"] == 200:
        put_files_found = list_put_file["body"]["resources"]
        if put_files_found:
            # Retrieve the details of all putfiles
            handle_response_scripts_and_files_infos(falcon_rtra.get_put_files_v2(ids=put_files_found)["body"]["resources"], "Put files")
        else:
            write_logs({"message": "No putfile found within your Falcon tenant."}, f"error_{now}.json")
    else:
        # Retrieve the details of the error response
        handle_error(list_put_file["body"]["errors"])

def handle_response_scripts_and_files_infos(scripts_and_files: dict, output_type: str) -> None:
    """Get infos of customs scripts or put files"""
    print(f"{output_type} :")
    for detail in scripts_and_files:
        print("Name : " + f"{detail['name']}" + " | Plateform : " + f"{detail['platform']}")

def init_session(hosts_list: dict) -> dict:
    """Init sessions on hosts"""
    list_hosts_id = []
    for host in hosts_list:
        list_hosts_id.append(host["devide_id"])

    # Init batch session
    init_session = falcon_rtr.batch_init_sessions(host_ids=list_hosts_id, host_timeout_duration="10s", queue_offline=False, timeout=90, timeout_duration="5m",)

    # Confirm we received a success response back from the CrowdStrike API
    if init_session["status_code"] == 201:
        handle_201_code(init_session, "batch_init_session", True, hosts_list)
        return init_session
    else:
        # Retrieve the details of the error response
        handle_error(init_session["body"]["errors"])

def delete_session(sessions_list: list) -> None:
    """Delete hosts sessions"""
    for key in sessions_list.keys():
        delete_session = falcon_rtr.delete_session(sessions_list[key]["session_id"])
        if delete_session["status_code"] != 204:
            handle_error(delete_session["body"]["errors"])

def batch_admin_command(base_command: str, batch_id: dict, command: str, log_info: str, hosts_list: list) -> None:
    """Execute admin command"""
    # Execute batch command
    admin_command = falcon_rtra.batch_admin_command(base_command=base_command, batch_id=batch_id, command_string=command, persist_all=False, timeout=90, timeout_duration="5m")
    if admin_command["status_code"] == 201:
            handle_201_code(admin_command, f"batch_{base_command}_{log_info}", False, hosts_list)
    else:
        # Retrieve the details of the error response
        handle_error(admin_command["body"]["errors"])

def handle_201_code(response_data: list, log_file: str, is_init_session: bool, hosts_list: list) -> None:
    """Handle 201 response code"""
    if is_init_session:
        response = response_data["body"]["resources"].items()
    else:
        response = response_data["body"]["combined"]["resources"].items()

    data = []
    for device_id, device_data in response:
        # Save infos
        info = {}
        info["devide_id"] = device_id
        info["hostname"] = get_hostname(hosts_list, device_id)
        info["complete"] = device_data["complete"]
        info["stdout"] = device_data["stdout"]
        info["stderr"] = device_data["stderr"]
        data.append(info)
    write_logs(data, f"{log_file}_{now}.json")

def get_hostname(hosts_list: list, device_id: str) -> str:
    """Get hostname"""
    for host in hosts_list:
        if host["devide_id"] == device_id:
            return host["hostname"]

if __name__ == "__main__":
    # Show list of custom scripts
    if args.list_scripts == "show":
        get_scripts()

    # Show list of put files
    if args.list_putfiles == "show":
        get_put_files()

    # Bulk script execution
    if (args.machines_name is not None or args.machines_plateform is not None and 
        args.scripts_name is not None or args.putfiles_name is not None or args.raw_commands is not None):
        # Get list of hosts
        hosts_list = get_hosts(condition=args.condition, machines_name=args.machines_name, machine_plateform=args.machines_plateform)
        print(f"Number of hosts found => {len(hosts_list)}")
        if len(hosts_list) >= 1:
            # Init batch session
            batch_init = init_session(hosts_list)
            # Run command
            if batch_init["body"]["batch_id"]:
                if args.scripts_name is not None:
                    for script in args.scripts_name.split(","):
                        # Command : runscript -CloudFile
                        batch_admin_command(batch_id=batch_init["body"]["batch_id"], base_command="runscript", command=f"runscript -CloudFile={script}", log_info=script, hosts_list=hosts_list)
                if args.putfiles_name is not None:
                    for putfile in args.putfiles_name.split(","):
                        # Command : put
                        batch_admin_command(batch_id=batch_init["body"]["batch_id"], base_command="put", command=f"put {putfile}", log_info=putfile, hosts_list=hosts_list)
                        if args.machines_plateform == "Windows":
                            # Command : runscript -HostPath
                            batch_admin_command(batch_id=batch_init["body"]["batch_id"], base_command="runscript", command=f"runscript -HostPath='C:\{putfile}'", log_info=putfile, hosts_list=hosts_list)
                        else:
                            batch_admin_command(batch_id=batch_init["body"]["batch_id"], base_command="runscript", command=f"runscript -HostPath='/{putfile}'", log_info=putfile, hosts_list=hosts_list)
                if args.raw_commands is not None:
                    for command in args.raw_commands.split(","):
                        # Command : runscript -Raw
                        batch_admin_command(batch_id=batch_init["body"]["batch_id"], base_command="runscript", command=f"runscript -Raw=```{command}```", log_info="raw_command", hosts_list=hosts_list)
            delete_session(batch_init["body"]["resources"])