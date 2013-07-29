#!/usr/bin/env python
# vim: set ts=4 sw=4 tw=4 syntax=python ai et :

'''
Module to provide salt the ability to control lxc containers

'''


import subprocess
import logging
from pprint import pprint
import re

# Import salt libs
#import salt.utils

log = logging.getLogger(__name__)

badchars = re.compile(r"""[/;:%^$#@!`'"*()\\]""")



def _checkForBadCharacters(cmd):
    for entry in cmd:
        if badchars.search(entry):
            return (True,entry)
    return False


def _runCommand(cmd):
    result = subprocess.Popen(cmd,stdout=subprocess.PIPE).communicate()[0]
    return result


def getContainerList():
    cmd = "/usr/bin/lxc-ls"
    result = _runCommand([cmd])
    return result

def getContainerProcessList(container,psargs=None):
    if not container in getContainerList():
        return { 'status':'error', 'message':'No such container {}'.format(container) }
    cmd = ["/usr/bin/lxc-ps", "-n", container]
    if psargs:
        isBad = _checkForBadCharacters([psargs])
        if isBad:
            return {'error':"{} has unacceptable characters in it".format(isBad[1]) }
        cmd.append("--")
        cmd.append(psargs)
    results = _runCommand(cmd).splitlines()
    fields = results[0].split()
    records=[]
    for line in results:
        data = dict( zip(fields, line.split(None,len(fields)-1) ) )
        records.append( data )
    return records

def getAllContainerProcessList(psargs=None):
    cmd = ["/usr/bin/lxc-ps", '--lxc']
    if psargs:
        isBad = _checkForBadCharacters([psargs])
        if isBad:
            return {'error':"{} has unacceptable characters in it".format(isBad[1]) }
        cmd.append("--")
        cmd.append(psargs)

    raw = _runCommand(cmd)
    results = raw.splitlines()
    fields = results[0].split()
    records=[]
    for line in results[1:]:
        data = dict( zip(fields, line.split(None,len(fields)-1) ) )
        records.append( data )
    return records

def getContainerInfo(container):
    cmd = ["lxc-info","-n",container]
    result = _runCommand(cmd)
    infodata = {}
    for line in result.splitlines():
        key,value = line.split(":")
        value=value.strip()
        infodata[key]=value
    return infodata

def startContainer(container):
    cmd = ["lxc-start","-d","-n",container]
    if container not in getContainerList():
        return { 'status':'error', 'message':'No such container {}'.format(container) }
    if getContainerInfo(container)['state'] != "STOPPED":
        return { 'status':'error', 'message':'container {} is not stopped'.format(container) }

    result = _runCommand(cmd)
    return getContainerInfo(container)

def stopContainer(container):
    cmd = ["lxc-stop","-n",container]
    if container not in getContainerList():
        return { 'status':'error', 'message':'No such container {}'.format(container) }
    if getContainerInfo(container)['state'] != "RUNNING":
        return { 'status':'error', 'message':'container {} is not running'.format(container) }

    result = _runCommand(cmd)
    return getContainerInfo(container)

def createContainer(name,template,disksize,backingstore="lvm",vgname="containers"):
    allowed_templates = ('debian-wheezy',)
    vgname = 'containers'

    if name in getContainerList():
        return (False,"{} already exists".format(name) )

    if template not in allowed_templates:
        return {'error':'"{}" is not an allowed template'.format(template) }

    if not disksize.isalnum():
        return {'error':'"{}" has disallowed characters'.format(disksize) }

    cmd = ["lxc-create", "-t", template, "--fssize", disksize, '--vgname',vgname, '-B',backingstore,'-n',name]
    isBad= _checkForBadCharacters(cmd)
    if isBad:
        return {'error':"{} has unacceptable characters in it".format(isBad[1]) }

    results = _runCommand(cmd)
    if "'{}' created".format(name) in results:
        return (True,results)
    else:
        return (False,results)

def deleteContainer(container,StopIfRunning=False):
    if getContainerInfo(container)['state'] == 'RUNNING':
        if StopIfRunning:
            stopContainer(container)
        else:
            return { 'error':"{} is running, you must stop it first".format(container) }
    cmd = ['lxc-destroy','-n',container]
    result = _runCommand(cmd)
    return result
