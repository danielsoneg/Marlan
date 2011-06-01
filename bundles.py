#!/usr/bin/env python
# encoding: utf-8

import os
import re
import tempfile
import logging
try: import simplejson as json
except ImportError: import json

debug = False
class fakelog(object):
    def info(self,arg): pass
#if not debug: logging = fakelog()

class Bundles(object):
    def __init__(self, client, cypher):
        self.client = client
        self.cypher = cypher
    
    def getPath(self, path):
        """docstring for getPath"""
        path = path.lstrip('/')
        path = "/Public/%s" % path
        #logging.info(path)
        resp = self.client.metadata("dropbox", path)
        logging.info("%s , %s" % (resp.data, resp.status))
        if 'is_dir' in resp.data and resp.data['is_dir']:
            t = 'index'
            ret = self.listDir(resp)
        elif 'error' in resp.data and resp.status == 404:
            t = 'index'
            ret = {'folders':[],'files':[],'images':[],'hasinfo':False,'has_pass':False}
        if path == "/Public/":
            ret['files'] = []
            ret['images'] = []
        return (t, ret)
    
    def writeMetadata(self,path,pw):
        (t, info) = self.getPath(path)
        meta = dropBoxFile(path,self.client,'.metadata')
        info = self.cypher.cryptInfo(pw,info)
        meta.write(info)
        return
    
    def writeContent(self,path,content,pw=False):
        #logging.info("Writing...")
        info = dropBoxFile(path, self.client, 'info.txt')
        status = info.write(content)
        if pw:
            logging.info("Hey, a password! %s" % pw)
            (t, pathInfo) = self.getPath(path)
            meta = dropBoxFile(path,self.client,'.metadata')
            pathInfo = self.cypher.cryptInfo(pw,pathInfo)
            meta.write(pathInfo)
        return status
    
    def getInfo(self, path):
        info = dropBoxFile(path,self.client,'info.txt')
        return info.read()
    
    def listDir(self,resp):
        dirlist = {'folders':[],'files':[],'images':[],'has_info':False,'has_pass':False}
        for item in resp.data['contents']:
            path = item['path']
            path = rePublic.sub('/', path, 1)
            if item['path'].endswith('/info.txt'): dirlist['has_info'] = True
            elif item['path'].endswith('/.metadata'): dirlist['has_pass'] = True
            elif item['is_dir']: dirlist['folders'].append(path)
            elif item['mime_type'].startswith('image/') and not item['path'].lower().endswith('.psd'): dirlist['images'].append(path)
            else: dirlist['files'].append(path)
        return dirlist

class dropBoxFile( object ):
    def __init__(self, path, client, name):
        self.client = client
        self.name = name
        self.dir = '/Public/%s/' % path
        self.path = self.dir + self.name
    
    def read(self):
        self.handle = self.client.get_file("dropbox", self.path)
        self.content = self.handle.read()
        self.handle.close()
        self.__addLinks()
        return self.content
    
    def test(self):
        self.handle = self.client.get_file("dropbox", self.path)
        return dir(self.handle)
    
    def rm(self):
        """Delete the file"""
        self.client.file_delete("dropbox", self.path)
        return self.__success('Deleted %s' % self.path)
    
    def write(self,content):
        self.content = content
        self.__preSave()
        self.__stripLinks()
        self.handle = tempfile.SpooledTemporaryFile()
        self.handle.name = self.name
        self.handle.write(self.content.encode('ascii','replace'))
        self.handle.seek(0)
        #logging.info(self.handle.read())
        #self.handle.seek(0)
        self.client.put_file('dropbox', self.dir, self.handle)
        self.handle.close()
        self.__addLinks()
        return self.__success(self.content)

    def __preSave(self):
        """docstring for _preSave"""
        content = self.content
        content = content.replace('<meta charset="utf-8">','')
        content = content.replace('<br/>', '\n')
        content = content.replace('<div><br>', '\n')
        content = content.replace('<br>', '\n')
        content = content.replace('</div><div>','\n')
        content = content.replace('<div>','\n')
        content = content.replace('</div>','')
        content = reUnspan.sub("\\1", content)
        self.content = content

    # Link Handling
    def __addLinks(self):
        self.content = delinkify(self.content)
        self.content = linkify(self.content)

    def __stripLinks(self):
        self.content = delinkify(self.content)

    def __success(self,message,code={}):
        code['Code'] = 1
        code['Message'] = message
        #logging.info(code)
        return json.dumps(code)
    
def linkify(content):
    content = __linkify_pageLinks(content)
    content = __linkify_webLinks(content)
    return content

def __linkify_pageLinks(content):
    return reLink.sub('<a href="\\1">\\1</a>', content, 0)

def __linkify_webLinks(content):
    return reHref.sub(__linkify_webLinks_fixHref, content, 0)

def __linkify_webLinks_fixHref(link):
    url = link.group(0)
    href = url
    if not url.startswith('http'):
        href = "http://%s" % url
    return '<a href="%s">%s</a>' % (href, url)

def delinkify(content):
    return reUnlink.sub(__delinkify_linkType, content)

def __delinkify_linkType(link):
    if link.group(1).startswith('http'):
        return link.group(2)
    else:
        return "`%s`" % link.group(2)

reLink   = re.compile(r'`(.*?)`', re.U)
reUnlink = re.compile(r'<a href="(.*?)">(.*?)</a>', re.U)
reUnspan = re.compile(r'<span .*?>(.*?)</span>', re.MULTILINE)
reHref   = re.compile(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''', re.U)
rePublic = re.compile(r'\/public\/', re.IGNORECASE)