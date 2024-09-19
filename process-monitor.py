"""
1.configuration in router:
set system scripts snmp file process-monitor.py oid .1.3.6.1.4.1.2636.13.61.1.9.1.2
set system scripts snmp file process-monitor.py oid .1.3.6.1.4.1.2636.13.61.1.9.1.3
set system scripts snmp file process-monitor.py oid .1.3.6.1.4.1.2636.13.61.1.9.1.4
set system scripts snmp file process-monitor.py oid .1.3.6.1.4.1.2636.13.61.1.9.1.5
set system scripts language python3
set system scripts synchronize
set system scripts snmp file process-monitor.py python-script-user JNPR-RO

2.add annotate for each oid for easier reference
edit system scripts snmp file process-monitor.py
annotate oid .1.3.6.1.4.1.2636.13.61.1.9.1.2 "chassisd"   
annotate oid .1.3.6.1.4.1.2636.13.61.1.9.1.3 "rpd"  
annotate oid .1.3.6.1.4.1.2636.13.61.1.9.1.4 "ppmd"  
annotate oid .1.3.6.1.4.1.2636.13.61.1.9.1.5 "bfdd"  

3. test from snmp server or local
[huasu@pinkie ~]$ snmpget -v2c -t 2 -c 50LaRp0l lab-mx480-3d-02 .1.3.6.1.4.1.2636.13.61.1.9.1.4
SNMPv2-SMI::enterprises.2636.13.61.1.9.1.4.1 = INTEGER: 22224
[huasu@pinkie ~]$ snmpget -v2c -t 2 -c 50LaRp0l lab-mx480-3d-02 .1.3.6.1.4.1.2636.13.61.1.9.1.3
SNMPv2-SMI::enterprises.2636.13.61.1.9.1.3.1 = INTEGER: 242284
[huasu@pinkie ~]$ snmpget -v2c -t 2 -c 50LaRp0l lab-mx480-3d-02 .1.3.6.1.4.1.2636.13.61.1.9.1.2
SNMPv2-SMI::enterprises.2636.13.61.1.9.1.2.1 = INTEGER: 69892

huasu@lab-mx480-3d-02-re0> show snmp mib get .1.3.6.1.4.1.2636.13.61.1.9.1.4
juniperMIB.13.61.1.9.1.4.1 = 22224

4. User can add customised process command from cli 'show system processes wide detail' in below TARGET_COMMANDS_OIDS and configuration of juniper router accordingly.
"""
from jnpr.junos import Device
import jcs
 
# Define the list of exact command names to match and their corresponding SNMP OIDs
TARGET_COMMANDS_OIDS = {
    '/usr/sbin/chassisd -N': '.1.3.6.1.4.1.2636.13.61.1.9.1.2',
    '/usr/libexec64/rpd -N': '.1.3.6.1.4.1.2636.13.61.1.9.1.3',
    '/usr/sbin/ppmd -N': '.1.3.6.1.4.1.2636.13.61.1.9.1.4',
    '/usr/sbin/bfdd -N': '.1.3.6.1.4.1.2636.13.61.1.9.1.5'
}
 
def get_rss_for_command(dev, command):
    """Function to get the RSS value for a specific command."""
    response = dev.rpc.get_system_process_information(detail=True, wide=True)
    commands = response.xpath('//process-information/process/command')
    rss_values = response.xpath('//process-information/process/rss')
 
    for command_elem, rss_elem in zip(commands, rss_values):
        cmd = command_elem.text.strip()
        if cmd == command:
            return rss_elem.text.strip()
    return None
 
def main():
    # Connect to the device
    dev = Device()
    dev.open()
 
    snmp_action = jcs.get_snmp_action()
    snmp_oid = jcs.get_snmp_oid()
 
    if snmp_action == 'get':
        for command, oid in TARGET_COMMANDS_OIDS.items():
            if snmp_oid == oid:
                rss_value = get_rss_for_command(dev, command)
                if rss_value:
                    jcs.emit_snmp_attributes(snmp_oid, "Integer32", rss_value)
                else:
                    jcs.syslog("8", f"Command {command} not found.")
                break
 
    dev.close()
 
if __name__ == '__main__':
    main()
