import json,urllib2, base64
import sys
import logging
import subprocess

logging.basicConfig(filename='example.log',level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

def get_metaservice_url():
  p = subprocess.Popen(['facter', 'meta-service-host'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  out, err = p.communicate()
  url = "https://localhost:9443/stratosmetadataservice/application/abc/cluster/pqr/property"
  logging.debug("Meta data service host: %s " % out)
  return url

def get_appId():
  return sys.argv[1]

def get_alias():
  return sys.argv[2]

def get_my_ip():
  return urllib2.urlopen('http://ip.42.pl/raw').read() 

myIp = get_my_ip() 
data = {
        'MYSQLIP': myIp
}

data = {"key":"MYSQLIP","values":myIp}
datas = {data,data}
print(datas)
logging.debug("POST payload: %s " % data)
print(data)

url = get_metaservice_url()
logging.debug("Metadata serive url = %s " % url)
req = urllib2.Request(url)
base64string = base64.encodestring('%s:%s' % ("admin", "admin")).replace('\n', '')
req.add_header("Authorization", "Basic %s" % base64string)
req.add_header('Content-Type', 'application/json')

print json.dumps(data)
response = urllib2.urlopen(req, json.dumps(data))
