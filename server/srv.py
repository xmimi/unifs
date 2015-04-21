#!/usr/bin/env python

import sqlite3, os, sys, errno, json, subprocess, time, xmlrpclib, atexit, datetime, stat, re

lhost="192.168.1.90" #listening interface
lport=58000 #listening port
mntpoint="../testdir" #mount point
fcdb="../fc.db" #path of the database

def query(q):
    conn = sqlite3.connect(fcdb)
    conn.row_factory = sqlite3.Row # This enables column access by name: row['column_name'] 
    db = conn.cursor()
    rows = db.execute(q).fetchall()
    conn.commit()
    conn.close()
    return [dict(ix) for ix in rows] #CREATE JSON

def mnt():
    mnts = query('SELECT * FROM extrafs')
    print mnts
    for mntpt in mnts:
        print mntpt['MountCmd']+' '+mntpoint+'/'+mntpt['Path']
        try: 
            os.makedirs(mntpoint+'/'+mntpt['Path'])
            subprocess.call(mntpt['MountCmd']+' '+mntpoint+'/'+mntpt['Path'],shell=True)
        except: raise

class unifs:
    def __init__(self):
        self.fh={}
        self.dirtyfile=[]
        #self.user = 'wusuowei'
        self.user = 'xli'

    def which(self, p,u,g):
        q=[]
        print p,u,g
        if p.split(os.path.sep)[1] in self.xtrafolder(u,g):
            q = query("SELECT * FROM uc WHERE usr = '%s' AND grp = '%s' AND vFolder = '%s'"%(u,g,p.split(os.path.sep)[1]))
        else:
            q = query("SELECT * FROM uc WHERE usr = '%s' AND grp = '%s' AND vFolder is NULL"%(u,g))
        if len(q) > 0:
            q=q[0] #define the best one
            print q
            if q['vFolder']:
                p = re.sub(r'^\/'+q['vFolder'], '', p)
            print p
            realpath = mntpoint+'/'+q['idPath']+q['dPath']+p
            print 'realpath',realpath
            return realpath
        else:
            print '-----empty query-----'
            return None

    def xtrafolder(self,u,g):
        extrapath=query("SELECT vFolder FROM uc WHERE usr = '%s' AND grp = '%s'"%(u,g))
        extrapath=[x['vFolder'] for x in extrapath if x['vFolder']]
        return extrapath

    #def parse(self,p,u,g):
        

    def unigetattr(self, path, u, g):
        print '-----getting attr-----', path
        if path[1:] in self.xtrafolder(u,g):
            return {"st_mode":(stat.S_IFDIR | 0755),"st_ino":0,"st_dev":0,"st_nlink":1, "st_uid":os.geteuid(), "st_gid":os.getegid(), "st_atime":0, "st_mtime":0, "st_ctime":0, "st_size":4096}
        p = self.which(path,u,g)
        if p:
            try:
                res = os.stat(p)
                if res:
                    ret = {"st_mode":res.st_mode,"st_ino":res.st_ino,"st_dev":res.st_dev,"st_nlink":res.st_nlink, "st_uid":res.st_uid, "st_gid":res.st_gid, "st_atime":res.st_atime, "st_mtime":res.st_mtime, "st_ctime":res.st_ctime, "st_size":res.st_size}
                    return ret
                else:
                    return -errno.ENOENT 
            except:
                print path, "doesn't exists"
                #print Exception
        else:
            return -errno.ENOSYS
    
    def unilistdir(self, path,u, g):
        print '-----listing dir-----', path
        p = self.which(path,u,g)
        if p:
            try:
                d = os.listdir(p)
                if path=='/':
                    d.extend(self.xtrafolder(u,g))
                print d
                return d
            except:
                pass
        else:
            return -errno.ENOENT

    def unichmod(self, path, mode,u,g):
        print '-----chmoding-----', path, mode
        p = self.which(path,u,g)
        if p:
            return os.chmod(p, mode)
        else:
            return -errno.ENOENT

    def unichown(self, path, uid, gid,u,g):
        print '-----chowning-----', path, uid, gid
        p = self.which(path,u,g)
        if p:
            return os.chown(p, uid, gid)
        else:
            return -errno.ENOENT

    def unicreate(self, path, flags, mode,u,g):
        print '-----creating-----', path, flags, mode
        p = self.which(path,u,g)
        if p:
            self.fh[path,u,g] = open(p, 'w+b')
            self.fh[path,u,g].close()
            os.chmod(p, mode)
            del self.fh[path,u,g]
            return 0
        else:
            return -errno.ENOENT
            
    def uniopen(self, path, flags,u,g):
        print '-----opening-----', path, flags
        p = self.which(path,u,g)
        if p:
            try:
                self.fh[path,u,g] = open(p, 'rb+') #ab+?
            except Exception as e:
                print e
            #print self.fh
            return 0
        else:
            return -errno.ENOENT

    def uniread(self, path, length, offset,u,g):
        print '-----reading-----', path, length, offset
        p = self.which(path,u,g)
        if p:
            try:
                if not (path,u,g) in self.fh or self.fh[path,u,g].closed:
                    self.fh[path,u,g] = open(p, 'rb+') #ab+?
                #print path, self.fh[path,self.user]
                self.fh[path,u,g].seek(offset)
                d = self.fh[path,u,g].read(length)
                self.fh[path,u,g].close()
                return xmlrpclib.Binary(d)
            except:
                print Exception
            #print self.fh
        else:
            return -errno.ENOENT

    def unirelease(self, path, flags,u,g):
        print '-----releasing-----',path, flags
        try:
            if (path,u,g) in self.fh:
                self.fh[path,u,g].close()
                del self.fh[path,u,g]
            print 'gnignia', self.fh
        except:
            print Exception
        return

    def unimkdir(self, path, mode,u,g):
        p = self.which(path,u,g)
        if p:
            try:
                print 'mkdir', path
                return os.mkdir(p)
            except:
                pass
        else:
            return -errno.ENOENT

    def unirmdir(self, path,u,g):
        p = self.which(path,u,g)
        if p:
            return os.rmdir(p)
        else:
            return -errno.ENOENT

    def unitruncate(self, path, size,u,g):
        p = self.which(path,u,g)
        if p:
            try:
                if not (path,u,g) in self.fh or self.fh[path,u,g].closed:
                    self.fh[path,u,g] = open(p, 'ab+')
                self.fh[path,u,g].seek(0)
                self.fh[path,u,g].truncate(size)
                self.fh[path,u,g].close()
                return
            except:
                print Exception
        else:
            return -errno.ENOENT


    def uniunlink(self, path,u,g):
        print '-----unlink-----', path
        p = self.which(path,u,g)
        if p:
            return os.unlink(p)
        else:
            return -errno.ENOENT

    def uniwrite(self, path, buf, offset,u,g):
        print '-----write-----', path, buf, offset
        p = self.which(path, u,g)
        if p:
            try:
                if not (path,u,g) in self.fh or self.fh[path,u,g].closed:
                    self.fh[path,u,g] = open(p, 'ab+')
                self.fh[path,u,g].seek(offset)
                self.fh[path,u,g].write(buf.data)
                self.fh[path,u,g].close()
                return len(buf.data)
            except:
                print Exception
        else:
            return -errno.ENOENT

    def uniutime(self, path, times,u,g):
        p = self.which(path,u,g)
        if not len(q)==0:
            try:
                os.utime(p, times)
            except:
                print Exception
        else:
            return -errno.ENOENT

    def unirename(self, old, new,u,g):
        po = self.which(old,u,g) #new
        pn = self.which(new,u,g)
        if po:
            try:
                return os.renames(po, pn) #rename() respond successful but does nothing
            except:
                print Exception
        else:
            return -errno.ENOENT

def loop():
    from SimpleXMLRPCServer import SimpleXMLRPCServer
    server = SimpleXMLRPCServer((lhost, lport), logRequests=True, allow_none=True)
    #server.register_introspection_functions()
    print "Listening on port ",lport,"for the interface ",lhost,"..."
    #server.register_function(parse)
    server.register_instance(unifs())
    try:
        print 'Use Control-C to exit'
        server.serve_forever()
    except KeyboardInterrupt:
        print 'Exiting'

@atexit.register
def umnt():
    print "unmounting extrafs, please wait..."
    mnts = query('SELECT * FROM extrafs')
    for mntpt in mnts:
        print mntpt['UmountCmd']+' '+mntpoint+'/'+mntpt['Path']
        try:
            subprocess.call(mntpt['UmountCmd']+' '+mntpoint+'/'+mntpt['Path'],shell=True)
            time.sleep(2)
            os.rmdir(mntpoint+'/'+mntpt['Path'])
        except: raise

mnt()
loop()
