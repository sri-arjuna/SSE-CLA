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
global reasons_Chance, reasons_Skyrim
global lines_printed
global culprint, indicator
global iCulprintCount, iCulprintSolved
# Save original stdout
original_stdout = sys.stdout
######################################
### Script Variables
######################################
script_name = "CLA SSE - Sephs Skyrim Experimental Crash Log Analyzer"
script_version = "0.9"
script_changed = "2023.06.22"
script_title = script_name+" ("+script_version+") / "+script_changed
######################################
### Dictionary
### Provide the item of a list to get an according response.
######################################
# Reason
# Note: DLC.esm's have leading spaces on purpose to avoid false-positives
reasons_Chance = {
'skse64_loader.exe': "At best, this entry is an indication that the culprint is a mod that is using SKSE...",
'SkyrimSE.exe': "This file on its own is not the cause, however, we'll do further parsing...",
'skse64_loader.exe': "At best, this entry is an indication that the culprint is a mod that is using SKSE...",
'SkyrimSE.exe': "This file on its own is not the cause, however, we'll do further parsing...",
'SkyrimVR.exe': "This file on its own is not the cause, however, we'll do further parsing...",
'skee64.dll': "Some mod might be incompatible with RaceMenu, or your body.\n\tYou might want to read:\n\t -  https://www.nexusmods.com/skyrimspecialedition/articles/1372 \n\t - https://www.nexusmods.com/skyrimspecialedition/mods/44252?tab=description\n\tIf there are any further entries below this, it might be a strong indicator for its cause.\n\tAlso, please make sure to have this installed:\n\t- Race Compatibility: https://www.nexusmods.com/skyrimspecialedition/mods/2853",
'Trishape': "Trishapes are related to meshes, specifically a mod supplying a bad mesh. ",
'NiNode': "Ninodes are related to skeletons. It could be a wrong loadorder for skeleton based mods.\n\tIf you use HDT/SMP, make sure to load it like: Body (CBBE or BH/UNP) -> FNIS/Nemesis -> DAR -> HDT -> XP32\n\tAlso make sure that you've chosen the HDT/SMP variant of xpmsse.\n\tIf you find a mod name in the following list, try disabling it and rerurn FNIS or Nemesis.",
'mesh': "Some generic mesh issue, yet to be defined...\n\tIf there are any 'indent' lines, they might give a more precice of what _could_ be the reason.\n\t-- This is beta detection, and might not be accurate --\n\t-- This is showing previous lines 1 & 2, and is considered WIP --",
'hdtSMP64.dll': "If this appears often, it might indicate a bad config (rare). However, it might also just indicate that there were NPCs around that were wearing hdt/SMP enabled clothing...\n\tPlease increase the log level for hdtsmp64 (if you have not done so yet) and check its content.\n\tMake sure to have Faster HDT-SMP that suits your Skyrim Version:\n\t- https://www.nexusmods.com/skyrimspecialedition/mods/57339 \n\tAlso make sure you have these installed:\n\t- SMP NPC fix: https://www.nexusmods.com/skyrimspecialedition/mods/91616 ",
'cbp.dll': "If this appears often, it might indicate a bad config (rare). However, it might also just indicate that there were NPCs around that were wearing SMP/cbp enabled clothing...\n\tMake sure to have this installed:\n\t\n\t- SMP NPC fix: https://www.nexusmods.com/skyrimspecialedition/mods/91616 ",
'bad_alloc': "100% your issue! Free RAM, buy more RAM or increase the swap-file (pagefile)... either way, this IS the cause!\n\tTry this:\n\t\t- https://learn.microsoft.com/en-us/sharepoint/technical-reference/the-paging-file-size-should-exceed-the-amount-of-physical-ram-in-the-system",
'no_alloc': "Could not find the proper memory allocation provided by reference\n\tIf this happens often, you might want to run a 'MemCheck' to check your RAM for faulty hardware.",
#' Dawnguard.esm': "Your missing the required DLC!\n\tThis might be a false-positive, or not... Needs further investigation!",
#' Dragonborn.esm': "Your missing the required DLC!\n\tThis might be a false-positive, or not... Needs further investigation!",
#' Hearthfire.esm': "Your missing the required DLC!\n\tThis might be a false-positive, or not... Needs further investigation!",
'SchlongsOfSkyrim.dll': "Dont esl'ify any mod that uses Schlongs. Use a previous save and re-schlongify all armors in MCM.",
'nvwgf2umx.dll': "Update your NVidia driver!\n\tOr your PC is too weak - aka - try fewer / lighter mods.",
'0x0 on thread ': "This actualy is an engine issue of Skyrim, but rare.\nMost often caused by 'Face lighting' / 'Face shadow' issues. Best chance to avoid: Make sure have the newest SSE Engine Fix!\nNow parsing some keywords that might (or not) give some additional indiciation.",
'HUD': "There seems to be an issue with your HUD / UI.\n\tNordic UI using the TDM patch might be the cause (at the very least in combination with Skyrim Souls).\n\tIf that is not what you are using, please figure out a fix and send me your crashlog and solution.",
'tbbmalloc.dll': "Threading Building Blocks Memory Allocator\n\tThis is either part of:\n\t- the CreationKit Fixes: https://www.nexusmods.com/skyrimspecialedition/mods/20061 \n\t- the Engine Fixes (part 2): https://www.nexusmods.com/skyrimspecialedition/mods/17230 \n\n\tMake sure to disable: SrtCrashFix64.dll (Animation Limit Crash fix SSE) as this is handled by the Engines Fixes, which is recomended to use!\n\tEither way, make sure to have the 'latest' version variant for your Skyrim edition.\n\tHowever, this probably is not the cause, but the causing mod relies on excessive memory handling.",
'DynamicCollisionAdjustment.dll': "General statement, this one is incompatible with the PLANCK for VR.\n\tWhile the name is tempting and promising, bug reports since october 2022 seems to be left untouched by the mod author.\n\tPlease check your issue with the bugs listed there:\n\t- https://www.nexusmods.com/skyrimspecialedition/mods/76783?tab=bugs\n\n\t",
'Modified by': "These are only listed as additional hints for probably debugging. If you have no other indicators, this might be worth investigating. \n\tIf you do have other indicators, try to solve those first!\n\tThat said, it is common to have 2-4 mods listed in a row, however, \n\tlists of 5 or more _might_ cause issuses by the sheer amount of what possibly could be overwritten several times.",
'lanterns\lantern.dds': "If you are using: 'Lanterns of Skyrim II' and 'JK Skyrim' do not install the 'No Lights Patch' since LoS II patch is meant to be used without it.",
}
# Dialogue - no detailed description, summarizing in if block
reasons_Dialog = {
'Honed Metal': "todo",
'Your Own Thoughts': "todo",
'Swift Service': "todo",
}
# Racemenu
reasons_Racemenu = {
'XPMSEWeaponStyleScaleEffect.psc': "todo",
'agud_system.psc': "todo",
'BGSHazard(Name: `Fire`': "todo BGSHazard",
'XPMSE': "todo XPMSE",
'race': "todo race",
'face': "todo face",
} 
# Engine
reasons_Engine = {
'Facelight Plus': "- Try 'no facelight' variant",
'Autoconversation-Illuminate': "- Try 'no facelight' variant for 'Facelight Plus'",
'ShadowSceneNode(Name: `shadow scene node`)': "Unproven, but could indicate cause by combination of multiple lighting mods.",
'BSFadeNode(Name: `skeleton.nif`)': "",
'NiCamera': "Unproven, but could indicate cause by combination of multiple lighting mods.",
}
# Skyrim SE
reasons_Skyrim = {
'0CB748E': "Have you closed Skyrim 'from the outside' aka with Taskmanager? -- Verification appreciated.",
'12FDD00': "Probable Callstack: BSShader::unk_xxxxxxx+xx mentioned FIRST or with the HIGHEST PRIORITY\nBroken NIF\nBest apporach, disable some of your NIF mods and figure out which one is causing it by starting a new game to reproduce the error, once figured, report to the mod author so they can create a fix.\nOR, use CAO(Cathedral Assets Optimizer), but that could lead to other issues.. so... its up to you.",
'12F5590': "Facegen issue:\nRegenerate the Face in CK, search for 'BSDynamicTriShape' as a hint, or check the  HDT-SMP log for the last NPC used. You might need to increase the log level if you havent dont so already.",
'132BEF': "Head Mesh Issue:\nCheck the HDT-SMP log where the last NPC most probably could be the issue.\nIf you use 'Ordinary Women', make sure that mod gets loaded last among mods that change body/heads.",
'5999C7': "Monster Mod.esp\nNumerous errors and causes of CTD, even with the unoffical patches and latest updates of the mod itself.\nTo keep it short: Do not use.",
'5E1F22': "Missing Master (esm):\nGet/fix your mod list in order... dammit!\nEither mod manager should have warned you about this issue!",
'67B88B': "Probably related to: Callstack: 'AnimationGraphManagerHolder'\nFor now, make sure to regenerate animations using FNIS or Nemesis and NEVER delete FNIS.esp, as that file is generated by either of the two.",
'7428B1': "Install 'SSE Engine Fixes.\nIf you do have that, are you using the'Equipment Durability System mod'?\nIt could be related to an enchanted weapon braking, or other mods that change a character while holding a weapon.",
'8BDA97': "This could be an issue of having both, 'SSE Engine Fixes' and 'SSE Display Tweaks' mods active.\nCheck their settings and/or disable one or the other to see if you get another crash - or avoid this from now on.",
'A': "(probably:) Animation Issue:\nNo further information available",
'A0D789': "Did you fight a dragon? Did he stomp?\nIf you're using 'Ultimate dragons' there's a fix on its Nexus page.\nIt could also be a DAR issue, please make sure that the animation is not being overwritten.",
'C0EB6A': "Actualy an issue of SkyrimSE.exe:\nShould be fix-able by the use of 'SSE Engine Fixes' mod",
'C1315C': "controlmap.txt...What have you done?!\nProbably some mod that uses hotkeys might have modified this file... good luck with the hunt!",
'D02C2C': "Monster Mod.esp\nNumerous errors and causes of CTD, even with the unoffical patches and latest updates of the mod itself.\nTo keep it short: Do not use.",
'D2B923': "Save game issue:\nCould be related to either: Save System Overhaul(SSO) or users of the mod Alternate Start-LAL\nMaybe also related to or fixable by SkyUI SE - Flashing Savegame fix",
'D6DDDA': "Stack: BSResource::anonymous_namespace::LooseFileStream* OR BSResource::ArchiveStream* OR BSResource::CompressedArchiveStream**\nEither you do not have a pagefile that is large enough, or there is an issue with a texture of one of your mods. ",
}
# Skyrim VR
reasons_VR = {
'0B7D4DA': "Could be related to 'View yourself VR' or PLANCK (Physical Animation and Character Kinetics)",
'ViewYourselfVR.esp': "Has been reported to cause CTD and other bugs.\n\tIf this CTD happened when opening your inventory, try downgrading to 1.1.\n\t - https://www.nexusmods.com/skyrimspecialedition/mods/16809",
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
    global iCulprintSolved
    global printed
    if topic in reasons_Chance:
        txt = reasons_Chance[topic]
        iCulprintSolved = iCulprintSolved + 1
        printed.append(topic)
    elif topic in reasons_Skyrim:
        txt = reasons_Skyrim[topic]
        iCulprintSolved = iCulprintSolved + 1
        printed.append(topic)
    elif topic in reasons_VR:
        txt = reasons_VR[topic]
        iCulprintSolved = iCulprintSolved + 1
        printed.append(topic)
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
        missing_SKSE = "Error: Script Extender version not found.\n\nPlease make sure you have downloaded and installed SKSE properly to your root game directory (where the game exe is.\nLaunch the game with skse_launcher.exe, not with SkyrimSE.exe.\n\t- https://skse.silverlock.org/ (Original: recomended)\n\t- https://www.nexusmods.com/skyrimspecialedition/mods/30379 (Wrapper: preferable for Vortex Collections)"
        return missing_SKSE
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

==================================

Last but not least, increasing your pagefile is a good and simple way to avoid this.
Best practice: pagefile-size > RAM
Example: 24 GB > 16 GB RAM

Please read / follow:
1. In the Taskbar Search, type “Advanced System“. ...
2. In System Properties, click Advanced tab.
3. In Performance section click Settings button.
4. Performance Options will open. ...
5. Here, under Virtual memory, select Change.
6. Uncheck Automatically manage paging file size for all drives.
7. Select a Drive that hardly use (as in not often)
8. Set manual size
9. Set value to ~ 150% of your RAM (as shown in example)
10. Confirm with "OK".

If you want to read more about (allthough, not related to sharepoint server):
https://learn.microsoft.com/en-us/sharepoint/technical-reference/the-paging-file-size-should-exceed-the-amount-of-physical-ram-in-the-system

'''
    return str_result

######################################
### Generic User Info
######################################
total_issues = 0
total_issues = len(reasons_Chance) + len(reasons_Skyrim) + len(reasons_Engine) + len(reasons_Dialog) + len(reasons_Racemenu)
print("=====================================================================================")
print("THE SCRIPT MUST BE IN THE SAME FOLDER AS YOUR CRASH LOGS, WHICH MUST BE 'crash-*.log'")
print("Usualy this is:          %userprofile%\Documents\My Games\Skyrim Special Edition\SKSE")
print("-------------------------------------------------------------------------------------")
print("If you get an error 'File not found', make sure that have applied the exception for")
print("this script to allow it to have read/write access within this folder.")
print("=====================================================================================")
print("Covered issues/topics on Skyrim: " , total_issues , "\t\t\tSkyrim VR specific issues:" , len(reasons_VR))
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
            # Reset Culprint counter
            iCulprintCount = 0
            iCulprintSolved = 0
            
            # Basic Header
            p_title(script_title)
            # Just a little READ ME
            print("If you are asking others for assistance / help, ALWAYS provide the crashlog as well!\n#####################################################################################\n\n")
            
            # Check for logger:
            print("Crashlog tool/ver:\t",end="")
            if "Skyrim" == str(DATA[0].split(" ")[0]):
                thisLOGGER = "Crash Logger"
                # Get logger version
                ver_Logger = str(DATA[1].strip())
                print(ver_Logger)
                
                # Get SKSE version
                first_pass_str = ''.join(DATA)
                ver_SKSE = re.search("skse.*\.dll", first_pass_str)
                if ver_SKSE:
                    ver_SKSE = ver_SKSE.group(0)
                # Get Skyrim version
                ver_Skyrim = str(DATA[0].strip())
                
                # Unhandled Exception
                line_Unhandled = str(DATA[3].strip())
                parts = line_Unhandled.split(" at ")
                subparts = parts[1].split(" ")
                #if "0x000000000000" == subparts[0]:
                if 6 >= len(line_Unhandled.split(" ")):
                    print("here")
                    thisMEM = subparts[0]
                    # TODO, skip this for now!
                    # culprint.append("0x0")
                    thisFile = "n/a"
                    thisFileAdd = "n/a"
                    thisAssembler = "n/a"
                else:
                    thisMEM = subparts[0]
                    thisFile = subparts[1].split('+')[0]
                    thisFileAdd = subparts[1].split("+")[1][:7]
                    if len(parts) >= 1:
                        if "\t" in parts[1]:
                            thisAssembler = parts[1].split("\t")[1]
                            #continue
                        elif " " in parts[1]:
                            thisAssembler = parts[1].split(" ")[1]
                            #continue
                        else:
                            thisAssembler = "n/a:: "+parts[0]
                    else:
                        thisAssembler = "n/a"
                    
                
                # Retrieve Memory info
                if "PHYSICAL MEMORY" in str(DATA[9].strip()):
                    # only 1 GPU, expecting default 2
                    line_RAM = str(DATA[9].strip())
                elif "PHYSICAL MEMORY" in str(DATA[10].strip()):
                    # 2 GPU, as expected
                    line_RAM = str(DATA[10].strip())
                elif "PHYSICAL MEMORY" in str(DATA[11].strip()):
                    # 3 GPU, laptop and nerds
                    line_RAM = str(DATA[11].strip())
                elif "PHYSICAL MEMORY" in str(DATA[12].strip()):
                    # 4 GPU, just to be sure
                    line_RAM = str(DATA[12].strip())
                # Actual parsing / split for RAM    
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
                
            elif "NetScriptFramework" in str(DATA[2].strip()):
                thisLOGGER = ".NET Script Framework"
                #ver_Logger = thisLOGGER+" "+str(DATA[3].split(":")[1])
                if len(DATA[3].split(":")) >= 2:
                    ver_Logger = thisLOGGER + " " + str(DATA[3].split(":")[1])
                else:
                    # Handle the case when the split operation doesn't produce the expected result
                    ver_Logger = thisLOGGER + " Unknown Version"
                print(ver_Logger,end="")
                print("Because this crash logger is not fully supported, you WILL get multiple false-positives, most likely 'count 1' ones!")
                
                # Get SKSE version
                first_pass_str = ''.join(DATA)
                ver_SKSE = re.search("skse64_1.*\.dll", first_pass_str)
                ver_SKSE = ver_SKSE.group(0)
                
                # Get Skyrim version
                for line in DATA:
                    if "ApplicationVersion" in line:
                        ver_Skyrim = line.split(":")[1]
                        break
                
                # Unhandled Exception
                line_Unhandled = str(DATA[0].strip())
                parts = line_Unhandled.split(" at ")
                subparts = parts[1].split(" ")
                thisMEM = subparts[0]
                thisFile = subparts[1].split('+')[0].strip("()")
                thisFileAdd = subparts[1].split("+")[1][:6]
                thisAssembler = "Thread: " + parts[1].split("thread")[1].strip("!")
                
                # RAM
                RAM = "INFO: \t\t'.Net Script Framework' does not provide RAM values...."
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
            if thisLOGGER == "Crash Logger" or thisLOGGER == ".NET Script Framework" :
                
                # Check Game vs SKSE versions
                #if thisLOGGER == "Crash Logger":
                print(p_solve_GameVer(ver_Skyrim, ver_SKSE))
                
                # Show RAM info
                p_section("RAM:")
                print(RAM)
                if thisLOGGER == "Crash Logger":
                    print(p_solve_RAM(ram_use, ram_avail, ram_free))
            else:
                print("TODO SKSE, Skyrim and RAM: " + thisLOGGER)
            
            # Applies to / Works for all loggers
            # or variables have been prepared.
            
            
            # Start actual parsing...
            for line in DATA:
                if "MODULES:" in line:
                    # Stop parsing (Load Order) to prevent false-positives
                    break
                # for list chance
                for low in reasons_Chance:
                    if low in line:
                        culprint = list_add(low,culprint)
                
            # Update Culprint max
            iCulprintCount = len(culprint)
            
            #  Check for main indicators:
            p_section("Header indicators:") 
            print("Memory:  \t" + thisMEM + " " + s_Count(thisMEM,DATA) )
            print("File:    \t" + thisFile + " " + s_Count(thisFile,DATA) )
            print("Address: \t" + thisFileAdd + " " + s_Count(thisFileAdd,DATA) )
            print("Assembler:\t" + thisAssembler + " " + s_Count(thisAssembler,DATA) )
            
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
                # Reasons
                if item in reasons_Chance:
                    # Show basic reason
                    print(s_explain_topic(item))
                    # Check for more details:
                    if item == "SkyrimSE.exe":
                        skyrimexe_counter = 0
                        for thisAdd in reasons_Skyrim:
                            str_Add = item+"+"+thisAdd
                            for aLine in DATA:
                                if "Unhandled exception" in line:
                                    # Dont print this line, output is handled already
                                    continue
                                if "MODULES:" in aLine or "Modules" in aLine:
                                    # Do not print after MODULES / Loadorder
                                    break
                                if str_Add in aLine:
                                    skyrimexe_counter = skyrimexe_counter + 1
                                    print("\t-" + str_Add )#+ ":\n")
                                    print("\t\t" + reasons_Skyrim[thisAdd])
                                    print_line(aLine.strip(),printed,"\t\t\t")
                        if skyrimexe_counter == 0:
                            print("\tCould not find any known issues related to SkyrimSE.exe.\n\tSkyrimSE.exe _might_ be listed for the sole reason of... you're playing this game!!")
                    
                    if item == "hdtSMP64.dll":
                        for line in DATA:
                            if "hdtSMP64\Hooks" in line:
                                pattern = r"skse64_(\d+)_(\d+)_(\d+)"
                                match = re.search(pattern, line)
                                
                                if match:
                                    hMajor = int(match.group(1))
                                    hMinor = int(match.group(2))
                                    hBuild = int(match.group(3))
                                    
                                    #print("hMajor:", hMajor)
                                    #print("hMinor:", hMinor)
                                    #print("hBuild:", hBuild)
                                    
                                    #print("SKSE: ",ver_SKSE)
                                    SKSE_Major = ver_SKSE.split("_")[1]
                                    SKSE_Minor = ver_SKSE.split("_")[2]
                                    SKSE_Build = ver_SKSE.split("_")[3].split(".")[0]
                                    
                                    print("\tYou are using FSMP version: " + str(hMajor) + "." + str(hMinor) + "." + str(hBuild))
                                    print("\tPlease ensure that this is compatible with your SKSE version: " + str(SKSE_Major) + "." + str(SKSE_Minor) + "." + str(SKSE_Build))

                                else:
                                    print("Version number not found in the string.")
                            #else:
                            #    print("Version number not found in the string.")
                                
                            
                    if item == "SkyrimVR.exe":
                        print("todo VR")
                        vr_counter = 0
                        for thisAdd in reasons_VR:
                            for vrLine in DATA:
                                #if "SkyrimVR.exe"+thisAdd in vrLine or 
                                if thisAdd in vrLine and not any(vrLine.strip() in p for p in printed):
                                    vr_counter = vr_counter + 1
                                    print("\t-" + str_Add )#+ ":\n")
                                    print("\t\t" + reasons_VR[thisAdd])
                                    print_line(vrLine.strip(),printed,"\t\t\t")
                     
                    if item == "0x0":
                        zero_lines = []
                        for zLine in DATA:
                            if "0x0" in zLine:
                                print("yay")
                                zero_lines.append(zLine)
                                if zLine.strip() not in printed:
                                    print(zero_lines[-1],end="")
                                    print_line(zLine.strip(),printed,"z::")
                    
                    if item == "NiNode":
                        ninode_lines = []
                        for nLine in DATA:
                            ninode_lines.append(nLine)
                            if "NiNode" in nLine and not any(nLine.strip() in p for p in printed):
                                print("-" * 80 )
                                print_line(nLine.strip()+" "+s_Count(nLine.strip(),DATA),printed,"")
                                print_line(ninode_lines[-6].strip()+" "+s_Count(nLine.strip(),DATA),printed,"")
                                print_line(ninode_lines[-5].strip()+" "+s_Count(nLine.strip(),DATA).strip(),printed,"")
                    
                    if item.lower == "mesh":
                        mesh_lines = []
                        for mLine in DATA:
                            mesh_lines.append(mLine)
                            if "mesh" in mLine.lower:
                                print(mLine,end="")
                                print(mesh_lines[-1],end="")
                                print(mesh_lines[-2])
                                #print("3",mesh_lines[-3],end="")   # Should not be needed, most of the time
                    
                    if item == "skee64.dll":
                        for raceM in reasons_Racemenu:
                            for rLine in DATA:
                                if "MODULES:" in rLine or "Modules" in rLine:
                                    # Do not print after MODULES / Loadorder
                                    break
                                if raceM in rLine:
                                    print_line(reasons_Racemenu[raceM].strip(),printed,"- ")
                                    if rLine not in printed:
                                        print_line(rLine.strip(),printed,"- ")
                    
                    # Simple solutions, less, "sub parsing"
                    for aLine in DATA:
                        if "Unhandled exception" in line:
                            # Dont print this line, output is handled already
                            continue
                        if "MODULES:" in aLine or "Modules" in aLine:
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
                        if item == "Modified by":
                            ninode_lines = []
                            for nLine in DATA:
                                ninode_lines.append(nLine)
                                if "Modified by" in nLine and not any(nLine.strip() in p for p in printed):
                                    print("-" * 80 )
                                    print_line(nLine.strip()+" "+s_Count(nLine.strip(),DATA),printed,"")
                                    print_line(ninode_lines[-1].strip()+" "+s_Count(nLine.strip(),DATA),printed,"")
                                    #print_line(ninode_lines[-5].strip()+" "+s_Count(nLine.strip(),DATA).strip(),printed,"")
                                
                        if item in aLine:
                            # This should avoid double prints
                            if item in printed:
                                continue
                            print("DEBUG check entry")
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
                        print("Artesian cloaks of Skyrim:\n\tMost likely due to HDT enabled capes. Possible fix: Use the according Retexture mod or remove the cape-mod itself.\n\t- HDT SMP XMLs (for Artesian Cloaks): https://www.nexusmods.com/skyrimspecialedition/mods/25240")
                        print_line(line.strip(),printed)
                # Smooth cam
                if "SmoothCam.dll+" in line:
                    if line not in printed:
                        print("Camera:\nIf you get this error more often, try disabling (some of) the compatiblity settings in MCM (trial & error).")
                        print_line(line.strip(),printed)
            
            print("\n")
            p_section("Success Statistic: (this has been detected/handled, does not mean its the cause)")
            print("Issues Found:\t" + str(iCulprintCount) + "\nIssues Solved:\t" + str(iCulprintSolved))
            
            print("\n")
            p_section("DEBUG State:")
            print("Culprint list content: (just a list)")
            c_list = ""
            for c in culprint:
                c_list = c_list + c + ", "
            print(c_list)
            
            # End of parsing thisLOG
            sys.stdout = original_stdout
            i += 1
    # Now we're done
    print(".....DONE")
sys.stdout.close()
os.system("pause")




####### TODO #######
# Race Menu version
# Computer\HKEY_CURRENT_USER\System\GameConfigStore\Children\09acc3ff-bf5b-411c-8f5c-58fe16493122
# MatchedExeFullPath

#import winreg
#def read_registry_value(key_path, value_name):
#    try:
#        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
#        value, _ = winreg.QueryValueEx(key, value_name)
#        return value
#    except WindowsError:
#        return None
#key_path = r"Computer\HKEY_CURRENT_USER\System\GameConfigStore\Children\09acc3ff-bf5b-411c-8f5c-58fe16493122"
#value_name = "MatchedExeFullPath"
#skyrim_path = read_registry_value(key_path, value_name)
#print(f"Skyrim Path: {skyrim_path}")


### exe version
## pip install pywin32 
#import win32api
#def get_file_version(file_path):
#    info = win32api.GetFileVersionInfo(file_path, "\\")
#    major_version = info['FileVersionMS'] >> 16
#    minor_version = info['FileVersionMS'] & 0xFFFF
#    return major_version, minor_version
#file_path = r"D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data\RaceMenu.esp"
#major, minor = get_file_version(file_path)
#print(f"File Version: {major}.{minor}")


### Handle config file.... later use:
#import configparser
# Create a ConfigParser object
#config = configparser.ConfigParser()
#config_file = "CLASSE.ini"
#config_section = "CLA"
#config_option_stagedir = "stagedir"

# Check if file exists
#if not os.path.isfile(config_file):
#    p_title("First Time Setup")
#    print("Please enter the stagedir of your mod manager (where the extracted zip files are).")
#    print("You can either type, or copy then right-click to paste.")
#    stagedir = input("Path: ")
#    config.add_section(config_section)
#    config.set(config_section,config_option_stagedir,stagedir)
#    with open(config_file,'w') as configfile:
#        config.write(configfile)

# Read the INI file
#config.read(config_file)
#stagedir = config.get(config_section, config_option_stagedir)
#print(f"stagedir: {stagedir}")

#sys.stdout.close()
#os.system("pause")