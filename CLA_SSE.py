#!/usr/bin/env python3
# SSE CLA - Sephs Skyrim Experimental Crash Log Analyzer
# 2023.04.22 by Sephrajin aka sri-arjuna aka (sea)
# Source code:      https://github.com/sri-arjuna/SSE-CLA
# Nexus Mod page:   https://www.nexusmods.com/skyrimspecialedition/mods/89860
# --------------
#
# This should work on Windows and *nix systems as well.
#
# --------------
#
# Most simple, just drag and drop the crashlog onto the script
# or exectue the script and drag and drop the file onto the open console window
#
# Then follow the menu instructions
#
# --------------
#
# In no way I claim this to be either perfect, nor functional, 
# it should only assist you to help getting an indication of what MIGHT be wrong, 
# without any guarantee that this actualy is the cause of the crash.
#
# --------------
#
# Syntax for functions:
#   s_  Returns a string
#   f_  Works with a file
#   p_  Prints a string/variable to screen/console
#   
######################################
### Python Version Check
######################################
import sys
if sys.version_info < (3, 3):
    print("This script requires Python 3.3 or higher.")
    print("Please download and install it from https://www.python.org/downloads/")
    sys.exit(1)
#import subprocess
# Check if contextlib2 package is installed
#try:
#    import contextlib2
#except ImportError:
#    print("contextlib2 package not found, installing...")
    # Install the package using pip
#    subprocess.check_call(['python', '-m', 'pip', 'install', 'contextlib2'])
######################################
### Imports
######################################
import os
import re
#import os.path
#import datetime
#import time
#import platform
import random
import logging
#import fnmatch
#from contextlib import redirect_stdout #, tee
#from contextlib2 import tee
######################################
### Initialize Global Variables 
######################################
global thisReport, REPORT, thisLOG, LOG
global thisMEM, thisFile, thisFileAdd, thisAssembler
global script_name, script_version, script_date
global ram_use, ram_avail, ram_free
global list_chance_low, list_chance_high
global hc_reasons, ignore_reasons
global culprint
# Save original stdout
original_stdout = sys.stdout
######################################
### Script Variables
######################################
script_name = "CLA SSE - Sephs Skyrim Experimental Crash Log Analyzer"
script_version = "0.3"
script_changed = "2023.04.24"
script_title = script_name+" ("+script_version+") / "+script_changed
######################################
### Lists
### This provides list that are looked for within the logfile
######################################
list_chance_low = ["skse64_loader.exe", "SkyrimSE.exe"]
list_chance_high = ["skee64.dll", "Trishape", "Ninode", "mesh", "hdtSMP64.dll", "cbp.dll", "bad_alloc", "no_alloc", "Dawnguard.esm", "Dragonborn.esm", "Hearthfire.esm" ]
list_chance_SkyrimAdd = ["A0D789", "67B88B", "D6DDDA", "D02C2C", "5999C7", "12FDD00", "7428B1", "D2B923", "12F5590", "132BEF", "C0EB6A", "8BDA97", "5E1F22", "C1315C", "A" ]
culprint = []
######################################
### Dictionary
### Provide the item of a list to get an according response.
######################################
# Low
reasons_low = {
'skse64_loader.exe': "At best, this entry is an indication that the culprint is a mod that is using SKSE...",
'SkyrimSE.exe': "This file on its own is not the cause, however, we'll do further parsing..."
}
# High
reasons_high = {
'skee64.dll': "Some mod might be incompatible with RaceMenu, or your body.",
'Trishape': "Trishapes are related to meshes, specifically a mod supplying a bad mesh. ",
'Ninode': "Ninodes are related to skeletons. Probably an xpmsse overwrite. ",
'Mesh': "Some generic mesh issue, yet to be defined",
'hdtSMP64.dll': "If this appears often, it might indicate a bad config. However, it might also just indicate that there were NPCs around that were wearing hdt/smp enabled clothing...",
'cbp.dll': "If this appears often, it might indicate a bad config. However, it might also just indicate that there were NPCs around that were wearing hdt/smp/sbp enabled clothing...",
'bad_alloc': "100% your issue! Free RAM, buy more RAM... either way, this IS the cause!",
'no_alloc': "Could not find the proper memory allocation provided by reference",
'Dawnguard.esm': "Your missing the required DLC!",
'Dragonborn.esm': "Your missing the required DLC!",
'Hearthfire.esm': "Your missing the required DLC!",
}
reasons_Skyrim = {
'A0D789': "Did you fight a dragon? Did he stomp?\nIf you're using 'Ultimate dragons' there's a fix on its Nexus page.\nIt could also be a DAR issue, please make sure that the animation is not being overwritten.",
'67B88B': "Probably related to: Callstack: 'AnimationGraphManagerHolder'\nFor now, make sure to regenerate animations using FNIS or Nemesis and NEVER delete FNIS.esp, as that file is generated by either of the two.",
'D6DDDA': "Stack: BSResource::anonymous_namespace::LooseFileStream* OR BSResource::ArchiveStream* OR BSResource::CompressedArchiveStream**\nEither you do not have a pagefile that is large enough, or there is an issue with a texture of one of your mods. ",
'D02C2C': "Monster Mod.esp\nNumerous errors and causes of CTD, even with the unoffical patches and latest updates of the mod itself.\nTo keep it short: Do not use.",
'5999C7': "Monster Mod.esp\nNumerous errors and causes of CTD, even with the unoffical patches and latest updates of the mod itself.\nTo keep it short: Do not use.",
'12FDD00': "Probable Callstack: BSShader::unk_xxxxxxx+xx mentioned FIRST or with the HIGHEST PRIORITY\nBroken NIF\nBest apporach, disable some of your NIF mods and figure out which one is causing it by starting a new game to reproduce the error, once figured, report to the mod author so they can create a fix.\nOR, use CAO(Cathedral Assets Optimizer), but that could lead to other issues.. so... its up to you.",
'7428B1': "Install 'SSE Engine Fixes.\nIf you do have that, are you using the'Equipment Durability System mod'?\nIt could be related to an enchanted weapon braking, or other mods that change a character while holding a weapon.",
'D2B923': "Save game issue:\nCould be related to either: Save System Overhaul(SSO) or users of the mod Alternate Start-LAL\nMaybe also related to or fixable by SkyUI SE - Flasching Savegame fix",
'12F5590': "Facegen issue:\nRegenerate the Face in CK, search for 'BSDynamicTriShape' as a hint, or check the  HDT-SMP log for the last NPC used.",
'132BEF': "Head Mesh Issue:\nCheck the HDT-SMP log where the last NPC most probably could be the issue.\nIf you use 'Ordinary Women', make sure that mod gets loaded last among mods that change body/heads.",
'C0EB6A': "Actualy an issue of SkyrimSE.exe:\nShould be fix-able by the use of 'SSE Engine Fixes' mod",
'8BDA97': "This could be an issue of having both, 'SSE Engine Fixes' and 'SSE Display Tweaks' mods active.\nCheck their settings and/or disable one or the other to see if you get another crash - or avoid this from now on.",
'5E1F22': "Missing Master (esm):\nGet/fix your mod list in order... dammit!\nEither mod manager should have warned you about this issue!",
'C1315C': "controlmap.txt...What have you done?!\nProbably some mod that uses hotkeys might have modified this file... good luck with the hunt!",
'A': "(probably:) Animation Issue:\nNo further information available"
}

######################################
### Functions : Tools
######################################
# Add item to a list.
def list_add(item, list):
    if item not in list:
        list.append(item)

# Remove item from a global list
def list_remove(item, list):
    if item in list:
        list.remove(item)

# Get Crash logs that do not have a report yet.
def get_crash_logs():
    pattern = re.compile(r'crash-.*\.log$')

    # Use list comprehension to create a list of files that match the pattern
    files = [f for f in os.listdir('.') if os.path.isfile(f) and pattern.search(f)]

    # Remove any corresponding "-REPORT.txt" files
    for f in files.copy():
        report_file = f.removesuffix(".log") + "-REPORT.txt"
        if report_file in files:
            print("Skipping: '" + f + "', report exists...")
            files.remove(f)

    return files

# Print regular title strings with an underline
def p_title(str):
        print(str)
        print("-" * len(str) + "\n")
        
# This is why!
def s_explain_topic(topic):
    if topic in list_chance_low:
        str = reason_low[topic]
    elif topic in list_chance_high:
        str = reason_high[topic]
    else:
        str = topic+"\t=\tNot handled yet, please report your situation, the crashlog, what happened, and your thoughts to help improve the tool."
    
    return str+"\n\n"

######################################
### Functions : Print Solutions
######################################
# Print solution to SKSE and Skyrim related issues
def p_solve_GameVer(g_ver, s_ver):
    # Print versions:
    GameVer_Result = ""
    GameVer_Result += "Game:\t\t\t" + g_ver + "\n"
    GameVer_Result += "Script Extender:\t" + s_ver + "\n"

    # Extract major and minor version numbers from game version string
    g_ver_parts = re.findall(r'\d+', g_ver)
    g_ver_major = int(g_ver_parts[0])
    g_ver_minor = int(g_ver_parts[1])

    # Extract major and minor version numbers from script extender version string
    s_ver_parts = s_ver.split('_')
    s_ver_major = int(s_ver_parts[1])
    s_ver_minor = int(s_ver_parts[2])

    # Perform actual version check
    if g_ver_major != s_ver_major or g_ver_minor != s_ver_minor:
        GameVer_Result += "\nWarning: Game and Script Extender versions may not be compatible.\n"
    # Return string to print
    return GameVer_Result + "\n"
        
# Print solution to RAM related issues
def p_solve_RAM():
    global ram_use, ram_avail, ram_free
    str_result = ""
    bol_maybe = 0
    if abs(ram_use - ram_avail) <= 1.5:
        str_result += "RAM (critical):\nThere is a very high chance that the main reason for the crash was lack of free ram: " + str(ram_free) + "\n"
        bol_maybe = 1
    elif abs(ram_use - ram_avail) <= 2.0:
        str_result += "RAM (maybe, probably not):\nAllthough unlikely, there is a slim chance that the crash might have happend due to lack of free ram: " + str(ram_free) + "\n"
        bol_maybe = 1
    else:
        str_result += "RAM (all good):\nIt is absolute unlikely that the crash was due to RAM.\n"
    
    if bol_maybe:
        str_result += '''
First and foremost, try to close any other application and background processes that might be running that you do not need.
Like, but not limited to, game launchers, web browsers with 20 open tabs, Spotify, even Discord.
Also, you might want to consider using lower texture mods, aka, use a 2k instead of a 4k texture mod, or just a 1k texture.

If the above did not help, you could try apply these config tweaks to: __Skyrim.ini___
Make sure to comment out (#) any existing variantes of these, so you can go back if they dont help or make things worse.

This is most applicable if you're using 4-8 GB ram (or less, you game addicted freak, said the guy who was playing WoW raids at 3 fps).

===============================================

[Display]
iTintTextureResolution=2048

[General]
ClearInvalidRegistrations=1

[Memory]
DefaultHeapInitialAllocMB=768
ScrapHeapSizeMB=256

===============================================
'''
    return str_result

######################################
### Generic User Info
######################################
print("=====================================================================================")
print("THE SCRIPT MUST BE IN THE SAME FOLDER AS YOUR CRASH LOGS, WHICH MUST BE 'crash-*.log'")
print("Usualy this is:          %userprofile%\Documents\My Games\Skyrim Special Edition\SKSE")
print("=====================================================================================")
######################################
### main()
######################################
# Retrieve crash logs that have no report file.
worklist = get_crash_logs()
work_count = len(worklist)
i = 1

# Tried:
# abspath / normpath(abspath) // os.path.normpath(os.path.abspath(thisReport))
# r"{}"  rf"{}"
# thisDIR = os.getcwd() // os.path.join(thisDIR, thisReport)

for thisLOG in worklist:
    # Set filename for output
    thisReport = thisLOG.removesuffix(".log")  + '-REPORT.txt'
    # Read the contents of the log file
    with open(thisLOG, 'r', encoding="utf-8", errors="ignore") as LOG:
        DATA = LOG.readlines()
        # Open output stream
        with open(thisReport, "w", encoding="utf-8", errors="ignore") as REPORT:
            # Open for both, stdout and file output
            sys.stdout = original_stdout
            print(str(i)+"/"+str(work_count)+" Parsing file: " + thisLOG, end='')
            sys.stdout = REPORT
            # Clear variable / Set Defaults
            thisMEM = ""
            thisFile = ""
            thisFileAdd = ""
            thisAssembler = ""
            RAM = ""
            ram_use = ""
            ram_avail = ""
            ram_free = ""
            
            # Basic Header
            p_title(script_title)
            
            # Get SKSE version
            first_pass_str = ''.join(DATA)
            ver_SKSE = re.search("skse.*\.dll", first_pass_str)
            if ver_SKSE:
                ver_SKSE = ver_SKSE.group(0)
            # Get Skyrim version
            ver_Skyrim = str(DATA[0].strip())
            
            # Check Game vs SKSE versions
            print(p_solve_GameVer(ver_Skyrim, ver_SKSE))
            # Get logger version
            ver_Logger = str(DATA[1].strip())
            
            # Unhandled Exception
            line_Unhandled = str(DATA[3].strip())
            parts = line_Unhandled.split(" at ")
            subparts = parts[1].split(" ")
            thisMEM = subparts[0]
            thisFile = subparts[1].split('+')[0]
            thisFileAdd = subparts[1].split("+")[1][:6]
            thisAssembler = parts[1].split("\t")[1]
            
            # Retrieve Memory info
            line_RAM = str(DATA[10].strip())
            match = re.search(r'PHYSICAL MEMORY: (\d+\.\d+) GB/(\d+\.\d+) GB', line_RAM)
            if match:
                ram_use = float(match.group(1))
                ram_avail = float(match.group(2))
                ram_free = abs(ram_avail - ram_use)
                RAM = "RAM used: \t\t" + str(ram_use) + "\n"
                RAM += "RAM available:\t\t" + str(ram_avail) + "\n"
                RAM += "RAM free: \t\t" + str(ram_free) + "\n"
            else:
                RAM = "FATAL: \t\t Could not parse RAM values...."
            
            # Show RAM info
            p_title("RAM")
            print(RAM)
            print(p_solve_RAM())
            
            # Start actual parsing... : LOW
            for line in DATA:
                for low in list_chance_low:
                    if low in line:
                        list_add(low,culprint)
            
            # Start actual parsing... : HIGH
            for line in DATA:
                for low in list_chance_low:
                    if low in line:
                        list_add(low,culprint)
            
            # Generate Summary:
            p_title("Summary")         
            
            # Prints reasons for : LOW
            for item in culprint:
                list_remove(item,culprint)
                print(item)
                print(reasons_low[item]+"\n")
                if item == "SkyrimSE.exe":
                    for thisAdd in list_chance_SkyrimAdd:
                        str_Add = str(item.strip)+"+"+thisAdd
                        for aLine in DATA:
                            if str_Add in aLine:
                                print(thisAdd+":\n")
                                print(reasons_Skyrim[thisAdd]+"\n")
            
            # Print current culprints:
            print("----------------------------\n\nRemaining culprints:\n\t"+str(culprint))
            
            # End of parsing thisLOG
            sys.stdout = original_stdout
            i += 1
    print(".....DONE")
        

sys.stdout.close()
os.system("pause")