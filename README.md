# unifs

A proof-of-concept project to mount multiple filesystem in a server-client architecture, with permission and attibute managed by a database system.

#Server side 

## Example

    sqlite> .schema
    CREATE TABLE "extrafs" (
        "Type" TEXT NOT NULL,
        "Name" TEXT NOT NULL,
        "Path" TEXT NOT NULL,
        "MountCmd" TEXT NOT NULL,
        "UmountCmd" TEXT NOT NULL
    );
    CREATE TABLE uc (
        "dPath" TEXT NOT NULL DEFAULT ('/'),
        "idPath" TEXT NOT NULL DEFAULT ('test'),
        "usr" TEXT NOT NULL DEFAULT ('nobody'),
        "grp" TEXT NOT NULL DEFAULT ('nobody'),
        "vFolder" TEXT
    );
    
extrafs table:

    * Type and Name are not used
    * Path correspond to the wished directory name, it will correspond to the idPath in uc table
    * MountCmd and UmountCmd are the mount and unmount commands without the mountdir name (ie: "fusermount -uz ", for 'fusermount -uz test', in case the mountpoint is called 'test')
    
uc table:

    * dPath is the remote path dir
    * idPath should correspond to a Path value in the extrafs table
    * usr and grp are used to identify user
    * vFolder correspond to the local name in the mountpoint directory name (ie: testdir_on_remote_fs)

the database needs to be initialised to work

    sqlite> insert into extrafs values ('ssh','mytest','toto','fuse mount command','fuse unmount command');
    sqlite> select * from extrafs;
    ssh|mytest|toto|fuse mount command|fuse unmount command

    sqlite> insert into uc values ('/','toto','test','test',null);
    sqlite> insert into uc values ('/testdir','toto','test','test','testdir_folder_on_toto');
    sqlite> select * from uc;
    /|toto|test|test|
    /testdir|toto|test|test|testdir_folder_on_toto

place the database on the right place, change the server attribute of bind address and port, database path and the mountpoint empty directory.

run srv.py

#client side

change the user and group attribute and the server's url:port

run ./unifs.py tmp or whatever locale empty mountpoint

#Todo

in the futur, if unifs gains success:

    * secure transport protocol: ssl?
    * identifycation with DIRAC proxy
    * not only folder but also files and its attributes should be registered in the table (ie: timestamp, mode)
    * integrate topological informations to the extrafs to choose the "nearest" server
