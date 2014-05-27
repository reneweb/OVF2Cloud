import httplib
import uuid
from novaclient.v1_1 import client as nova
from glanceclient import client as glance
from keystoneclient.v2_0 import client as keystone

class OpenStackHandler:
    def __init__(self, host, username, password, tenant, xml_handler):
        self.host = host
        self.username = username
        self.password = password
        self.tenant = tenant
        self.xml_handler = xml_handler

        self.auth_url = host + ":5000/v2.0/"

        self.nova_port = 8774
        self.glance_port = 9292

	self.glance_endpoint = host + ":" + str(self.glance_port)

        self.flavor_id = str(uuid.uuid4())

        self.image = None

        httplib.HTTPConnection.debuglevel = 1

    def create_flavor(self):
        nt = nova.Client(self.username, self.password, self.tenant, self.auth_url, service_type="compute")
        nt.flavors.create(self.xml_handler.get_name(), self.xml_handler.get_memory(), self.xml_handler.get_vcpu_count(),
                          self.xml_handler.get_disk_by_name("root_disk")['capacity'], self.flavor_id,
                          self.xml_handler.get_disk_by_name("ephemeral_disk")['capacity'], self.xml_handler.get_disk_by_name("swap_disk")['capacity'])

    def upload_image(self):
	ks = keystone.Client(username=self.username, password=self.password, tenant_name=self.tenant, auth_url=self.auth_url)
        gl = glance.Client(2, endpoint=self.glance_endpoint, token=ks.auth_token)
        self.image = gl.images.create(name=self.xml_handler.get_name(), disk_format="qcow2", container_format="bare")
	gl.images.upload(self.image.id, open(self.xml_handler.get_external_file(), 'rb'))

    def deploy(self):
        nt = nova.Client(self.username, self.password, self.tenant, self.auth_url, service_type="compute")
        nt.servers.create(self.xml_handler.get_name(), self.image, self.flavor_id)
