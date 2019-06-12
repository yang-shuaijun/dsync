#!/usr/bin/python3

import os
import json
import sys
import fileinput
import subprocess


def confirm_dir(snapDir):
    confirm=input(f"Are you sure you will sync directory from remote server into {snapDir} (y/n):")
    if confirm not in ['y','Y','n','N']:
        confirm_dir(snapDir)
    
    if confirm == 'n' or confirm == 'N':
        sys.exit(-1)

    create_zsync_dir(snapDir)  
    get_fqdn(snapDir) 
    run_zsync(snapDir)

def get_fqdn(snapDir):
    """
    If there isn't fqdn configuration file, we will get the user confirmed 
    server, and then we will put it into json configuration file.
    """
    if os.path.exists(f"{snapDir}/zsync/fqdn.json") == False:
        fqdn_cfg = {}
        fqdn = input("Please enter remote server ip address or FQDN name:")
        fqdn_cfg["server"] = fqdn
        with open(f'{snapDir}/zsync/fqdn.json', 'w') as outfile:  
            json.dump(fqdn_cfg, outfile)

def create_zsync_dir(snapDir):
    if os.path.exists(f"{snapDir}/zsync") == False:
        os.makedirs(f"{snapDir}/zsync")

def run_zsync(snapDir):
    with open(f"{snapDir}/zsync/fqdn.json","r") as inputfile:
        fqdn_cfg = json.load(inputfile)
        gv_fqdn = fqdn_cfg["server"]
    
    os.chdir(snapDir+"/zsync")
    subprocess.check_output(["curl","-O",f"http://{gv_fqdn}/zsync/dsyncfiles.txt"])
    
    with fileinput.input(files=(f'{snapDir}/zsync/dsyncfiles.txt')) as f:
        for item in f:
            print(item)
            relpath=item.replace("\n","").replace(f"http://{gv_fqdn}/zsync/","")
            print(relpath.split("/"))
            relpathlist=relpath.split("/")
            if len(relpathlist) > 1 :
                subdir=snapDir + "/" + "/".join(relpathlist[0:-1])
                if os.path.exists(subdir) == False:
                    os.makedirs(subdir)
                os.chdir(subdir)
                url=item.replace("\n","")
                print(url)
                subprocess.check_output(["/usr/local/bin/zsync",f"{url}"])
            else:
                url=item.replace("\n","")
                print(url)
                os.chdir(snapDir)
                subprocess.check_output(["/usr/local/bin/zsync",f"{url}"])
                  
def main():
    syncdir = sys.argv[1]
    confirm_dir(syncdir)

if __name__ == "__main__":
    main()