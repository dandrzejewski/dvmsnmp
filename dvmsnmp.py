#!/usr/bin/env python3

import configparser
import os
import sys
from typing import Callable, Dict, Tuple, Any
import ext.pydvm.dvmrest as dvmrest


# Grab the configs
CONFIG_PATH = "/etc/dvmsnmp.conf"

config = configparser.ConfigParser()
if not os.path.exists(CONFIG_PATH):
    print("string")
    print(f"Missing config file: {CONFIG_PATH}")
    sys.exit(1)

config.read(CONFIG_PATH)

try:
    host = config.get("connection", "host")
    port = config.getint("connection", "port")
    password = config.get("connection", "password")
except (configparser.NoSectionError, configparser.NoOptionError) as e:
    print("string")
    print(f"Invalid config: {e}")
    sys.exit(1)


# --- OID Definitions ---
OID_BASE_STATUS: str = ".1.3.6.1.4.1.69420.1.0"
OID_TOTAL_AFFILIATIONS: str = ".1.3.6.1.4.1.69420.1.1"
OID_TOTAL_PEERS: str = ".1.3.6.1.4.1.69420.1.2"

# --- SNMP Type Return ---
SNMPType = Tuple[str, Any]  # e.g., ("string", "value") or ("integer", 123)

# --- Connect to DVM ---
fne: dvmrest.DVMRest = dvmrest.DVMRest("ad8g-fne.netbird.selfhosted", 9990, "PASSWORD")
AUTH_FAILED: bool = not fne.auth()

# --- Handler Functions ---
def get_status() -> SNMPType:
    """
    Simply returns that we can connect to DVMHost.  If we get this far, we've authenticated already.
    """
    return ("string", "DVMSNMP is online")

def get_total_affiliations() -> SNMPType:
    """
    Returns the total number of affiliations as reported by dvmhost.
    """
    try:
        data: Dict[str, Any] = fne.get("/report-affiliations")
        total: int = count_total_affiliations(data)
        return ("integer", total)
    except Exception as e:
        return ("string", f"Error: {e}")

def get_total_peers() -> SNMPType:
    """
    Counts and returns the number of peers reported by dvmhost.
    """
    try:
        data: Dict[str, Any] = fne.get("/report-affiliations")
        total: int = len(data)
        return ("integer", total)
    except Exception as e:
        return ("string", f"Error: {e}")
    
        
def count_total_affiliations(affiliations: Dict[str, Any]) -> int:
    """
    Counts the total number of affiliations in the system.
    """
    total: int = 0
    for item in affiliations.get("affiliations", []):
        total += len(item.get("affiliations", []))
    return total

# --- OID -> Handler Map ---
OID_HANDLERS: Dict[str, Callable[[], SNMPType]] = {
    OID_BASE_STATUS: get_status,
    OID_TOTAL_AFFILIATIONS: get_total_affiliations,
    OID_TOTAL_PEERS: get_total_peers
}

# --- SNMP GET Handler ---
def handle_get(oid: str) -> None:
    """
    Handles "get" from snmpd.
    """
    if AUTH_FAILED:
        print("string")
        print("Authentication failed.")
        return

    handler: Callable[[], SNMPType] | None = OID_HANDLERS.get(oid)
    if handler:
        try:
            type_, value = handler()
            print(oid)
            print(type_)
            print(value)
            return
        except Exception as e:
            print(oid)
            print("string")
            print(f"Error: {e}")
            return
    else:
        print("NONE")

# --- SNMP GETNEXT Handler ---
def handle_getnext(oid: str) -> None:
    """
    Handles "getnext" from snmpd -- for example when using snmpwalk.
    """
    if AUTH_FAILED:
        print("string")
        print("Authentication failed.")
        return

    sorted_oids: list[str] = sorted(OID_HANDLERS.keys())
    for next_oid in sorted_oids:
        if oid < next_oid:
            type_, value = OID_HANDLERS[next_oid]()
            print(next_oid)
            print(type_)
            print(value)
            return
    print("NONE")

# --- SNMP Main Loop ---
def main() -> None:
    """
    main.
    """
    while True:
        line: str = sys.stdin.readline()
        if not line:
            break
        line = line.strip()

        if not line:
            continue

        if line == "PING":
            print("PONG")
            sys.stdout.flush()
            continue

        elif line == "get":
            oid: str = sys.stdin.readline().strip()
            handle_get(oid)
            sys.stdout.flush()
            continue

        elif line == "getnext":
            oid: str = sys.stdin.readline().strip()
            handle_getnext(oid)
            sys.stdout.flush()
            continue

        else:
            # Unrecognized input
            print("NONE")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
