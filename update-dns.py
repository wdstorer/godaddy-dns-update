#!/usr/bin/python
import yaml
import io
import urllib2
import requests
import json

def read_config():
  with open("config.yml", 'r') as stream:
    data_loaded = yaml.load(stream)
  return data_loaded

def get_publicIP():
  #ext_ip = urllib2.urlopen('https://api.ipifyx.org').read()
  
  try:
    result = requests.get('https://api.ipify.org', timeout=5).text
  except requests.exceptions.RequestException as e:
    print e
    exit(1)

  return result

def get_dnsIP(key, secret, domain, name):
  authHeader = "sso-key %s:%s" %(key, secret)
  headers = {'Authorization':authHeader}
  url = "https://api.godaddy.com/v1/domains/%s/records/A/%s" %(domain,name)
  
  try:
    result = json.loads(requests.get(url, headers=headers, timeout=5).text)
  except requests.exceptions.RequestException as e:
    print e
    exit(1)

  return result[0]["data"]

def set_dnsIP(dnsIP, publicIP, key, secret, domain, name, ttl):
  authHeader = "sso-key %s:%s" %(key, secret)
  headers = {'Content-Type':'application/json', 'Authorization':authHeader }
  payload = json.dumps({'data':publicIP, 'ttl':ttl})
  print "updating A record from %s to %s" %(dnsIP, publicIP)
  url = "https://api.godaddy.com/v1/domains/%s/records/A/%s" %(domain,name)
  try:
    result = requests.put(url, headers=headers, data=payload, timeout=5).text
  except requests.exceptions.RequestException as e:
    print e
    exit(1)

  return result

configData = read_config()
publicIP = get_publicIP()

dnsIP = get_dnsIP(configData["key"], configData["secret"], configData["domain"], configData["name"])

if publicIP != dnsIP:
  print set_dnsIP(dnsIP, publicIP, configData["key"], configData["secret"], configData["domain"], configData["name"], configData["ttl"])
else:
  print "IPs match. Nothing updated."
