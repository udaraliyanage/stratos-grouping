__author__ = 'udara'

import urllib2
from urllib2 import Request, urlopen, URLError, HTTPError
import json
import base64
import logging,sys,os

logging.basicConfig(filename='publish_metadata.log',level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

def get_launch_param_file_location():
    launch_params_file = os.path.abspath(os.path.dirname(__file__)).split("extensions")[0] + "payload/launch-params"
    logging.debug("Launch param file location " + launch_params_file)
    return launch_params_file

param_file = get_launch_param_file_location()
logging.debug("Payload file location " + param_file)

print param_file
try:
    metadata_file = open(param_file, "r")
except IOError:
    logging.error( 'Cannot open', param_file)
    raise RuntimeError

metadata_payload_content = metadata_file.read()
logging.debug("Payload : " + metadata_payload_content)
properties = {}
for param in metadata_payload_content.split(","):
    if param.strip() != "":
        param_value = param.strip().split("=")
        properties[param_value[0]] = param_value[1]

logging.debug("Payload properties : ")
logging.debug(properties)

def get_paylod_property(name):
    logging.debug("[property  " + name + " = " + properties[name] + "]")
    return properties[name]


def get_metadataserviceurl():
    # return properties['METADATASERVICE_URL']
    return "https://localhost:9443"



def do_post(url, data):
    req = urllib2.Request(url)
    base64string = base64.encodestring('%s:%s' % ("admin", "admin")).replace('\n', '')
    req.add_header("Authorization", "Basic %s" % base64string)
    req.add_header('Content-Type', 'application/json')

    try:
        logging.info('sending to ' + url)
        logging.info('sent data ' + json.dumps(data))
        response = urllib2.urlopen(req, json.dumps(data))
    except HTTPError as e:
        logging.error('The server couldn\'t fulfill the request.')
        logging.error('Error code .' + e.code)
    except URLError as e:
        print 'We failed to reach a server.'
        logging.error('We failed to reach a server.')
        logging.error('Reason: ' + e.reason)

my_alias = get_paylod_property('CARTRIDGE_ALIAS')

my_ip = urllib2.urlopen('http://ip.42.pl/raw').read()
my_username = "root"
my_password = "root"
#app_id= get_paylod_property(' APP_ID')
appid = "appid"

resource_url = get_metadataserviceurl()+ "/stratosmetadataservice/application/" + appid + "/cluster/" + my_alias + "/property"
print (resource_url)
data = {"key":"MYSQLIP","values":my_ip}
do_post(resource_url, data)
data = {"key":"MYSQL_PASS","values":my_password}
do_post(resource_url, data)

data = {"key":"MYSQL_USERNAME","values":my_username}
do_post(resource_url, data)



print("************************")
