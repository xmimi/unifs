# unifs

A proof-of-concept project to mount multiple filesystem in a server-client, with permission and attibute managed by a database system.

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

    sqlite> insert into extrafs values ('ssh','mytest','toto','fuse mount command','fuse unmount command');
    sqlite> select * from extrafs;
    ssh|mytest|toto|fuse mount command|fuse unmount command

    sqlite> insert into uc values ('/','toto','test','test',null);
    sqlite> insert into uc values ('/testdir','toto','test','test','testdir_folder_on_toto');
    sqlite> select * from uc;
    /|toto|test|test|
    /testdir|toto|test|test|testdir_folder_on_toto

place the database on the right place, change the server attribute of bind address and port and database path.

run srv.py

#client side

change the user and group attribute and the server's url:port
run ./unifs.py tmp or whatever locale mountpoint