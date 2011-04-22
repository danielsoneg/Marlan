#!/usr/bin/env python
# encoding: utf-8

import os
import re
import tempfile
import logging
try: import simplejson as json
except ImportError: import json

class Bundles(object):
    def __init__(self, client):
        self.client = client
    
    def getPath(self, path):
        """docstring for getPath"""
        path.lstrip('/')
        path = "/Public/%s" % path
        logging.info(path)
        resp = self.client.metadata("dropbox", path)
        logging.info("%s , %s" % (resp.data, resp.status))
        if 'is_dir' in resp.data and resp.data['is_dir']:
            t = 'index'
            ret = self.listDir(resp)
        elif 'error' in resp.data and resp.status == 404:
            t = 'index'
            ret = {'folders':[],'files':[],'images':[],'hasinfo':False}
        return (t, ret)
    
    def writeMetadata(self,path,info):
        meta = dropBoxFile(path,self.client,'.metadata')
        meta.write(json.dumps(info))
    
    def writeContent(self,path,content):
        info = dropBoxFile(path, self.client, 'info.txt')
        return info.write(content)
    
    def getInfo(self, path):
        info = dropBoxFile(path,self.client,'info.txt')
        return info.read()
    
    def listDir(self,resp):
        dirlist = {'folders':[],'files':[],'images':[],'has_info':False}
        for item in resp.data['contents']:
            if item['path'].endswith('/info.txt'): dirlist['has_info'] = True
            elif item['is_dir']: dirlist['folders'].append(item['path'])
            elif item['mime_type'].startswith('image/'): dirlist['images'].append(item['path'])
            else: dirlist['files'].append(item['path'])
        return dirlist

def addLinks(content):
    dummy = dropBoxFile('a',False,'b')
    return dummy.addLinks(content)

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
    
    def addLinks(self, content):
        '''The Max Power way'''
        self.content = content
        self.__addLinks()
        return self.content
    
    def test(self):
        self.handle = self.client.get_file("dropbox", self.path)
        return dir(self.handle)

    def write(self,content):
        self.content = content
        self.__preSave()
        self.__stripLinks()
        self.handle = tempfile.SpooledTemporaryFile()
        self.handle.name = self.name
        self.handle.write(self.content.encode('ascii','replace'))
        self.handle.seek(0)
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
        self.__stripLinks()
        self.__webLinks()
        self.__pageLinks()

    def __stripLinks(self):
        self.content = reUnlink.sub(self.__stripLinks_linkType, self.content)

    def __stripLinks_linkType(self, link):
        if link.group(1).startswith('http'):
            return link.group(2)
        else:
            return "`%s`" % link.group(2)

    def __pageLinks(self):
        self.content = reLink.sub('<a href="\\1">\\1</a>', self.content,0)

    def __webLinks(self):
        self.content = reHref.sub(self.__webLinks_fixHref, self.content, 0)

    def __webLinks_fixHref(self, link):
        url = link.group(0)
        href = url
        if not url.startswith('http'):
            href = "http://%s" % url
        return '<a href="%s">%s</a>' % (href, url)


    def __success(self,message,code={}):
        code['Code'] = 1
        code['Message'] = message
        return json.dumps(code)



reLink   = re.compile(r'`(.*?)`', re.U)
reUnlink = re.compile(r'<a href="(.*?)">(.*?)</a>', re.U)
reUnspan = re.compile(r'<span .*?>(.*?)</span>', re.MULTILINE)
reHref   = re.compile(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''', re.U)
