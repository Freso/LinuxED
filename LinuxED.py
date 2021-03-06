#!/usr/bin/env python3

# -*- coding: utf-8 -*-

# written by Creatable

# credits:
# - Tcll5850: https://gitlab.com/Tcll
#   for cleaning up the code, making it more maintainable, and extending it's functionality, as well as fixing issues with older python versions.

import os
import sys
import urllib.request
import zipfile
import distutils.core
import shutil
import getpass

"""Comment out old Windows notice
if os.name == 'nt': print('WARNING: it appears you are running the Linux installer on Windows.\n'
                          'If you are unaware of what you\'re doing, it\'s recommended you close this installer.\n'
                          'Otherwise you may continue at your own risk.\n')"""

if os.name == 'nt': print('WARNING: it appears you are running LinuxED on Windows.\n'
                          'LinuxED was not originally made for Windows and Windows compatibility is not maintained.\n'
                          'Continue at your own risk.')
# Define the starting variables, these are all their own thing.
username = getpass.getuser()
dirpath = os.path.realpath('')
filepath = os.path.dirname(os.path.realpath(__file__))

if os.name == 'nt':
    enhanceddir = dirpath + "\\EnhancedDiscord"
    injdir = 'process.env.injDir = "%s"' % enhanceddir.encode('unicode_escape').decode("utf-8")
else:
    enhanceddir = dirpath + "/EnhancedDiscord"
    injdir = 'process.env.injDir = "%s"' % enhanceddir

# this is not my code but it's what I put at the end of index.js
patch = """%s
require(`${process.env.injDir}/injection.js`);
module.exports = require('./core.asar');"""%injdir

detect_versions = lambda discordpath,idxsubpath: [
    (discordpath+vsn+idxsubpath, vsn) for vsn in (os.listdir(discordpath) if os.path.exists(discordpath) else []) if os.path.isdir(discordpath+vsn) and len(vsn.split('.')) == 3 ]

print('Welcome to the LinuxED installation script.')

# TODO: detect patched clients
if sys.platform == 'darwin':
    baseclients = {
    "STABLE" : detect_versions('/Users/%s/Library/Application Support/discord/'%username, '/modules/discord_desktop_core/index.js'),
    "CANARY" : detect_versions('/Users/%s/Library/Application Support/discordcanary/'%username, '/modules/discord_desktop_core/index.js'),
    "PTB"    : detect_versions('/Users/%s/Library/Application Support/discordptb/'%username, '/modules/discord_desktop_core/index.js'),
    "SNAP"   : detect_versions('/home/%s/snap/discord/82/.config/discord/'%username, '/modules/discord_desktop_core/index.js'),
    "FLATPAK": detect_versions('/home/%s/.var/app/com.discordapp.Discord/config/discord/'%username, '/modules/discord_desktop_core/index.js')
}
elif os.name == 'nt':
    baseclients = {
        "STABLE" : detect_versions('C:/Users/%s/AppData/Roaming/Discord/'%username, '/modules/discord_desktop_core/index.js'),
        "CANARY" : detect_versions('C:/Users/%s/AppData/Roaming/Discord Canary/'%username, '/modules/discord_desktop_core/index.js'),
        "PTB"    : detect_versions('C:/Users/%s/AppData/Roaming/Discord PTB/'%username, '/modules/discord_desktop_core/index.js'),
        "SNAP"   : detect_versions('/home/%s/snap/discord/82/.config/discord/'%username, '/modules/discord_desktop_core/index.js'),
        "FLATPAK": detect_versions('/home/%s/.var/app/com.discordapp.Discord/config/discord/'%username, '/modules/discord_desktop_core/index.js')
    }
else:
    baseclients = {
        "STABLE" : detect_versions('/home/%s/.config/discord/'%username, '/modules/discord_desktop_core/index.js'),
        "CANARY" : detect_versions('/home/%s/.config/discordcanary/'%username, '/modules/discord_desktop_core/index.js'),
        "PTB"    : detect_versions('/home/%s/.config/discordptb/'%username, '/modules/discord_desktop_core/index.js'),
        "SNAP"   : detect_versions('/home/%s/snap/discord/82/.config/discord/'%username, '/modules/discord_desktop_core/index.js'),
        "FLATPAK": detect_versions('/home/%s/.var/app/com.discordapp.Discord/config/discord/'%username, '/modules/discord_desktop_core/index.js')
    }

clients = [ (str(i+1),cpv) for i,cpv in enumerate( (c,p,v) for c in [ "STABLE", "CANARY", "PTB", "SNAP", "FLATPAK" ] if baseclients[c] for p,v in baseclients[c] ) ]
clients.append( (str(len(clients)+1), ("CUSTOM",'', '')) )
getclient = dict(clients).get

def validate_custom_client():
    while True:
        print("\nPlease enter the location of your client's index.js file.")
        jspath = input('> ')
        if os.path.exists(jspath): return 'CUSTOM', jspath, '' # TODO: can we detect the version of a custom client?
        elif not jspath:
            print("\nOperation cancelled...")
            return 'CUSTOM', jspath, ''
        else:
            print("\nError: The specified location was not valid.")
            print("Please enter a valid location or press Enter to cancel.")

def select_client(allow_custom=False):
    if len(clients) > 2 or allow_custom:
        while True:
            print('\nPlease enter the number for the client you wish to patch, or press Enter to exit:')
            result = input('%s\n> '%('\n'.join('%s. %s: %s'%(i,o,v) for i,(o,p,v) in clients)) )
            client, jspath, version = getclient( result, (None,'','') )
            if client=='CUSTOM':
                client, jspath, version = validate_custom_client()
                if not jspath: continue
            if jspath: return client, jspath, version
            if not result:
                print("\nOperation cancelled...")
                #input('Press Enter to Exit...')
                return 'CUSTOM', jspath, ''
            print("\nError: The specified option was not valid.")
    
    elif len(clients) == 1:
        print('\nThe installer could not detect any known Discord clients.')
        print('Do you have Discord installed in a custom location? (y/n)')
        if input("> ").upper() in {"Y","YES"}: return validate_custom_client()
        else:
            print('\nNo Discord client could be found.')
            print('Please install Discord and re-run this installer.')
            #input('Press Enter to Exit...')
            return 'CUSTOM', '', ''
    
    else: return getclient('1')

client, jspath, version = select_client()
if jspath:
    print('\nOperating on client: %s %s\n'%(client,version))
    print('Please type the number for your desired option:')
    
    # room for expansion (other params can be provided here)
    options = [ (str(i+1),o) for i,o in enumerate([
        ('Install ED',),
        ('Uninstall ED',),
        ('Update ED',),
        ('Update LinuxED',),
        ('Select Client',),
        ('Exit',),
    ])]
    getoption = dict(options).get
    
    while True:
        option,*params = getoption( input( '%s\n> '%('\n'.join('%s. %s'%(i,o) for i,(o,*p) in options) ) ), (None,) )
        print()
        
        if option == 'Exit':
            print("Exiting...")
            exit()
            break # shouldn't get here, but just in case.
        
        
        elif option == 'Update LinuxED':
            print("Updating LinuxED...")
            urllib.request.urlretrieve('https://github.com/Cr3atable/LinuxED/archive/master.zip', '%s/LinuxEDUpdate.zip' % filepath)
            with zipfile.ZipFile("%s/LinuxEDUpdate.zip" % filepath,"r") as zip_ref:
                zip_ref.extractall(filepath)
            os.remove("%s/LinuxED-master/LICENSE" % filepath)
            os.remove("%s/LinuxED-master/README.md" % filepath)
            os.remove("%s/LinuxED-master/.gitignore" % filepath)
            distutils.dir_util.copy_tree('%s/LinuxED-master/' % filepath, filepath)
            shutil.rmtree("%s/LinuxED-master" % filepath)
            os.remove("%s/LinuxEDUpdate.zip" % filepath)
            print("Update complete!")
    
    
        elif option == 'Uninstall ED':
            print('Uninstalling EnhancedDiscord...')
            if os.path.exists("%s.backup"%jspath):
                os.remove(jspath)
                os.rename("%s.backup"%jspath, jspath)
                print("Successfully uninstalled EnhancedDiscord!")
            else:
                print("Error: Couldn't find index.js backup, did you use the installer to install ED?\n")
    
        elif option == 'Install ED':
            if os.path.exists("%s.backup"%jspath):
                print('Uninstalling EnhancedDiscord...')
                os.remove(jspath)
                os.rename("%s.backup"%jspath, jspath)
                print("Successfully uninstalled EnhancedDiscord!")

            if not os.path.exists(enhanceddir):
                print("Downloading ED...")
                urllib.request.urlretrieve('https://github.com/joe27g/EnhancedDiscord/archive/master.zip', 'EnhancedDiscord.zip')
                with zipfile.ZipFile("EnhancedDiscord.zip","r") as zip_ref:
                    zip_ref.extractall(".")
                os.rename("EnhancedDiscord-master", "EnhancedDiscord")
                os.remove("EnhancedDiscord.zip")
            
            backuppath = "%s.backup"%jspath
            if not os.path.exists(backuppath):
                print("Creating index.js.backup...")
                with open(jspath,'r') as original:
                    with open(backuppath,'w') as backup: backup.write(original.read())
    
            print("Patching index.js...")
            with open(jspath,"w") as idx: idx.write(patch)

            cfgpath = "%s/config.json"%enhanceddir
            if not os.path.exists(cfgpath):
                print("Creating config.json...")
                with open(cfgpath,"w") as cfg: cfg.write("{}")
        
            print("EnhancedDiscord installation complete!\n")

        elif option == 'Update ED':
            if os.path.exists(enhanceddir):
                print("Updating ED...")
                urllib.request.urlretrieve('https://github.com/joe27g/EnhancedDiscord/archive/master.zip', 'EDUpdate.zip')
                with zipfile.ZipFile("EDUpdate.zip","r") as zip_ref:
                    zip_ref.extractall(".")
                distutils.dir_util.copy_tree('./EnhancedDiscord-master', './EnhancedDiscord')
                shutil.rmtree("EnhancedDiscord-master")
                os.remove("EDUpdate.zip")
                print("Update complete!")
            else:
                print("It seems EnhancedDiscord is not installed in the current directory so it was unable to be updated.")
        elif option == 'Select Client':
            print("Selecting new Discord client...")
            backup = (client, jspath, version)
            client, jspath, version = select_client(True)
            if not jspath: client, jspath, version = backup
            print('\nOperating on client: %s %s\n'%(client,version))

        else:
            print('Error: The specified option was not valid.\n')

        print('Please type the number for your desired option:')
