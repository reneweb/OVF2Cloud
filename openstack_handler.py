import httplib
import uuid
from novaclient.v2_0 import client as nova
from glanceclient.v2_0 import client as glance

class OpenStackHandler:
    def __init__(self, host, username, password, tenant, xml_handler):
        self.host = host
        self.username = username
        self.password = password
        self.tenant = tenant
        self.xml_handler = xml_handler

        self.auth_url = "http://host:5000/v2.0/"

        self.nova_port = 8774
        self.glance_port = 9292

        self.flavor_id = str(uuid.uuid4())

        self.image = None

        httplib.HTTPConnection.debuglevel = 1

    def create_flavor(self):
        nt = nova.Client(self.username, self.password, self.tenant, self.auth_url, service_type="compute")
        nt.flavors.create(self.xml_handler.get_name(), self.xml_handler.get_memory(), self.xml_handler.get_vcpu_count(),
                          self.xml_handler.get_disk_by_name("root_disk")['capacity'], self.flavor_id,
                          self.xml_handler.get_disk_by_name("ephemeral_disk")['capacity'], self.xml_handler.get_disk_by_name("swap_disk")['capacity'])

    def upload_image(self):
        gl = glance.Client(self.username, self.password, self.tenant, self.auth_url)
        self.image = gl.images.create(name=self.xml_handler.get_name())
        self.image.upload(open(self.xml_handler.get_external_file(), 'rb'))

    def deploy(self):
        nt = nova.Client(self.username, self.password, self.tenant, self.auth_url, service_type="compute")
        nt.servers.create(self.xml_handler.get_name(), self.image, self.flavor_id)