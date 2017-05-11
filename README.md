# safeandsound
Backup script

This is a backup script written in Python 3, maybe it will become something fancy one day.
Currently it was written because I didn't want to use a shell script for taking a backup even if that shell script 
was to drive duplicity or some other existing backup software solution.

It is configurable using configparser fileformat http://docs.python.jp/3/library/configparser.html
See backup.cfg-sample for a sample configuration

Currently the standalone version only takes one optional argument which is a path to the configuration, if this is not specified then uses backup.cfg in the same directory
as the script.

Currently it supports 
* Making base backups of a given list of directories
* Making a MySQL database dump of all databases
* Saving the root users bash history
* Making a gzipped tarball
* GPG symmetric encryption of the MySQL database dump 
* GPG symmetric encryption of the tarball 
* GPG asymmetric encryption of the MySQL database dump
* GPG asymmetric encryption of the tarball
* Copying the backup to a given user directory in order for it to be pulled to a remote server

It probably needs more features, more error handling, more documentation, etc, Patches and pull requests are welcome.

Possible future functionality
* Actually interacting with / delegating to other backup software (duplicity, barman, Amanda, rsync,etc)
* Incremental backups
* Pull and push distribution of backups.


Current dependencies are
* mysqldump needs to be configured in order to run using a predefined password in its configuration file
* python-gnupg for encryption

Using GPG Asymmetric encryption

encryption_mode_dump or encryption_mode_tar need to be asymmetric
gpg_recipients needs to a comma separated list of emails,  public keys for the recipients must exist in the keyring identified in gnupghome.
