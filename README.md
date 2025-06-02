Allow dvmhost to be monitored via net-snmp.

# Place the file

```
cp dvmsnmp.py /usr/local/bin  # or pick your own, whatever
chmod +x /usr/local/bin/dvmsnmp.py
```

# snmpd config
```
pass_persist .1.3.6.1.4.1.69420 /usr/local/bin/dvmsnmp.py
```

# /etc/dvmsnmp.conf
```ini
[connection]
host = host-or-ip
port = port
password = password
```