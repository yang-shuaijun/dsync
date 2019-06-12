#!/usr/bin/python3
import os
import json
import sys
import fileinput
import subprocess
import re

def confirm_dir(snapDir):
    confirm=input(f"Are you sure you will sync {snapDir} to remote(y/n):")
    if confirm not in ['y','Y','n','N']:
        confirm_dir(snapDir)
    
    if confirm == 'n' or confirm == 'N':
        sys.exit(-1)

    create_zsync_dir(snapDir)  
    get_fqdn(snapDir) 
    generate_dir_zsync(snapDir)

def get_fqdn(snapDir):
    """
    If there isn't fqdn configuration file, we will get the user confirmed 
    server, and then we will put it into json configuration file.
    """
    if os.path.exists(f"{snapDir}/zsync/fqdn.json") == False:
        fqdn_cfg = {}
        fqdn = input("Please enter yourself web server ip address or FQDN name:")
        fqdn_cfg["server"] = fqdn
        with open(f'{snapDir}/zsync/fqdn.json', 'w') as outfile:  
            json.dump(fqdn_cfg, outfile)

        
def create_zsync_dir(snapDir):
    if os.path.exists(f"{snapDir}/zsync") == False:
        os.makedirs(f"{snapDir}/zsync")
        
def generate_dir_zsync(snapDir):
    """
    Generate the file zsync metadata information without the prefix dir.
    """
    with open(f"{snapDir}/zsync/fqdn.json","r") as inputfile:
        fqdn_cfg = json.load(inputfile)
        gv_fqdn = fqdn_cfg["server"]
         
    prefix_url = "http://"+gv_fqdn
    
    with open(f"{snapDir}/zsync/allfiles.txt","w") as outfile:
        for dirpath, dirname, fileList in os.walk(snapDir,topdown=True):
            if re.search(f"zsync",dirpath):
                pass
            else:
                for file in fileList:
                    fileurl = dirpath + "," + file + "\n"
                    print(fileurl)
                    outfile.write(fileurl)
    
    # Generate the zsync file according to the allfiles.txt
    print("This is going to take a long time.")
    with open(f"{snapDir}/zsync/dsyncfiles.txt","w") as outfile:
       with fileinput.input(files=(f'{snapDir}/zsync/allfiles.txt')) as f:
           for item in f:
                url = prefix_url + item.replace("\n","").replace("," , "/").replace(snapDir,"")
                orgfile=item.replace("\n","").replace("," , "/")
                print(url)
                print(orgfile)
                os.chdir(snapDir+"/zsync")
                relDir=item.split(",")[0].replace(snapDir,"").replace("/","",1)
                #print(relDir)
                if relDir != "":
                    if os.path.exists(snapDir + "/zsync/" + relDir) == False:
                        os.makedirs(snapDir + "/zsync/" + relDir)
                    zsyncfile = snapDir + "/zsync/" + relDir + "/" + item.replace("\n","").split(",")[1] + ".zsync"
                else:
                     zsyncfile = snapDir + "/zsync/" + item.replace("\n","").split(",")[1] + ".zsync"
                print(zsyncfile)
                subprocess.check_output(["/usr/local/bin/zsyncmake", "-b 4096", f"-o{zsyncfile}", f"-u{url}", orgfile])
                url_zsync = prefix_url + zsyncfile.replace(snapDir,"")
                outfile.write(url_zsync+"\n")

def main():
    syncdir = sys.argv[1]
    confirm_dir(syncdir)

if __name__ == "__main__":
    main()