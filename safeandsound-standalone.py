#!/usr/bin/env python
import configparser
import errno
import glob
import gnupg
import os
import shutil
import sys
import tarfile
import time

from distutils.dir_util import copy_tree
from subprocess import Popen

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

def main():
    config_filename = 'backup.cfg'
    if len(sys.argv) > 1:
        config_filename =  sys.argv[1]
    
    # Read in variables from configuration file
    config = configparser.ConfigParser()
    config.read(config_filename)
    backup_root_directory = config.get('settings', 'backup_root_directory')
    scp_users = config.get('settings', 'scp_users').split(',')
    directories_to_backup = config.get('settings', 'directories_to_backup').split(',') 
    tar_gpg_passphrase = config.get('settings', 'tar_gpg_passphrase').split(',') 
    dump_gpg_passphrase = config.get('settings', 'dump_gpg_passphrase').split(',') 
    encrypt_dump = config.getboolean('settings', 'encrypt_dump')
    encrypt_tar = config.getboolean('settings', 'encrypt_tar')
    encrypt_mode_dump = config.get('settings', 'encryption_mode_dump')
    encrypt_mode_tar = config.get('settings', 'encryption_mode_tar')
    gpg_recipients = config.get('settings', 'gpg_recipients').split(',')

    scp_directories = ["/home/" + x for x in scp_users]
    scp_directory_dict =  dict(zip(scp_users, scp_directories))

    backup_sub_directory = str(int(time.time()))  
    backup_directory = os.path.join(backup_root_directory,backup_sub_directory)
    backup_directory_slash = os.path.join(backup_root_directory,backup_sub_directory + os.sep)
    tar_filename = backup_sub_directory.rstrip(os.sep) + ".tar.gz"
    tar_filepath = os.path.join(backup_root_directory, tar_filename)

    gpg = gnupg.GPG()
     
    # Create backup directory
    make_sure_path_exists(backup_directory)
    
    # Copy files into directory
    for directory in directories_to_backup:
       directory_suffix =  os.path.basename(os.path.normpath(directory)) 
       copy_tree(directory,os.path.join(backup_directory_slash,directory_suffix),preserve_symlinks=1)
    
    # Database dump 
    #os.system("mysqldump --all-databases > " + backup_directory_slash + "dump-$(date +%Y-%m-%d_%H-%M-%S).sql")
    mysqldump_process = Popen('mysqldump --all-databases > ' + backup_directory_slash + 'dump-$(date +%Y-%m-%d_%H-%M-%S).sql', shell=True)
    mysqldump_process.wait()
    dump_filename = glob.glob(os.path.join(backup_directory_slash,'dump-*.sql'))
    dump_gpg_filename = ""
 
    # Encrypt dump with gnupg
    if encrypt_dump:
        dump_gpg_filename = dump_filename[0]  + ".gpg"
        dump_file = open(dump_filename[0], "rb")
        if encrypt_mode_dump == "symmetric":
            gpg.encrypt_file(dump_file, recipients=None, symmetric='AES256', passphrase=dump_gpg_passphrase, armor=False, output=dump_gpg_filename)
        else:
            gpg.encrypt_file(dump_file, recipients=gpg_recipients, passphrase=dump_gpg_passphrase, armor=False, output=dump_gpg_filename)
        os.remove(dump_filename[0])

    # History 
    #os.system("history > " + backup_directory + "history")
    shutil.copy("/root/.bash_history", os.path.join(backup_directory_slash,"history"))
    
    # Make tarball
    #os.system("tar -czv " + backup_directory  + "-f " + tar_filepath)
    make_tarfile(tar_filepath,backup_directory)
    
    # Remove backup directory  
    #os.system("rm -rf " + backup_directory)
    shutil.rmtree(backup_directory)
    
    filename = tar_filepath
  
    # Encrypt tar with gnupg
    if encrypt_tar:
        tar_gpg_filename = tar_filepath + ".gpg"
        tar_file = open(tar_filepath, "rb")
        if encrypt_mode_tar == "symmetric":
            gpg.encrypt_file(tar_file,  recipients=None, symmetric='AES256', passphrase=tar_gpg_passphrase, armor=False,output=tar_gpg_filename)
        else:
            gpg.encrypt_file(tar_file, recipients=gpg_recipients, passphrase=tar_gpg_passphrase, armor=False,output=tar_gpg_filename)
        os.remove(tar_filepath)
        filename = tar_gpg_filepath
 
    #os.system("cp " + gpg_file + " " + scp_directory) 
    for user in scp_directory_dict:
        directory = scp_directory_dict[user] 
    	
        # Copy to scp directory 
        shutil.copy(filepath,directory)
 
        # Adjust permissions
        filename = os.path.basename(filepath)
        #os.system("chown " + user + ":" + user + " " + directory + "/" + filename)
        shutil.chown(os.path.join(directory,os.sep,filename),user=user,group=user)

if __name__ == '__main__':
    main()
