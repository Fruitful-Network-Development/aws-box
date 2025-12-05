# Ops notes and environment snapshots

## Home directory snapshot (reference)
```
admin@ip-172-31-30-106:~$ ls -la
total 84
drwx------ 7 admin admin  4096 Dec  3 21:35 .
drwxr-xr-x 3 root  root   4096 Nov 20 15:30 ..
-rw------- 1 admin admin 34335 Dec  4 05:27 .bash_history
-rw-r--r-- 1 admin admin   220 Jul 30 19:28 .bash_logout
-rw-r--r-- 1 admin admin  3578 Nov 27 20:26 .bashrc
drwxrwxr-x 5 admin admin  4096 Nov 28 21:20 .cache
-rw------- 1 admin admin    20 Nov 30 00:03 .lesshst
drwxrwxr-x 3 admin admin  4096 Nov 27 19:34 .local
drwx------ 3 admin admin  4096 Nov 28 21:54 .pki
-rw-r--r-- 1 admin admin   807 Jul 30 19:28 .profile
drwx------ 2 admin admin  4096 Nov 26 00:39 .ssh
-rw-r--r-- 1 admin admin     0 Nov 20 15:45 .sudo_as_admin_successful
drwxrwxr-x 6 admin admin  4096 Dec  4 01:12 awsDev
```

## Repo snapshot (reference)
```
admin@ip-172-31-30-106:~/awsDev$ ls -la
total 32
drwxrwxr-x 6 admin admin 4096 Dec  4 01:12 .
drwx------ 7 admin admin 4096 Dec  3 21:35 ..
drwxrwxr-x 8 admin admin 4096 Dec  4 05:26 .git
-rw-rw-r-- 1 admin admin 6004 Dec  4 01:12 README.md
drwxrwxr-x 3 admin admin 4096 Dec  3 21:35 etc
drwxrwxr-x 2 admin admin 4096 Dec  4 02:33 scripts
drwxrwxr-x 3 admin admin 4096 Dec  3 21:35 srv
```

These snapshots are informational only and may drift over time; verify on the target host before acting on them.
