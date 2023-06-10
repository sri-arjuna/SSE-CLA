#!/usr/bin/env python3
# SSE CLA - Sephs Skyrim Experimental Crash Log Analyzer
# --------------
# Created: 2023.04.22 by Sephrajin aka sri-arjuna aka (sea)
# Licence: GPLv2
# Source code:      https://github.com/sri-arjuna/SSE-CLA
# Nexus Mod page:   https://www.nexusmods.com/skyrimspecialedition/mods/89860
#
# --------------
#
# In no way I claim this to be either perfect, nor functional, 
# it should only assist you to help getting an indication of what MIGHT be wrong, 
# without any guarantee that this actualy is the cause of the crash.
#
# --------------
#
# TODO
# Precision version
# racemenu version
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
######################################
### Imports
######################################
import os
import re
import random
import logging
######################################
### Initialize Global Variables 
######################################
global thisReport, REPORT, thisLOG, LOG
global thisMEM, thisFile, thisFileAdd, thisAssembler
global script_name, script_version, script_date
global ram_use, ram_avail, ram_free
global list_chance_low, list_chance_high, list_chance_SkyrimAdd
global reasons_low, reasons_high, reasons_Skyrim
global lines_printed
global culprint, indicator
# Save original stdout
original_stdout = sys.stdout
######################################
### Script Variables
######################################
script_name = "CLA SSE - Sephs Skyrim Experimental Crash Log Analyzer"
script_version = "0.6"
script_changed = "2023.05.02"
script_title = script_name+" ("+script_version+") / "+script_changed
######################################
### Lists
### This provides list of known issues
### that are looked for within the logfile
######################################
list_chance_low = ["skse64_loader.exe", "SkyrimSE.exe"]
list_chance_high = ["skee64.dll", "Trishape", "Ninode", "mesh", "hdtSMP64.dll", "cbp.dll", "bad_alloc", "no_alloc", " Dawnguard.esm", " Dragonborn.esm", " Hearthfire.esm", "SchlongsOfSkyrim.dll", "nvwgf2umx.dll", "0x0 on thread " ]
list_chance_SkyrimAdd = ["A0D789", "67B88B", "D6DDDA", "D02C2C", "5999C7", "12FDD00", "7428B1", "D2B923", "12F5590", "132BEF", "C0EB6A", "8BDA97", "5E1F22", "C1315C", "A" ]
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
# Note: DLC.esm's have leading spaces on purpose to avoid false-positives
reasons_high = {
'skee64.dll': "Some mod might be incompatible with RaceMenu, or your body.\n\tYou might want to read: https://www.nexusmods.com/skyrimspecialedition/articles/1372 and/or https://www.nexusmods.com/skyrimspecialedition/mods/44252?tab=description\n\tIf there are any further entries below this, it might be a strong indicator for its cause.",
'Trishape': "Trishapes are related to meshes, specifically a mod supplying a bad mesh. ",
'Ninode': "Ninodes are related to skeletons. Probably an xpmsse overwrite. ",
'Mesh': "Some generic mesh issue, yet to be defined",
'hdtSMP64.dll': "If this appears often, it might indicate a bad config. However, it might also just indicate that there were NPCs around that were wearing hdt/SMP enabled clothing...",
'cbp.dll': "If this appears often, it might indicate a bad config. However, it might also just indicate that there were NPCs around that were wearing SMP/cbp enabled clothing...",
'bad_alloc': "100% your issue! Free RAM, buy more RAM... either way, this IS the cause!",
'no_alloc': "Could not find the proper memory allocation provided by reference",
' Dawnguard.esm': "Your missing the required DLC!",
' Dragonborn.esm': "Your missing the required DLC!",
' Hearthfire.esm': "Your missing the required DLC!",
'SchlongsOfSkyrim.dll': "Don esl'ify any mod that uses Schlongs. Use a previous save and re-schlongify all armors in MCM.",
'nvwgf2umx.dll': "Update your NVidia driver!\nOr your PC is too weak - aka - try fewer / lighter mods.",
'0x0 on thread ': "This actualy is an engine issue of Skyrim, but rare.\nMost often caused by 'Face lighting' / 'Face shadow' issues. Best chance to avoid: Make sure have the newest SSE Engine Fix!\nNow parsing some keywords that might (or not) give some additional indiciation.",

}
# Dialogue - no detailed description, summarizing in if block
reasons_Dialog = {
'Honed Metal': "",
'Your Own Thoughts': "",
'Swift Service': "",
}
# Racemenu
reasons_Racemenu = {
'XPMSEWeaponStyleScaleEffect.psc': "",
'agud_system.psc': "",
'BGSHazard(Name: `Fire`': "",
'XPMSE': "",
'race': "",
'face': "",
} 
# Engine
reasons_Engine = {
'Facelight Plus': "- Try 'no facelight' variant",
'Autoconversation-Illuminate': "- Try 'no facelight' variant for 'Facelight Plus'",
'ShadowSceneNode(Name: `shadow scene node`)': "Unproven, but could indicate cause by combination of multiple lighting mods.",
'BSFadeNode(Name: `skeleton.nif`)': "",
'NiCamera': "Unproven, but could indicate cause by combination of multiple lighting mods.",
}
# Skyrim
reasons_Skyrim = {
'A0D789': "Did you fight a dragon? Did he stomp?\nIf you're using 'Ultimate dragons' there's a fix on its Nexus page.\nIt could also be a DAR issue, please make sure that the animation is not being overwritten.",
'67B88B': "Probably related to: Callstack: 'AnimationGraphManagerHolder'\nFor now, make sure to regenerate animations using FNIS or Nemesis and NEVER delete FNIS.esp, as that file is generated by either of the two.",
'D6DDDA': "Stack: BSResource::anonymous_namespace::LooseFileStream* OR BSResource::ArchiveStream* OR BSResource::CompressedArchiveStream**\nEither you do not have a pagefile that is large enough, or there is an issue with a texture of one of your mods. ",
'D02C2C': "Monster Mod.esp\nNumerous errors and causes of CTD, even with the unoffical patches and latest updates of the mod itself.\nTo keep it short: Do not use.",
'5999C7': "Monster Mod.esp\nNumerous errors and causes of CTD, even with the unoffical patches and latest updates of the mod itself.\nTo keep it short: Do not use.",
'12FDD00': "Probable Callstack: BSShader::unk_xxxxxxx+xx mentioned FIRST or with the HIGHEST PRIORITY\nBroken NIF\nBest apporach, disable some of your NIF mods and figure out which one is causing it by starting a new game to reproduce the error, once figured, report to the mod author so they can create a fix.\nOR, use CAO(Cathedral Assets Optimizer), but that could lead to other issues.. so... its up to you.",
'7428B1': "Install 'SSE Engine Fixes.\nIf you do have that, are you using the'Equipment Durability System mod'?\nIt could be related to an enchanted weapon braking, or other mods that change a character while holding a weapon.",
'D2B923': "Save game issue:\nCould be related to either: Save System Overhaul(SSO) or users of the mod Alternate Start-LAL\nMaybe also related to or fixable by SkyUI SE - Flashing Savegame fix",
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
    return list

# Remove item from a global list
def list_remove(item, list):
    if item in list:
        list.remove(item)

# Print line if not printed yet
def print_line(tLine, printed_lines, prefix=""):
    if tLine not in printed_lines:
        printed_lines.append(tLine)
        print(prefix + tLine)

# Get Crash logs that do not have a report yet.
def get_crash_logs():
    pattern = re.compile(r'crash-.*\.log$')
    patternR = re.compile(r'crash-.*REPORT\.txt$')

    # Use list comprehension to create a list of files that match the pattern
    files = [f for f in os.listdir('.') if os.path.isfile(f) and pattern.search(f)]
    reports = [f for f in os.listdir('.') if os.path.isfile(f) and patternR.search(f)]
    return files   # TODO Remove this when stable
    
    # Remove any log that already has a "-REPORT.txt" file
    for f in files.copy():
        report_file = f.removesuffix(".log") + "-REPORT.txt"
        if report_file in reports:
            print("Skipping: '" + f + "', report exists...")
            files.remove(f)

    return files

# Get occourences
def s_Count(txt,log):
    count = 0
    for line in log:
        if txt in line:
            count += 1
    count = "(count: " + str(count) + ")"
    return count

# Print regular title strings with an underline
def p_title(str):
    print(str)
    print("-" * len(str) + "\n")

# Print regular title strings with an underline
def p_section(str):
    print("\n" + "#" * 80)
    print(str)
    print("#" * 80 + "\n")
        
# This is why!
def s_explain_topic(topic):
    # Check for topic in lists and print the result
    txt = ""
    if topic in list_chance_low:
        txt = reasons_low[topic]
    elif topic in list_chance_high:
        txt = reasons_high[topic]
    else:
        txt = topic+"\t=\tNot handled yet, please report your situation, the crashlog, what happened, and your thoughts to help improve the tool."
    # Final string adjustment
    txt = "\t" + txt + "\n"
    return txt

######################################
### Functions : Print Solutions
######################################
# Print versions of SKSE and Skyrim
def p_solve_GameVer(g_ver, s_ver):
    # SKSE version might be empty...
    if s_ver is None or s_ver == "":
        return "Error: Script Extender version not found.\n"
    # Basic versions
    GameVer_Result = ""
    GameVer_Result += "Game Version:   \t" + str(g_ver) + "\n"
    GameVer_Result += "Script Extender:\t" + str(s_ver) + "\n"

    # Extract major and minor version numbers from game version string
    g_ver_parts = re.findall(r'\d+', g_ver)
    g_ver_major = int(g_ver_parts[0])
    g_ver_minor = int(g_ver_parts[1])

    # Extract major and minor version numbers from script extender version string
    s_ver_parts = s_ver.split('_')
    s_ver_major = int(s_ver_parts[1])
    s_ver_minor = int(s_ver_parts[2])

    # Perform actual version check for possible issues
    if g_ver_major != s_ver_major or g_ver_minor != s_ver_minor:
        GameVer_Result += "\nWarning: Game and Script Extender versions may not be compatible.\n"
    # Return string to print
    return GameVer_Result + "\n"
        
# Print solution to RAM related issues
def p_solve_RAM(ram_use, ram_avail, ram_free):
    str_result = ""
    bol_maybe = 0
    if abs(ram_use - ram_avail) <= 1.5:
        str_result += "RAM (critical):\nThere is a very high chance that the main reason for the crash was lack of free ram: " + str(ram_free)
        bol_maybe = 1
    elif abs(ram_use - ram_avail) <= 2.0:
        str_result += "RAM (maybe, probably not):\nAllthough unlikely, there is a slim chance that the crash might have happend due to lack of free ram: " + str(ram_free)
        bol_maybe = 1
    else:
        str_result += "RAM (all good):\nIt is absolute unlikely that the crash was due to RAM."
    
    if bol_maybe:
        str_result += '''
        
First and foremost, try to close any other application and background processes that might be running that you do not need.
Like, but not limited to, game launchers, web browsers with 20 open tabs, Spotify, even Discord.
Also, you might want to consider using lower texture mods, aka, use a 2k instead of a 4k texture mod, or just a 1k texture.

If the above did not help, you could try apply these config tweaks to: __Skyrim.ini___
Make sure to comment out (#) any existing variantes of these, so you can go back if they dont help or make things worse.

This is most applicable if you're using 4-8 GB ram or less, you game addicted freak! ;) (said the guy who was playing WoW raids at 3 fps).

==================================

[Display]
iTintTextureResolution=2048

[General]
ClearInvalidRegistrations=1

[Memory]
DefaultHeapInitialAllocMB=768
ScrapHeapSizeMB=256
'''
    return str_result

######################################
### Generic User Info
######################################
print("=====================================================================================")
print("THE SCRIPT MUST BE IN THE SAME FOLDER AS YOUR CRASH LOGS, WHICH MUST BE 'crash-*.log'")
print("Usualy this is:          %userprofile%\Documents\My Games\Skyrim Special Edition\SKSE")
print("-------------------------------------------------------------------------------------")
print("If you get an error 'File not found', make sure that have applied the exception for")
print("this script to allow it to have read/write access within this folder.")
print("=====================================================================================")
######################################
### main()
######################################
# Retrieve crash logs that have no report file.
worklist = get_crash_logs()
# Prepare counter for nicer display
work_count = len(worklist)
i = 1
# Crash log writer yet unknown
thisLOGGER = ""
for thisLOG in worklist:
    # Set filename for output
    thisReport = thisLOG.removesuffix(".log")  + '-REPORT.txt'
    # Read the contents of the log file
    with open(thisLOG, 'r', encoding="utf-8", errors="ignore") as LOG:
        DATA = LOG.readlines()
        # Open output stream
        with open(thisReport, "w", encoding="utf-8", errors="ignore") as REPORT:
            # Prepare stdout to be restorable
            sys.stdout = original_stdout
            # Console: Inform user of current file passed
            print(str(i)+"/"+str(work_count)+" Parsing file: " + thisLOG, end='')
            # Print to file
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
            # List: No lines printed yet of this crashlog
            printed = []
            # List: no culprints found yet in this crashlog
            culprint = []
            
            # Basic Header
            p_title(script_title)
            # Just a little READ ME
            print("If you are asking others for assistance / help, ALWAYS provide both files!\n################################################################################\n\n")
            
            # Check for logger:
            print("Crashlog tool/ver:\t",end="")
            if "Skyrim" in str(DATA[0].strip()):
                thisLOGGER = "Crash Logger"
                # Get logger version
                ver_Logger = str(DATA[1].strip())
                print(ver_Logger)
            elif "NetScriptFramework" in str(DATA[2].strip()):
                thisLOGGER = ".NET Script Framework"
                ver_Logger = thisLOGGER+" "+str(DATA[3].split(":")[1])
                print(ver_Logger,end="")
                print("Not yet handled")
                # Not yet handled, will do later
                # Inform user: just skip to keep it short.
                sys.stdout = original_stdout
                i += 1
                print(".....SKIP")
                continue
            else:
                thisLOGGER = "Unknown"
                print(thisLOGGER,end="")
                # End of parsing thisLOG
                print("Can not handle unknown logger")
                sys.stdout = original_stdout
                i += 1
                print(".....SKIP")
                continue  
            
            # Logger specific tasks:
            if thisLOGGER == "Crash Logger":
                # Get SKSE version
                first_pass_str = ''.join(DATA)
                ver_SKSE = re.search("skse.*\.dll", first_pass_str)
                if ver_SKSE:
                    ver_SKSE = ver_SKSE.group(0)
                # Get Skyrim version
                ver_Skyrim = str(DATA[0].strip())
                
                # Check Game vs SKSE versions
                print(p_solve_GameVer(ver_Skyrim, ver_SKSE))
                
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
                    ram_free = round(ram_avail - ram_use, 2)   # abs(ram_avail - ram_use)
                    RAM = "RAM used: \t\t" + str(ram_use) + "\n"
                    RAM += "RAM avail:\t\t" + str(ram_avail) + "\n"
                    RAM += "RAM free: \t\t" + str(ram_free) + "\n"
                else:
                    RAM = "FATAL: \t\t Could not parse RAM values...."
            # Other Logger specific tasks
            elif thisLOGGER == ".NET Script Framework":
                print("TODO: " + thisLOGGER)
            
            # Applies to / Works for all loggers
            # or variables have been prepared.
            
            # Show RAM info
            p_section("RAM:")
            print(RAM)
            print(p_solve_RAM(ram_use, ram_avail, ram_free))
            
            # Start actual parsing...
            for line in DATA:
                if "MODULES:" in line:
                    # Stop parsing (Load Order) to prevent false-positives
                    break
                # for list LOW
                for low in list_chance_low:
                    if low in line:
                        culprint = list_add(low,culprint)
                # for list HIGH
                for high in list_chance_high:
                    if high in line:
                        culprint = list_add(high,culprint)
            
            #  Check for main indicators:
            p_section("Header indicators:") 
            print("Memory:  \t" + thisMEM + " " + s_Count(thisMEM,DATA) )
            print("File:    \t" + thisFile + " " + s_Count(thisFile,DATA) )
            print("Address: \t" + thisFileAdd + " " + s_Count(thisFileAdd,DATA) )
            print("Assemler:\t" + thisAssembler + " " + s_Count(thisAssembler,DATA) )
            
            # Parse for it
            p_title("\nParsing results:")
            for item in thisMEM, thisFile, thisFileAdd, thisAssembler:
                print(item + ":")
                for line in DATA:
                    if "MODULES:" in line:
                        # Stop parsing (Load Order) to prevent false-positives
                        break
                    if item in line:
                        print_line(line.strip(),printed,"\t")
            
            # Generate Summary:
            p_section("Summary:")
            
            # Prints reasons
            for item in culprint:
                # Print 'title' for current item
                print("\n"+item+" "+s_Count(item,DATA))
                # LOW
                if item in list_chance_low:
                    # Show basic reason
                    print(s_explain_topic(item))
                    # Check for more details:
                    if item == "SkyrimSE.exe":
                        for thisAdd in list_chance_SkyrimAdd:
                            str_Add = item+"+"+thisAdd
                            for aLine in DATA:
                                if "Unhandled exception" in line:
                                    # Dont print this line, output is handled already
                                    continue
                                if "MODULES:" in aLine:
                                    # Do not print after MODULES / Loadorder
                                    break
                                if str_Add in aLine:
                                    print("\t-" + str_Add )#+ ":\n")
                                    print("\t\t" + reasons_Skyrim[thisAdd])
                                    print_line(aLine.strip(),printed,"\t\t\t")
                # HIGH
                if item in list_chance_high:
                    print(s_explain_topic(item))
                    if item == "skee64.dll":
                        #print(reasons_high[item])
                        for raceM in reasons_Racemenu:
                            for rLine in DATA:
                                print_line(rLine.strip(),printed,"- ")
                    for aLine in DATA:
                        if "Unhandled exception" in line:
                            # Dont print this line, output is handled already
                            continue
                        if "MODULES:" in aLine:
                            # Do not print after MODULES / Loadorder
                            break
                        if "0x0 on thread " in aLine:
                            # Re-parse all lines for possible facelight indicators
                            for oxLine in DATA:
                                # Yes, this is not the nicest method, but i'm currently not aware of better methods
                                for engR in reasons_Engine:
                                    if engR in oxLine and not lines_printed:
                                        lines_printed = list_add(oxLine,lines_printed)
                                        print(engR + ":\n")
                                        print(reasons_Engine(engR))
                                        print(oxLine)
                                        
                        
                        if item in aLine:
                            print_line(item,printed)
                
            # Additional parse for more
            for line in DATA:
                if "MODULES:" in line:
                    # Do not print after MODULES / Loadorder
                    break
                # Dialog
                for rD in reasons_Dialog:
                    if rD in line and line not in printed:
                        print("Dialogue Mods:\nIf you get more than one entry here, try to figure which one is working best, remove the other ones.\nI mean, come on, why did you even use 2 or more dialogue mods? (if applicable).")
                        print_line(line.strip(),printed)
                # Vamire feed animations
                if "Sacrilege" in line and line not in printed:
                    print("Sacrilege:\nMake sure you have no mods like: Campfire, Honed Metal or Hunterborn born installed. Also, other mods that add/change different kinds of vampire feeding might be the cause for this CTD.")
                    print_line(line.strip(),printed)
                # Cloaks
                if "clothes\\cloaksofskyrim\\" in line:
                    if line not in printed:
                        print("Artesian cloaks of Skyrim:\nMost likely due to HDT enabled capes. Possible fix: Use the according Retexture mod or remove the cape-mod itself.")
                        print_line(line.strip(),printed)
                # Smooth cam
                if "SmoothCam.dll+" in line:
                    if line not in printed:
                        print("Camera:\nIf you get this error more often, try disabling (some of) the compatiblity settings in MCM (trial & error).")
                        print_line(line.strip(),printed)
            
            # End of parsing thisLOG
            sys.stdout = original_stdout
            i += 1
    print(".....DONE")
sys.stdout.close()
os.system("pause")