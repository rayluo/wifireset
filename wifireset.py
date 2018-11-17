"""WiFiReset is a tool created to solved a very specific problem:
my main wifi router sometimes stops transmitting WiFi signal,
and would typically need a manual restart. But its wired ports work all the time.

So I come up with this workaround.
1. Runs WiFiReset on a device connected to main router M, via ethernet wire.
   (In my case, I have a cascading router C, connecting to main router via wire,
   and my WiFiReset runs on a device wirelessly connecting to router C.
   That still counts as a wired connection, from main router's perspective.)
2. WiFiReset pings a neighbor in the network, periodically (i.e. via crontab).
3. If the neighbor is unreachable, WiFiReset logs in to the main router,
   and reset WiFi radio, automatically.

It works. Currently this script supports my main router ArrisSbg6580 only.
"""  # Note: This docstring will also be used as CLI description.
import re
import time
import os
import logging
import argparse

import requests


__version__ = "1.0.0"
logger = logging.getLogger(__file__)

class Router(object):

    def __init__(self, password, username="admin", ip="192.168.0.1"):
        raise NotImplementedError()

    def _radio(self, enable=True):
        raise NotImplementedError()

    def toggle_radio(self, wait=5):
        self._radio(False)
        time.sleep(wait)
        self._radio(True)

class ArrisSbg6580(Router):
    def __init__(self, password, username="admin", ip="192.168.0.1"):
        self.ip = ip
        self.session = requests.session()
        result = self.session.post(  # login
            "http://{}/goform/login".format(ip),
            data={"loginUsername": username, "loginPassword": password})
        assert "login" not in result.text, "Probably incorrect username/password?"

    def _radio(self, enable=True):
        radio_page = self.session.get("http://{}/wlanRadio.asp".format(self.ip))
        radio = self.session.post(
            "http://{}/goform/wlanRadio.pl".format(self.ip), data={
            "GetNonce": re.search(
                '"GetNonce" size=31 value=(\w+)>', radio_page.text).group(1),
            "WirelessEnable": 1 if enable else 0,
            "OutputPower": 100,
            "Band": 2,  # 2 means 2.4 GHz, 1 means 5 GHz
            "NMode": 3,  # 3 means b/g/n mode
            "NBandwidth": 20,  # 20 means 20 Mhz, 40 means 40 MHz
            "ChannelNumber": 0,  # 0 means Auto

            "commitwlanRadio": 1,  # It was set by javascript in original page
            "restoreWirelessDefaults": 0,
            "scanActions": 0,
            "SelectedRadio": 0,
            })
        assert "login" not in radio.text
        assert "Error" not in radio.text, radio.text

def _ping(host):  # Returns True if host is up; False otherwise.
    # The "-c 1" is POSIX only
    return os.system("ping -c1 -w2 {} > /dev/null 2>&1".format(host)) == 0

def ping(host, retry=5):  # Returns True if host is up; False otherwise.
    for i in range(retry):
        if i:  # That means it is not the first attempt
            time.sleep(3)
        if _ping(host):
            return True
        logger.debug("Neighbor {} unreachable".format(host))
    return False

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=__doc__)
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("neighbor_ip", help="IP of a neighbor to ping")
    parser.add_argument("--router_ip", help="IP of router", default="192.168.0.1")
    parser.add_argument("--username", help="Username to login to the router",
        default="admin")
    parser.add_argument("--password", help="Password to login to the router",
        default="admin")  # Not that I want to commit credential into VCS,
            # but some router actually uses such well-known default password.
    supported_routers = {  # "NameInString": Class
        "ArrisSbg6580": ArrisSbg6580,
        }
    parser.add_argument("--model", required=True, help="The model of your router",
        choices=supported_routers),
    args = parser.parse_args()
    if ping(args.neighbor_ip):
        logger.info("Neighbor {} in contact".format(args.neighbor_ip))
    else:
        logger.warning("Ping {} failed. Restarting WiFi...".format(args.neighbor_ip))
        router = supported_routers[args.model](
            args.password, username=args.username, ip=args.router_ip)
        router.toggle_radio()

