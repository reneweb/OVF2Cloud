import xmlrpclib
import re
import hashlib

class OpenNebulaHandler:
    def __init__(self, host, username, password, xml_handler):
        self.host = host
        self.username = username
        self.password = password
        self.xml_handler = xml_handler

	self.password = hashlib.sha1(self.password).hexdigest()
	self.one_auth = '{0}:{1}'.format(self.username, self.password)

        self.img = None
        self.vm_template = None

        self.server = xmlrpclib.ServerProxy(self.host + ':2633/RPC2')

    def upload_image(self):
        img_template = """
          NAME  = {0}
          DESCRIPTION = {1}
          PUBLIC   = NO
          TYPE     = OS
          PERSISTENT  = NO
          PATH     = {2}
        """.format(self.xml_handler.get_name(), 
		   self.xml_handler.get_name, 
		   self.xml_handler.get_external_file)

        self.img = self.server.one.image.allocate(self.one_auth, img_template, 1)
	if not self.img[0]:
            raise Exception(self.img[1])

    def deploy(self):
        self.vm_template = """
          NAME  = {0}
          MEMORY = {1}
          CPU  = {2}
          DISK = [ IMAGE     = {3} ]

          DISK = [ TYPE     = swap,
                   SIZE     = {4},
                   READONLY = "no" ]

          DISK = [ TYPE   = fs,
                   SIZE   = {5},
                   FORMAT = ext3,
                   SAVE   = yes,
                   TARGET = sde ]
        """.format(self.xml_handler.get_name(), 
		   self.xml_handler.get_memory(), 
		   self.xml_handler.get_vcpu_count(),
                   self.img,
                   self.xml_handler.get_disk_by_name("swap_disk")['capacity'],
                   self.xml_handler.get_disk_by_name("root_disk")['capacity'])

        vm = self.server.one.vm.allocate(self.one_auth, self.vm_template)
	if not vm[0]:
            raise Exception(vm[1])

        vminfo = self.server.one.vm.info(self.one_auth, vm[1])
