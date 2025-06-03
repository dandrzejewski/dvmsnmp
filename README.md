# DVMSNMP
Allow dvmhost to be monitored via net-snmp.

### Clone the repository locally.
```
git clone ...
```

### Set up your config in `dvmsnmp.conf`
```ini
[connection]
host = host-or-ip
port = port
password = password
```

### Update your snmpd config appropriately:

`/etc/snmp/snmpd.config.d/dvmsnmp.conf`

```
pass_persist .1.3.6.1.4.1.69420 /path/to/dvmsnmp.py
```

### Restart snmpd
```
systemctl restart snmpd
```

### Test it
```
# Get status info
root:~# snmpget -v2c -c public 127.0.0.1 .1.3.6.1.4.1.69420.1.0
iso.3.6.1.4.1.69420.1.0 = STRING: "DVMSNMP is online"

# Walk it
root:~# snmpwalk -v2c -c public 127.0.0.1 .1.3.6.1.4.1.69420
iso.3.6.1.4.1.69420.1.0 = STRING: "DVMSNMP is online"
iso.3.6.1.4.1.69420.1.1 = INTEGER: 0
iso.3.6.1.4.1.69420.1.2 = INTEGER: 2
```

---

## OIDs currently available: 

| OID | Return Type | Description|
|-----|-------------|------------|
.1.3.6.1.4.1.69420.1.0 | String | Connection status, string 
.1.3.6.1.4.1.69420.1.1 | Integer | Number of affiliated subscriber units
.1.3.6.1.4.1.69420.1.2 | Integer | Number of connected peers

Want more?  Open an issue, or better yet, submit a pull request!
