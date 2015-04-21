#! /usr/bin/env python
#
# Copyright (C) 2014  Xiabo LI
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
########################################################################
  
import stat, time, random, errno, os, fuse, xmlrpclib

  
class UniFS(fuse.Fuse):
    def __init__(self, *args, **kw):
	fuse.fuse_python_api = (0, 2)
        fuse.Fuse.__init__(self, *args, **kw)
        self.SE = "DIRAC-USER"
        self.file={}
        #getid from dproxy
        self.usr='test'
        self.grp='test'
        self.result = None
	self.proxy = 'http://192.168.1.90:58000' #host:port of the server

    def getproxy(self):
        #return self.p
        return xmlrpclib.ServerProxy(self.proxy, allow_none=True)

    def getattr(self, path):
        print '*** getattr', path
        #path = path.decode('utf_8')
	self.result = self.getproxy().unigetattr(path, self.usr, self.grp)
	#print self.result, self.getproxy()
	st = fuse.Stat()
	if self.result:
	    st.st_mode = self.result['st_mode']
	    st.st_ino = self.result['st_ino']
      	    st.st_dev = self.result['st_dev']
      	    st.st_nlink = self.result['st_nlink']
      	    st.st_uid = os.getuid() #if md['Owner']==self.result['Owner'] else 65534
      	    st.st_gid = os.getgid() #if md['OwnerGroup']==self.result['Group'] else 65534
      	    st.st_size = self.result['st_size']
      	    st.st_atime = self.result['st_atime']#time.mktime(datetime.datetime.strptime(self.result['atime'],'%Y-%m-%dT%H:%M:%S.%f').timetuple())
      	    st.st_mtime = self.result['st_mtime']#time.mktime(datetime.datetime.strptime(self.result['mtime'],'%Y-%m-%dT%H:%M:%S.%f').timetuple())
            st.st_ctime = self.result['st_ctime']#time.mktime(datetime.datetime.strptime(self.result['ctime'],'%Y-%m-%dT%H:%M:%S.%f').timetuple())
            return st
	else :
            return -errno.ENOENT

    def readdir(self, path, offset):
        print '*** readdir', path, offset
        #path = path.decode('utf_8')
        dirents = [ '.', '..']
	self.result = self.getproxy().unilistdir(path,self.usr, self.grp)
	if self.result:
	    dirents.extend(x for x in self.result)
            print dirents
            for r in dirents:
                yield fuse.Direntry(r.encode('utf_8', 'replace'))

    def getdir(self, path):
        print '*** getdir', path
        return -errno.ENOSYS

    def mythread ( self ):
        print '*** mythread'
        return -errno.ENOSYS

    def chmod ( self, path, mode ):
        print '*** chmod', path, oct(mode)
        #return self.getproxy().unichmod(path, mode, self.usr,self.grp)
        return -errno.ENOSYS

    def chown ( self, path, uid, gid ):
        print '*** chown', path, uid, gid
        #return self.getproxy().unichown(path, uid, gid, self.usr, self.grp)
        return -errno.ENOSYS

    def fsync ( self, path, isFsyncFile ):
        print '*** fsync', path, isFsyncFile
        return -errno.ENOSYS

    def link ( self, targetPath, linkPath ):
        print '*** link', targetPath, linkPath
        return -errno.ENOSYS

    def mkdir ( self, path, mode):
        print '*** mkdir', path, oct(mode)
        return self.getproxy().unimkdir(path, mode, self.usr, self.grp) 

    def mknod ( self, path, mode, dev ):
        print '*** mknod', path, oct(mode), dev
        return -errno.ENOSYS

    def create (self, path, flags, mode):
        print '*** create', path, flags, oct(mode)
        self.getproxy().unicreate(path, flags, mode, self.usr, self.grp)
	return 0

    def open ( self, path, flags ):
        print '*** open', path, flags
        return self.getproxy().uniopen(path, flags, self.usr, self.grp)
        #return -errno.ENOSYS

    def read ( self, path, length, offset ):
        print '*** read', path, length, offset
        return self.getproxy().uniread(path, length, offset, self.usr, self.grp).data

    def readlink ( self, path ):
        print '*** readlink', path
        return -errno.ENOSYS

    def release ( self, path, flags ):
        print '*** release', path, flags
        return self.getproxy().unirelease(path, flags, self.usr, self.grp)
        #return -errno.ENOSYS

    def rename ( self, oldPath, newPath ):
        print '*** rename', oldPath, newPath
        return self.getproxy().unirename(oldPath, newPath, self.usr, self.grp)
        #return -errno.ENOSYS

    def rmdir ( self, path ):
        print '*** rmdir', path
        self.getproxy().unirmdir(path, self.usr, self.grp)
        return 0

    def statfs ( self ):
        print '*** statfs'
        return -errno.ENOSYS

    def symlink ( self, targetPath, linkPath ):
        print '*** symlink', targetPath, linkPath
        return -errno.ENOSYS

    def truncate ( self, path, size ):
        print '*** truncate', path, size
        return self.getproxy().unitruncate(path,size, self.usr, self.grp)

    def unlink ( self, path ):
        print '*** unlink', path
        return self.getproxy().uniunlink(path, self.usr, self.grp)

    def utime ( self, path, times ):
        print '*** utime', path, times
        return self.getproxy().uniutime(path, times, self.usr, self.grp)
        #return -errno.ENOSYS

    def write ( self, path, buf, offset ):
        print '*** write', path, buf, offset
        return self.getproxy().uniwrite(path, xmlrpclib.Binary(buf), offset, self.usr, self.grp)

    #def access(self, path, mode):
    #    if not os.access(path, mode):
    #        return -errno.EACCES

def main():
    usage="""
        UniFS: A filesystem to allow viewing dirac cloud's extra filesystem in an uniform unix filesystem.
    """ + fuse.Fuse.fusage
    server = UniFS(version="%prog " + fuse.__version__,
                    usage=usage, dash_s_do='setsingle')
    server.parser.add_option(mountopt="SE", metavar="Storage Element ID", default="DIRAC-USER", help="specify the used storage element [default: %default]")
    server.parse(values = server,errex=1)
    server.main()

if __name__ == '__main__':
    main()
