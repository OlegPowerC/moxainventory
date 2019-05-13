import telnetlib
import argparse
import configparser
import xml.etree.cElementTree as ET
import logging

DEBUGGPRINT = True


def getmoxadata(moxaip):
    tn = telnetlib.Telnet(moxaip, 4000)
    tn.write(b"!")
    sts = tn.read_all()
    st1 = sts[2:].decode()
    if len(st1) < 2:
        return "ERROR"
    return st1


class Invent:
    def __init__(self):
        self.name = ""
        self.sn = ""


class Device:
    def __init__(self, ip):
        self.ipaddr = ip
        self.inventory = []


class Devices:
    def __init__(self):
        self.devlist = []


if __name__ == '__main__':
    parcer = argparse.ArgumentParser(description="Params")
    parcer.add_argument('-f', type=str, help="File with devices IP addresses", required=True)
    parcer.add_argument('-o', type=str, help="Output file name without extension", default="inventoryout")

    logging.basicConfig(filename="invent.log", level=logging.INFO)
    logging.info("Start Inventory Process")

    args = parcer.parse_args()
    cp = configparser.ConfigParser()
    cp.read(args.f)
    ipaddrs = cp.get('access', 'switches')
    ipaddrslist = ipaddrs.split('\n')
    if DEBUGGPRINT:
        print(ipaddrslist)

    devicesall = Devices()

    root = ET.Element("switches")

    for ipa in ipaddrslist:
        if DEBUGGPRINT:
            print(ipa)
        devicesall.devlist.append(Device(ipa))

        rdata = getmoxadata(ipa)
        if rdata == 'ERROR':
            print("No Response!")
            logging.error("Host: " + ipa + " no response!")
            continue
        else:

            logging.info("Host: " + ipa + " inventory OK")

            stl2 = rdata.split('\n')
            moxaname = ""
            moxamodel = ""
            moxaserial = ""
            moxalocation = ""

            for a in stl2:
                if a.find("Name") == 0:
                    moxaname = a.split('\t')
                    # print(mdm[0] + ": " + mdm[1] + " " + HOST)
                if a.find("Model") == 0:
                    moxamodel = a.split('\t')
                    # print(mdm[0] + ": " + mdm[1])
                if a.find("Serial") == 0:
                    moxaserial = a.split('\t')
                    # print(mdm[0] + ": " + mdm[1])
                if a.find("Location") == 0:
                    moxalocation = a.split('\t')
                    # print(mdm[0] + ": " + mdm[1])

            if DEBUGGPRINT:
                print(moxaname[1] + "\r\n" + moxamodel[1] + " " + moxaserial[1] + "\r\n" + moxalocation[1])

            swr = ET.SubElement(root, "sw")
            ast = ET.SubElement(swr, "name").text = moxaname[1]
            sip = ET.SubElement(swr, "ip").text = ipa
            sloc = ET.SubElement(swr, "location").text = moxalocation[1]
            sinv = ET.SubElement(swr, "inv")

            invrec = ET.SubElement(sinv, "invrec")
            invrecin = ET.SubElement(invrec, "modulename").text = moxamodel[1]
            invrecin2 = ET.SubElement(invrec, "SN").text = moxaserial[1]

    tree = ET.ElementTree(root)
    tree.write(args.o + ".xml")
