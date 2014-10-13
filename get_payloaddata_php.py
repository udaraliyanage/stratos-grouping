__author__ = 'udara'

# Get mysql ip from the metadata service.

import urllib2
import base64
import json
import subprocess
from subprocess import PIPE
import logging
import os


logging.basicConfig(filename='get_payload.log',level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

def get_launch_param_file_location():
    launch_params_file = os.path.abspath(os.path.dirname(__file__)).split("extensions")[0] + "payload/launch-params"
    logging.debug("Launch param file location " + launch_params_file)
    return launch_params_file

def get_paylod_property(name):
    logging.debug("[property  " + name + " = " + properties[name] + "]")
    return properties[name]


def get_metadataservice_url():
    return properties['METADATASERVICE_URL']

def restart_apache():
    p = subprocess.Popen(['sudo service apache2 restart'], stdout=PIPE, stderr=PIPE, shell=True)
    stdout_data, stderr_data = p.communicate()
    if p.returncode != 0:
        logging.error(" failed, status code %s stdout %r stderr %r" % ( p.returncode, stdout_data, stderr_data))
        raise RuntimeError(" failed, status code %s stdout %r stderr %r" % ( p.returncode, stdout_data, stderr_data))
    logging.debug("Apache2 restart return code" + stdout_data)

param_file = get_launch_param_file_location()
print param_file
try:
    metadata_file = open(param_file, "r")
except IOError:
    logging.error( 'Cannot open' + param_file)
    raise RuntimeError("Could not open payload params, halting....")


def write_to_env_variable(key, value):
    try:
        command="\nexport "+ key +"="+value
        env_file = open("/etc/apache2/envvars", "a")
        env_file.write(command)
        logging.debug("wrote to /ect/apache2/envvars " + command)
    except IOError:
        logging.error( 'Cannot open' + env_file)
        raise RuntimeError("Could not write to env_file, halting....")

metadata_payload_content = metadata_file.read()
logging.debug("Payload : " + metadata_payload_content)
properties = {}
for param in metadata_payload_content.split(","):
    if param.strip() != "":
        param_value = param.strip().split("=")
        properties[param_value[0]] = param_value[1]

app_id= get_paylod_property('APP_ID')
my_alias = get_paylod_property('CARTRIDGE_ALIAS')

url = get_metadataservice_url()+ "/stratosmetadataservice/application/" + app_id + "/cluster/" + my_alias + "/properties"
logging.debug("Metadata serive url = %s " % url)

req = urllib2.Request(url)
base64string = base64.encodestring('%s:%s' % ("admin", "admin")).replace('\n', '')
req.add_header("Authorization", "Basic %s" % base64string)
req.add_header('Content-Type', 'application/json')
response = urllib2.urlopen(req).read().decode("utf-8")

logging.debug("Response: %s " % response)

data=json.loads(response)
properties=data['properties']
for property in properties:
    key = property['key']
    values = property['values']
    write_to_env_variable(key, values)

restart_apache()
logging.debug("************************")

