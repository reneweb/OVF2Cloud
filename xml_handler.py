import xml.dom.minidom as dom

class XMLHandler:
    def __init__(self, ovfFilePath):
        self.ovf = dom.parse(ovfFilePath).firstChild
        self.name = self.ovf.getElementsByTagName('VirtualSystem')[0].getElementsByTagName('Name')[0].firstChild.nodeValue
        self.external_files = self.ovf.getElementsByTagName('References')[0].getElementsByTagName('File')
        self.disks = self.ovf.getElementsByTagName('DiskSection')[0].getElementsByTagName('Disk')

        vhs = self.ovf.getElementsByTagName('VirtualSystem')[0].getElementsByTagName('VirtualHardwareSection')[0]
        self.system = vhs.getElementsByTagName('System')[0]
        self.items = vhs.getElementsByTagName('Item')

    def get_name(self):
        return self.name

    def get_external_file(self):
        return self.external_files[0].getAttribute("ovf:href")

    def get_vcpu_count(self):
        return [item.getElementsByTagName('rasd:VirtualQuantity')[0].firstChild.nodeValue
                for item in self.items
                if item.getElementsByTagName('rasd:ResourceType')[0].firstChild.nodeValue == '3'][0]

    def get_memory(self):
        return [item.getElementsByTagName('rasd:VirtualQuantity')[0].firstChild.nodeValue
                for item in self.items
                if item.getElementsByTagName('rasd:ResourceType')[0].firstChild.nodeValue == '4'][0]

    def get_disks(self):
        disks_to_attach_names = self.__get_disks_to_attach_names()
        self.disks = map(lambda disk: self.__add_attach_data_to_disk(disk, disks_to_attach_names), self.disks)

        return map(lambda disk: {"name": disk.getAttribute('ovf:diskId'),
                                 "capacity": int(disk.getAttribute('ovf:capacity')) / (2**30),
                                 "attach": disk.getAttribute('attach')}, self.disks)

    def get_disk_by_name(self, name):
        disks_to_attach_names = self.__get_disks_to_attach_names()
        disk = [disk for disk in self.disks if disk.getAttribute("ovf:diskId") == name][0]
        disk = self.__add_attach_data_to_disk(disk, disks_to_attach_names)
        return {"name": disk.getAttribute('ovf:diskId'),
                "capacity": int(disk.getAttribute('ovf:capacity')) / (2**30),
                "attach": disk.getAttribute('attach')}

    def __add_attach_data_to_disk(self, disk_element, disks_to_attach):
        if disk_element.getAttribute('ovf:diskId') in disks_to_attach:
            disk_element.setAttribute("attach", True)
            return disk_element
        else:
            disk_element.setAttribute("attach", False)
            return disk_element

    def __get_disks_to_attach_names(self):
        return [item.getElementsByTagName('rasd:HostResource')[0].firstChild.nodeValue.split("/")[2]
                for item in self.items
                if item.getElementsByTagName('rasd:ResourceType')[0].firstChild.nodeValue == '17']