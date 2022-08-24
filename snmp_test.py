
(''')
1.This snmp script is for getting the actual power usage of zone 0 and zone 1 in Juniper MX router
2.Device need to be with Junos 16.1 onwards
3. Installation guide:
copy the file or create file in /var/db/scripts/snmp with filename of test.py
 
Configuration below in MX:
set system scripts snmp file test.py oid .1.3.6.1.4.1.2636.13.61.1.9.1.2.1 priority 120
set system scripts snmp file test.py oid .1.3.6.1.4.1.2636.13.61.1.9.1.3.1 priority 120
set system scripts snmp file test.py python-script-user <add user group>
set system scripts language python
set system scripts synchronize
 

 
test from snmp server:
snmpget -v2c -t 2 -c <community> <router_ip> .1.3.6.1.4.1.2636.13.61.1.9.1.2.1 <<<for zone 0
snmpget -v2c -t 2 -c <community> <router_ip> .1.3.6.1.4.1.2636.13.61.1.9.1.3.1 <<<for zone 1

test result:

snmpget -v2c -t 2 -c 50LaRp0l LAB-MX960-3D-01 .1.3.6.1.4.1.2636.13.61.1.9.1.3.1
SNMPv2-SMI::enterprises.2636.13.61.1.9.1.3.1 = INTEGER: 627

snmpget -v2c -t 2 -c 50LaRp0l LAB-MX960-3D-01 .1.3.6.1.4.1.2636.13.61.1.9.1.2.1
SNMPv2-SMI::enterprises.2636.13.61.1.9.1.2.1 = INTEGER: 228

(''')

from jnpr.junos import Device
import jcs
 
def main():
    dev = Device()
    # Opens a connection
    dev.open()
    zone = dev.rpc.get_power_usage_information()

    zone0 = zone.findtext(".//power-usage-zone-information/[zone='0']/capacity-actual-usage")
    zone1 = zone.findtext(".//power-usage-zone-information/[zone='1']/capacity-actual-usage")
    snmp_action = jcs.get_snmp_action()
    snmp_oid = jcs.get_snmp_oid()
    jcs.syslog("8", "snmp_action = ", snmp_action, " snmp_oid = ", snmp_oid)
    if snmp_action == 'get':
        if snmp_oid == '.1.3.6.1.4.1.2636.13.61.1.9.1.2.1':
            jcs.emit_snmp_attributes(snmp_oid, "Integer32", zone0.strip())
        elif snmp_oid == '.1.3.6.1.4.1.2636.13.61.1.9.1.3.1':
            jcs.emit_snmp_attributes(snmp_oid, "Integer32", zone1.strip())


 
    dev.close()
if __name__ == '__main__':
    main()