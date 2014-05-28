import sys
import getopt
from xml_handler import XMLHandler
from openstack_handler import OpenStackHandler
from opennebula_handler import OpenNebulaHandler

try:
    opts, args = getopt.getopt(sys.argv[1:], "fphupt", ["file=", "provider=", "host=", "username=", "password=", "tenant="])
except getopt.GetoptError:
    sys.exit(2)

for o, a in opts:
    if o in ("-f", "--file"):
        file = a
    elif o in ("-p", "--provider"):
        provider = a
    elif o in ("-h", "--host"):
        host = a
    elif o in ("-u", "--username"):
        username = a
    elif o in ("-p", "--password"):
        password = a
    elif o in ("-t", "--tenant"):
        tenant = a

if not host or not file or not provider or not username or not password:
    sys.exit(2)

if provider == "OpenStack" and not tenant:
    sys.exit(2)

xmlHandler = XMLHandler(file)
if provider == "OpenStack":
    openstack = OpenStackHandler(host, username, password, tenant, xmlHandler)
    openstack.upload_image()
    openstack.create_flavor()
    openstack.deploy()
    openstack.clean_up()
elif provider == "OpenNebula":
    opennebula = OpenNebulaHandler(host, username, password, xmlHandler)
    opennebula.upload_image()
    opennebula.deploy()



