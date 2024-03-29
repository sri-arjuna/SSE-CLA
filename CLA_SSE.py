#!/usr/bin/env python3
"""
  Work-name:		SSE CLA - Sephs Skyrim Experimental Crash Log Analyzer
 Release-name:	 CLA SSE
 -----------------------------------------------------------------------------

 Created: 2023.04.22 by Sephrajin aka sri-arjuna aka (sea)
 Licence: GPLv2
 Source code:	  https://github.com/sri-arjuna/SSE-CLA
 Nexus Mod page:   https://www.nexusmods.com/skyrimspecialedition/mods/89860

 -----------------------------------------------------------------------------

 In no way I claim this to be either perfect, nor functional,
 it should only assist you to help getting an indication of what MIGHT be wrong,
 without any guarantee that this actually is the cause of the crash.

 -----------------------------------------------------------------------------
"""
######################################
### Script Variables
######################################
script_name = "CLA SSE - Sephs Skyrim Experimental Crash Log Analyzer"
script_version = "1.2.0"
script_changed = "2023.09.10"
script_title = script_name + " (" + script_version + ") / " + script_changed
######################################
### Windows Version Check
######################################
import platform
import sys
import os
# Get the Windows version string
windows_version = platform.release()
# Check if the version is 7 or lower than 10
if windows_version.startswith("6.") or windows_version.startswith("5."):
	print("Windows version is 7 or lower than 10.")
	print("You will need to install the following, in order for the tool to work:")
	print("--> https://github.com/adang1345/PythonWin7/tree/master/3.12.0b4")
	os.system("pause")
	sys.exit(1)
######################################
### Python Version Check
######################################

if sys.version_info[:2] < (3, 3):
	print("This script requires Python 3.3 or higher.")
	print("Please download and install it from https://www.python.org/downloads/")
	os.system("pause")
	sys.exit(1)
######################################
### Imports
######################################
import re
import time  # # Not really required, but otherwise we get 0 files on tqdm's progressbar...
from dataclasses import dataclass  # dict_RAM and others
from enum import Enum
from multiprocessing import freeze_support  # pip install multiprocessing
from cpuinfo import get_cpu_info  # pip install py-cpuinfo
from tqdm import tqdm  # Progress bar -- pip install tqdm
######################################
### Dictionaries
######################################
# Exception due to recently shared "same solution"...
txt_solution_low_ram = '''
		First and foremost, try to close any other application and background processes that might be running that you do not need.
		Like, but not limited to, game launchers, web browsers with 20 open tabs, Spotify, even Discord.
		Also, you might want to consider using lower texture mods, aka, use a 2k instead of a 4k texture mod, or just a 1k texture.

		If the above did not help, you could try apply these config tweaks to: __Skyrim.ini___
		Make sure to comment out (#) any existing variants of these, so you can go back if they dont help or make things worse.

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


# Skyrim SE
simple_Skyrim = {
	'0CB748E': "Have you closed Skyrim 'from the outside' aka with Taskmanager? -- Verification appreciated.",
	'12FDD00': "Probable Callstack: BSShader::unk_xxxxxxx+xx mentioned FIRST or with the HIGHEST PRIORITY\nBroken NIF\n"
			+ "Best approach, disable some of your NIF mods and figure out which one is causing it by starting a new game to reproduce the error,"
			+ "once figured, report to the mod author so they can create a fix.\n"
			+ "OR, use CAO(Cathedral Assets Optimizer), but that could lead to other issues.. so... its up to you.",
	'12F5590': "Facegen issue:\n"
			+ "Regenerate the Face in CK, search for 'BSDynamicTriShape' as a hint, or check the  HDT-SMP log for the last NPC used. You might need to increase the log level if you haven't dont so already.",
	'132BEF': "Head Mesh Issue:\nCheck the HDT-SMP log where the last NPC most probably could be the issue.\n"
			+ "If you use 'Ordinary Women', make sure that mod gets loaded last among mods that change body/heads.",
	'5999C7': "Monster Mod.esp\n"
			+ "Numerous errors and causes of CTD, even with the unofficial patches and latest updates of the mod itself.\n"
			+ "To keep it short: Do not use.",
	'5E1F22': "Missing Master (esm):\n"
			+ "Get/fix your mod list in order... dammit!\n"
			+ "Either mod manager should have warned you about this issue!",
	'67B88B': "Probably related to: Callstack: 'AnimationGraphManagerHolder'\n"
			+ "For now, make sure to regenerate animations using FNIS or Nemesis and NEVER delete FNIS.esp, as that file is generated by either of the two.",
	'7428B1': "Install 'SSE Engine Fixes.\n"
			+ "If you do have that, are you using the 'Equipment Durability System mod'?\n"
			+ "It could be related to an enchanted weapon braking, or other mods that change a character while holding a weapon.",
	'8BDA97': "This could be an issue of having both, 'SSE Engine Fixes' and 'SSE Display Tweaks' mods active.\n"
			+ "Check their settings and/or disable one or the other to see if you get another crash - or avoid this from now on.",
	'A': "(probably:) Animation Issue:\nNo further information available",
	'A0D789': "Did you fight a dragon? Did he stomp?\n"
			+ "If you're using 'Ultimate dragons' there's a fix on its Nexus page.\n"
			+ "It could also be a DAR issue, please make sure that the animation is not being overwritten.",
	'C0EB6A': "Actually an issue of SkyrimSE.exe:\nShould be fix-able by the use of 'SSE Engine Fixes' mod",
	'C1315C': "controlmap.txt...What have you done?!\nProbably some mod that uses hotkeys might have modified this file... good luck with the hunt!",
	'D02C2C': "Monster Mod.esp\n"
			+ "Numerous errors and causes of CTD, even with the unofficial patches and latest updates of the mod itself.\n"
			+ "To keep it short: Do not use.",
	'D2B923': "Save game issue:\n"
			+ "Could be related to either: Save System Overhaul(SSO) or users of the mod Alternate Start-LAL\n"
			+ "Maybe also related to or fixable by SkyUI SE - Flashing Savegame fix",
	'D6DDDA': "Stack: BSResource::anonymous_namespace::LooseFileStream* OR BSResource::ArchiveStream* OR BSResource::CompressedArchiveStream**\n"
			+ "Either you do not have a pagefile that is large enough, or there is an issue with a texture of one of your mods. ",
}
# Skyrim VR
simple_VR = {
	'0B7D4DA': "Could be related to 'View yourself VR' or PLANCK (Physical Animation and Character Kinetics)",
	'ViewYourselfVR.esp': "Has been reported to cause CTD and other bugs.\n"
			+ "\tIf this CTD happened when opening your inventory, try downgrading to 1.1.\n"
			+ "\t - https://www.nexusmods.com/skyrimspecialedition/mods/16809",
	'FPSFixPlugin.dll': "",
}
# Both
simple_Chance = {
	'skse64_loader.exe': "At best, this entry is an indication that the culprint is a mod that is using SKSE...",
	'SkyrimSE.exe': "This file on its own is not the cause, however, we'll do further parsing...",
	'SkyrimVR.exe': "This file on its own is not the cause, however, we'll do further parsing...\n"
				+ "\tBe aware, VR has a lot fewer players, so much less issues are covered...",
	'skee64.dll': "Some mod might be incompatible with RaceMenu, or your body.\n\tYou might want to read:\n"
				+ "\t -  https://www.nexusmods.com/skyrimspecialedition/articles/1372 \n"
				+ "\t - https://www.nexusmods.com/skyrimspecialedition/mods/44252?tab=description\n"
				+ "\tIf there are any further entries below this, it might be a strong indicator for its cause.\n"
				+ "\tAlso, please make sure to have this installed:\n"
				+ "\t- Race Compatibility: https://www.nexusmods.com/skyrimspecialedition/mods/2853",
	'Trishape': "Trishapes are related to meshes, specifically a mod supplying a bad mesh. ",
	'NiNode': "Ninodes are related to skeletons. It could be a wrong loadorder for skeleton based mods.\n"
				+ "\tIf you use HDT/SMP, make sure to load it like: Body (CBBE or BH/UNP) -> FNIS/Nemesis -> DAR -> HDT -> XP32\n"
				+ "\tAlso make sure that you've chosen the HDT/SMP variant of xpmsse.\n"
				+ "\tIf you find a mod name in the following list, try disabling it and rerun FNIS or Nemesis.",
	'mesh': "Some generic mesh issue, yet to be defined...\n"
				+ "\tIf there are any 'indent' lines, they might give a more precise of what _could_ be the reason.\n"
				+ "\t-- This is beta detection, and might not be accurate --\n"
				+ "\t-- This is showing previous lines 1 & 2, and is considered WIP --",
	'hdtSMP64.dll': "If this appears often, it might indicate a bad config (rare).\n"
				+ "\tHowever, it might also just indicate that there were NPCs around that were wearing hdt/SMP enabled clothing...\n"
				+ "\tPlease increase the log level for hdtsmp64 (if you have not done so yet) and check its content.\n"
				+ "\n\tMake sure to have Faster HDT-SMP that suits your Skyrim Version:\n"
				+ "\t- https://www.nexusmods.com/skyrimspecialedition/mods/57339 \n"
				+ "\n\tAlso make sure you have these installed:\n"
				+ "\t- SMP NPC fix: https://www.nexusmods.com/skyrimspecialedition/mods/91616 \n",
	'cbp.dll': "If this appears often, it might indicate a bad config (rare). \n"
				+ "\tHowever, it might also just indicate that there were NPCs around that were wearing SMP/cbp enabled clothing...\n"
				+ "\tMake sure to have this installed:\n\t\n"
				+ "\t- SMP NPC fix: https://www.nexusmods.com/skyrimspecialedition/mods/91616 ",
	'bad_alloc': "100% your issue! Free RAM, buy more RAM or increase the swap-file (pagefile)... either way, this IS the cause!\n"
				+ "\tTry this:\n"
				+ "\t\t- https://learn.microsoft.com/en-us/sharepoint/technical-reference/the-paging-file-size-should-exceed-the-amount-of-physical-ram-in-the-system",
	'no_alloc': "Could not find the proper memory allocation provided by reference\n"
				+ "\tIf this happens often, you might want to run a 'MemCheck' to check your RAM for faulty hardware.",
	#' Dawnguard.esm': "Your missing the required DLC!\n\tThis might be a false-positive, or not... Needs further investigation!",
	#' Dragonborn.esm': "Your missing the required DLC!\n\tThis might be a false-positive, or not... Needs further investigation!",
	#' Hearthfire.esm': "Your missing the required DLC!\n\tThis might be a false-positive, or not... Needs further investigation!",
	'SchlongsOfSkyrim.dll': "Dont esl'ify any mod that uses Schlongs. Use a previous save and re-schlongify all armors in MCM.",
	'nvwgf2umx.dll': "Update your NVidia driver!\n"
				+ "\tOr your PC is too weak - aka - try fewer / lighter mods.",
	'0x0 on thread ': "This actually is an engine issue of Skyrim, but rare.\n"
				+ "\tMost often caused by 'Face lighting' / 'Face shadow' issues. Best chance to avoid: Make sure have the newest SSE Engine Fix!\n"
				+ "Now parsing some keywords that might (or not) give some additional indication.",
	'HUD': "There seems to be an issue with your HUD / UI.\n" \
		   		+ "\tNordic UI using the TDM patch might be the cause (at the very least in combination with Skyrim Souls).\n"
				+ "\tIf that is not what you are using, please figure out a fix and send me your crashlog and solution.",
	'tbbmalloc.dll': "Threading Building Blocks Memory Allocator\n"
				+ "\tThis is either part of:\n"
				+ "\t- the CreationKit Fixes: https://www.nexusmods.com/skyrimspecialedition/mods/20061 \n"
				+ "\t- the Engine Fixes (part 2): https://www.nexusmods.com/skyrimspecialedition/mods/17230 \n" \
				+ f"\tI do recommend to use Engine Fixes (pick 'part 1' according to your SKSE)\n\n"
				+ "\tThis message is shown without a check:\n" \
				+ "\tMake sure to disable: SrtCrashFix64.dll (Animation Limit Crash fix SSE) as this is handled by the Engines Fixes, which is recommended to use!\n"
				+ "\tEither way, make sure to have the 'latest' version variant for your Skyrim edition.\n"
				+ "\tHowever, this probably is not the cause, but the causing mod relies on excessive memory handling."\
				+ txt_solution_low_ram	,
	'DynamicCollisionAdjustment.dll': "General statement, this one is incompatible with the PLANCK for VR.\n"
				+ "\tWhile the name is tempting and promising, bug reports since october 2022 seems to be left untouched by the mod author.\n"
				+ "\tPlease check your issue with the bugs listed there:\n"
				+ "\t- https://www.nexusmods.com/skyrimspecialedition/mods/76783?tab=bugs\n\n\t",
	'Modified by': "These are only listed as additional hints for probably debugging. If you have no other indicators, this might be worth investigating. \n"
				+ "\tIf you do have other indicators, try to solve those first!\n"
				+ "\tThat said, it is common to have 2-4 mods listed in a row, however, \n"
				+ "\tlists of 5 or more _might_ cause issues by the sheer amount of what possibly could be overwritten several times.",
	'lanterns\\lantern.dds': "If you are using: 'Lanterns of Skyrim II' and 'JK Skyrim' do not install the 'No Lights Patch' since LoS II patch is meant to be used without it.",
	'Lanterns Of Skyrim II.esm': f"If you are using: 'Lanterns of Skyrim II' and 'JK Skyrim' do not install the 'No Lights Patch' since LoS II patch is meant to be used without it.",
	'CompressedArchiveStream': "Indicates an issue with a corrupted texture.\n"
				+ "\tIf the results show a DLC, it is probable that another mod overwrites that texture.\n"
				+ "\tIf you do not get a specific texture name, you might want to extract the according '*.BSA' of any found '*.esp' or '*.esm', that is not a DLC.esm.\n"
				+ "\tHowever, best practice would probably be to disable texture mods that change locations you crashed in.",
	'XPMSE': "This _might_ shows a probable issue with animations.\n" \
				+ "\tPlease check mods that add animations.",
	'XAudio': "Despite the leading X, xaudio is part of Windows base installations and NOT part of DirectX.\n"
				+ "\tGeneral info on xaudio:\n\t\t\t https://learn.microsoft.com/en-us/windows/win32/xaudio2/xaudio2-redistributable \n\n"
				+ "\tYou can download an xaudio redist version directly form:\n\t\t\t https://www.nuget.org/packages/Microsoft.XAudio2.Redist \n"
				+ "\tUsualy, the later the better, however it also depends on which version you are missing.\n"
				+ "\tThe nuget site is linked to from the official Microsoft website.",
	'BGSSaveLoadManager': "Once you've managed to load the last working save, try this:\tplayer.kill \n"
				+ "\tThis has to be confirmed to be working (guess, I'll be told when its not).",
	'textures': "There is a chance for an issue with textures.\n" \
				+ "\tThe following tool might be of help to solve that issue:\n" \
				+ "\t- Cathedral Assets Optimizer: https://www.nexusmods.com/skyrimspecialedition/mods/23316",
	'ImprovedCameraSE.dll+': "It is not yet clear what can cause this...\n" \
				+ "\t- Some report to add: '-forcesteamloader' (without quotes) to SKSE arguments for your mod manager.\n" \
				+ "\t- If running ReShade, try changing the ini to 'MenuMode=0'\n"\
				+ "\n\tIf neither of this works, please ask for help on: https://www.nexusmods.com/skyrimspecialedition/mods/93962 \n" \
				+ "\tand let me know about the solution as well, so i'll be able to include it in the 'next update'.",
	'Skyrim unbound': "If you have not already, you can try installing (one of) these fixes:" \
				+ "\t- https://www.nexusmods.com/skyrimspecialedition/mods/30536" ,
	'Upscaler.dll+': "This crash could be related to Upscaler.\n" \
				+ "\t- Try disabling it to figure it it really is. (aka cant reproduce issue)\n" \
				+ f"\t- If is, you might want to check: %userprofile%\Documents\My Games\Skyrim Special Edition\SKSE\SkyrimUpscaler.log\n" \
				+ "\n\tThen Report your issues to: https://www.nexusmods.com/skyrimspecialedition/mods/80343" ,
	'bswin32keyboarddevice': "Usualy, a simple restart of the computer should fix the issue.",
	'DynDOLOD.esm': "There is a chance that this might cause a CTD when changing locations.\n" \
				+ "\tSpecificly when passing a door of some sorts, can cause the game its AUTO-SAVE to be triggered, because the scripts were not done when its called and thus make the game stall.\n" \
				+ "\tTo avoid that, it is recomended to DISABLE Autosave in game settings.\n" \
				+ "\n\tIf that does not help, please report to either:\n" \
				+ "\thttps://www.nexusmods.com/skyrimspecialedition/mods/32382 \n<OR>\n"
				+ "\thttps://stepmodifications.org/forum/forum/223-dyndolod-xlodgen/ for a more detailed investigation.",
}
# Dialogue - no detailed description, summarizing in if block
simple_Dialog = {
	'Honed Metal': "todo Honed Meta",
	'Your Own Thoughts': "todo Your Own Thoughts",
	'Swift Service': "todo Swift Service",
}
# Racemenu
simple_Racemenu = {
	'XPMSEWeaponStyleScaleEffect.psc': "todo XPMSEWeaponStyleScaleEffect",
	'agud_system.psc': "todo",
	'BGSHazard(Name: `Fire`': "todo BGSHazard",
	'XPMSE': "todo XPMSE",
	'race': "todo race",
	'face': "todo face",
} 
# Engine
simple_Engine = {
	'Facelight Plus': "- Try 'no facelight' variant",
	'Autoconversation-Illuminate': "- Try 'no facelight' variant for 'Facelight Plus'",
	'ShadowSceneNode(Name: `shadow scene node`)': "Unproven, but could indicate cause by combination of multiple lighting mods.",
	'BSFadeNode(Name: `skeleton.nif`)': "",
	'NiCamera': "Unproven, but could indicate cause by combination of multiple lighting mods.",
}
# HUD related
simple_HUD = {
	'Nordic ': "If you're using Nordic UI's TDM patch together with Skyrim Souls, this might be the cause.\n",
	'Skyrim Souls': "If you're using this mod, make sure to DISABLE the TDM patch of Nordic UI (if you're using that).\n",

}

######################################
### Dictionaries	:	counter+
######################################
# Dynamically get all dictionaries into one list
list_all_dict = [name for name in globals() if name.startswith('simple_')]
# Initialize / reset solution counter
count_solution_64 = 0
count_solution_VR = 0
count_solution_All = 0
# Now 'split' count them, make VR specific
for lid in list_all_dict:
	# Expand var to dict:
	dictionary = globals()[lid]
	# Now add amount of entries of each dictionary
	if lid == "simple_VR":
		count_solution_VR += len(dictionary)
	else:
		count_solution_64+= len(dictionary)
	count_solution_All = count_solution_64 +count_solution_VR
# Update counter for soluztions:
list_dict = list_all_dict.copy()
list_dict.remove("simple_Skyrim")
list_dict.remove("simple_Engine")
list_dict.remove("simple_Racemenu")
list_dict.remove("simple_Dialog")
list_dict.remove("simple_HUD")


######################################
### Functions:		Error Handling
######################################

class err_CLA(Enum):
	NoCrashLogger = "Fatal:\n"\
		+ "\tCould not detect CrashLogger. Please use:\n"\
		+ "\thttps://www.nexusmods.com/skyrimspecialedition/mods/59818"
	NoFiles = "\nEither there are no logs in: \n"\
		+ "\t\t%s\n"\
		+ "\tOr all logs have a Report.\n" \
		+ "\tEither way, nothing to do...\n\n"
	NoPerm = "\nPermissionError:\n"\
		+ "\tPath exists, but you have no permission to it: %s\n"\
		+ "\tPlease check your Windows security notifications (next to the clock in the taskbar).\n"
	NoSeparator = "Error: \n" \
		+ "\tCould find neither '.' nor '_' as seperator in string: %s\n"
	Usage = "Usage: CLA_SSE.py [\"C:\\some dir\\to\\logs\"]"

	def format(self, err_msg):
		return self.value % err_msg


def print_error(eType, eStr=""):
	"""Prints formatted error"""
	print(eType.format(eStr))
	os.system("pause")
	sys.exit(1)

def print_err(eType):
	"""Prints formatted error"""
	print(eType.value)
	os.system("pause")
	sys.exit(1)


######################################
### Functions:		Console Output
######################################

def console_Header(total_Skyrim=0, total_VR=0):
	"""Prints basic disclaimer-heading on the console"""
	print("=====================================================================================")
	print("THE SCRIPT MUST BE IN THE SAME FOLDER AS YOUR CRASH LOGS, WHICH MUST BE 'crash-*.log'")
	print("Usually this is:		  %userprofile%\\Documents\\My Games\\Skyrim Special Edition\\SKSE")
	#print("-------------------------------------------------------------------------------------")
	#print("If you get an error 'File not found', make sure that have applied the exception for")
	#print("this script to allow it to have read/write access within this folder.")
	print("=====================================================================================")
	print("Covered issues/topics on Skyrim: ", total_Skyrim, "\t\t\tSkyrim VR specific issues:", total_VR)
	print("=====================================================================================")


######################################
### Functions:		File Output
######################################
def p_title(msg) -> str:
	"""Print regular title strings with an underline"""
	sReturn = msg + "\n"
	sReturn += "-" * len(msg) #+ "\n"
	return sReturn


def p_section(msg) -> str:
	"""Print string with a line of # on top and bottom"""
	sReturn = "\n" + "#" * 80 + "\n"
	sReturn += msg + "\n"
	sReturn += "#" * 80 + "\n"
	return sReturn


def p_debug_status(debugList, iCount=0, iSolved=0) -> str:
	"""Shows statistic & closing debug info"""
	sReturn = p_section("Success Statistic: (this has been detected/handled, does not mean it's the cause)")
	sReturn += "Issues Found:\t" + str(iCount) + "\nIssues Solved:\t" + str(iSolved) + "\n"
	sReturn += p_section("DEBUG State:")
	sReturn += "Culprit list content: (just a list)" + "\n"
	for s in debugList:
		sReturn += s + ", "
	return sReturn


def show_Simple(itm, FileContent) -> str | None:
	"""Check dict's for itm and prints the according entry, while printing nice 'section'"""
	# Print simple solution
	for lad in list_all_dict:
		# Expand var to dict:
		d = globals()[lad]
		for l in FileContent:
			if itm in d and itm in l:
				sReturn = itm + ": " + s_Count(itm, FileContent) + "\n"
				sReturn +="\t" + d[itm]
				return sReturn
	return None

######################################
### Functions:		Strings & Lists
######################################
def s_Count(txt, FileContent):
	"""Returns 'count' of 'txt' found in 'log'"""
	count = 0
	for line in FileContent:
		if txt in line:
			count += 1
	#return "(count: " + str(count) + ")"
	return f"count: ({count})"


def list_add(item, list) -> list:
	"""Add item to a list if not in list already."""
	if item not in list:
		list.append(item)
	return list


def list_remove(item, list) -> list:
	"""Remove item from a global list"""
	if item in list:
		list.remove(item)
	return list


def print_line(line2print, list2add, prefix="") -> str:
	"""Print line if not printed yet and add to list2add """
	str_tmp = ""
	if line2print not in list2add:
		list2add.append(line2print)
		if prefix is not None and prefix != "":
			str_tmp = prefix + line2print + "\n"
		else:
			str_tmp = line2print + "\n"
	return str_tmp


@dataclass
class RamData:
	total: float
	used: float
	free: float

def get_RAM(FileContent) -> RamData | None:
	"""Parses FileContent and returns a Dataclass with: Total, Used, Free"""
	match = re.search(r'PHYSICAL MEMORY: (\d+\.\d+) GB/(\d+\.\d+) GB', FileContent)
	dict_RAM = {}
	if match:
		total = float(match.group(2))
		used = float(match.group(1))
		free = round(total - used, 2)
		return RamData(total, used, free)
	else:
		return None


def solve_RAM(ram_data: RamData) -> str:
	"""Expands ram_dict and returns possible solution"""
	if ram_data:
		str_result = ""
		str_result = f"RAM Total:	{ram_data.total} GB\n"
		str_result += f"RAM Used:	{ram_data.used} GB\n"
		str_result += f"RAM Free:	{ram_data.free} GB\n"
		bol_maybe = 0
		str_result += "\nAnalysis "
		if ram_data.free <= 1.5:
			str_result += "RAM (critical):\n" \
				+ f"\t\tThere is a very high chance that the main reason for the crash was lack of free ram: {ram_data.free} GB\n"
			bol_maybe = 1
		elif ram_data.free <= 2.0:
			str_result += "RAM (maybe, probably not):\n" \
				+ "\t\tAlthough unlikely, there is a slim chance that the crash might have happened due to lack of free ram: " \
				+ str(ram_data.free) + " GB\n"
			bol_maybe = 1
		else:
			str_result += "RAM (all good):\n" \
				+ "\t\tIt is absolute unlikely that the crash was due to RAM.\n"

		if bol_maybe:
			str_result += txt_solution_low_ram
		return str_result + "\n"
	else:
		return "RAM could not be detected...\nSkipping...\n"


@dataclass
class UnhandledData:
	mem: str
	file: str
	adress: str
	assembler: str

def get_Unhandled(sUnhandled: str) -> UnhandledData | None:
	"""Returns a dataclass of UnhandledExceptions: file, mem, address, assembler"""
	parts = sUnhandled.split(" at ")
	subparts = parts[1].split(" ")

	if 6 >= len(sUnhandled.split(" ")):
		# This is the short variant that does not have this data...
		thisMEM = subparts[0]
		thisFile = "n/a"
		thisFileAdd = "n/a"
		thisAssembler = "n/a"
	else:
		# This should be most cases:
		thisMEM = subparts[0]
		thisFile = subparts[1].split('+')[0]
		thisFileAdd = subparts[1].split("+")[1][:7]
		# TODO check with Net Framework
		if len(parts) >= 1:
			if "\t" in parts[1]:
				thisAssembler = parts[1].split("\t")[1]
			# continue
			elif " " in parts[1]:
				thisAssembler = parts[1].split(" ")[1]
			# continue
			else:
				thisAssembler = "n/a:: " + parts[0]
		else:
			thisAssembler = "n/a"
	return UnhandledData(thisMEM, thisFile, thisFileAdd, thisAssembler)

def get_crash_logs(logdir='.') -> list:
	"""Get Crash logs that do not have a report yet."""
	pattern = re.compile(r'crash-.*\.log$')
	patternR = re.compile(r'crash-.*REPORT\.txt$')
	# Make sure logdir is a directory
	if os.path.isfile(logdir):
		logdir = os.path.dirname(logdir)
	# Use list comprehension to create a list of files that match the pattern
	files = [os.path.join(logdir, f) for f in os.listdir(logdir.strip()) if os.path.isfile(os.path.join(logdir, f)) and pattern.search(f)]
	reports = [os.path.join(logdir, f) for f in os.listdir(logdir.strip()) if os.path.isfile(os.path.join(logdir, f)) and patternR.search(f)]
	#if patternR is not None and len(patternR) > 1:
		# More than one report has found, just inform user anyway
	#	print("--> You might want to move your old crashlogs to a sub-directory. <--")
	return files	## TODO: Remove when rewrite is done // re-enabled bypass: bug fix #1
	# Remove any log that already has a "-REPORT.txt" file
	with tqdm(total=len(files), desc="Removing duplicates", unit="Report") as progress_bar:
		for f in files.copy():
			report_file = f.removesuffix(".log") + "-REPORT.txt"
			if report_file in reports:
				progress_bar.update(1)
				time.sleep(0.0000000000001)
				files.remove(f)
	return files


@dataclass
class VersionData:
	Full: int
	Major: int
	Minor: int
	Build: int

def get_version_Mod(str_Mod: str) -> VersionData:
	"""Parses str_Mod for regex based on prefix and suffix, then returns:
	full, major, minor, build numbers"""
	str_work = []
	full_tmp = ""
	sFull = 0
	sMajor = 0
	sMinor = 0
	sBuild = 0
	# Prepare string
	exp = r"(?:(64_)?)((\d+[\._]){2}\d+)"
	str_work = re.search(exp, str_Mod).groups()
	full_tmp = str_work[1]
	# Split to subsections
	if "_" in full_tmp:
		sMajor = full_tmp.split("_")[0]
		sMinor = full_tmp.split("_")[1]
		sBuild = full_tmp.split("_")[2]
	elif "." in full_tmp:
		sMajor = full_tmp.split(".")[0]
		sMinor = full_tmp.split(".")[1]
		sBuild = full_tmp.split(".")[2]
	else:
		#print("Error: \nCould find neither '.' nor '_' as seperator in string:\n" + full_tmp)
		print_error(err_CLA.NoSeparator, full_tmp)
		#return None
	# Print proper "full"
	sFull = f"{sMajor}.{sMinor}.{sBuild}"
	# Return dictionary
	return VersionData(sFull, sMajor, sMinor, sBuild)


def solve_SKSE(skyrim: VersionData, skse: VersionData) -> str:
	"""Compares the versions of Skyrim and SKSE and returns an according answer"""
	if skse.Full is None or skse.Full == "":
		missing_SKSE = "Error:\n" \
				+ "\tScript Extender version not found.\n\n" \
				+ "Please make sure you have downloaded and installed SKSE properly to your root game directory (where the game exe is.\n" \
				+ "Launch the game with skse_launcher.exe, not with SkyrimSE.exe.\n" \
				+ "\t- https://skse.silverlock.org/ (Original: recomended)\n" \
				+ "\t- https://www.nexusmods.com/skyrimspecialedition/mods/30379 (Wrapper: preferable for Vortex Collections)"
		return missing_SKSE
	# Show basic full versions
	GameVer_Result = "Game Version:   \t" + str(skyrim.Full) + "\n"
	GameVer_Result += "Script Extender:\t" + str(skse.Full) + "\n"
	# Perform actual version check for possible issues
	if skyrim.Major != skse.Major or skyrim.Minor != skse.Minor:
		GameVer_Result += "\nWarning: Game and Script Extender versions may not be compatible.\n"
	# Return string to print
	return GameVer_Result

def solve_Mods(FileContent) -> str:
	"""Print section 'Mods' if line with mods are found	"""
	sReturn = ""
	pat_mods = r"Light: (\d+)."
	for line in FileContent:
		match = re.search(pat_mods, line)
		if match:
			sReturn = p_section("Mod Count:")
			sReturn += line
			break
	return sReturn

from collections import Counter  # TODO maybe sometime later
def show_issue_occourence__OLD(issue: str, FileContent: list, list2add: list) -> str:
	"""Parses through 'FileContent' looking for 'issue', prints 'issue' if found and not in list2add yet"""
	sReturn = ""
	for tmp_Line in FileContent:
		if "Unhandled " in tmp_Line:
			continue
		#if "MODULES:" in tmp_Line.strip():
		#	return sReturn
		#else:
		#	print("DEBUG --> " + tmp_Line, flush=True)
		#if issue in tmp_Line and not any(tmp_Line in t for t in list2add):
		if issue in tmp_Line.strip() and tmp_Line.strip() not in list2add:
			sReturn += f"{tmp_Line.strip()} -//- {s_Count(tmp_Line.strip(),FileContent)}\n"
		#	list_add(tmp_Line.strip(),list2add)
		#line_counts = Counter(l.strip() for l in FileContent if issue in l)
		#for line, count in line_counts:
			list2add.append(tmp_Line.strip())
	if sReturn != "":
		return f"\n{sReturn}"
	else:
		return sReturn

def show_issue_occourence(issue: str, FileContent: list, list2add: list) -> str:
    """Parses through 'FileContent' looking for 'issue', prints 'issue' if found and not in list2add yet"""
    sReturn = ""
    for tmp_Line in FileContent:
        if "Unhandled " in tmp_Line:
            continue
        if issue in tmp_Line.strip() and tmp_Line.strip() not in list2add:
            # Not yet added, so add anyway..
            list2add.append(tmp_Line.strip())
            # Handle Exception for pre-text
            if issue == "Modified by":
                val_count = tmp_Line.strip().count("->")
                if val_count >= 10:
                    sReturn += f"\nChance: HIGH ({val_count})\n"
                elif val_count >= 5:
                    sReturn += f"\nChance: MEDIUM ({val_count})\n"
                else:
                    sReturn += f"\nChance: LOW ({val_count})\n"
            # Regular returns
            sReturn += f"{tmp_Line.strip()} -//- {s_Count(tmp_Line.strip(), FileContent)}\n"
            
    if sReturn != "":
        return f"\n{sReturn}"
    else:
        return None

##################################################################################################################
### Main Function
##################################################################################################################
def main(file_list):
	"""Get additional cpu info, loop all files and start related functions"""
	# Variables
	files_max = len(file_list) - 1
	files_cur = 0
	# Multiprocess avoidance
	if __name__ == '__main__':
		freeze_support()
		info_cpu = get_cpu_info()
		# Print console header only once, idk why this otherwise gets printed twice when compiled
		console_Header(count_solution_64, count_solution_VR)

	# Start parsing passed files:
	for thisLOG in file_list:
		files_cur += 1
		print("\n" + str(files_cur) + "/" + str(files_max) + " " + os.path.basename(thisLOG)) # + "\n")
		# Reset variables 'per file'
		culprints = []
		printed = []
		CrashLogger = "Unknown"
		MODE = "64"
		# Read the contents of the log file
		with open(thisLOG, 'r', encoding="utf-8", errors="ignore") as LOG:
			DATA = LOG.readlines()
			print("\t",end="")
			with tqdm(total=(count_solution_All - len(simple_Skyrim) - len(simple_Racemenu) - len(simple_Engine) - len(simple_Dialog) - len(simple_HUD) ), desc="* Searching...", unit=" culprint") as progress_bar:
				# Expand list of all dictionaries
				for lad in list_dict:
					# Expand var to dict:
					d = globals()[lad]
					for itm in d:
						progress_bar.update(1)
						# Just check for culprints
						for culprint_Line in DATA:
							if "modules" in culprint_Line.lower():
								if not "DynDOLOD.esm" == itm:
									break
							if itm in culprint_Line:
								#culprints.append(itm)
								culprints = list_add(itm, culprints)
			# Some file specific tasks:
			try:
				if "Skyrim" == str(DATA[0].split(" ")[0]):
					CrashLogger = "Crash Logger"
					ver_Skyrim = get_version_Mod(str(DATA[0]))
					ver_Logger = str(DATA[1].strip())
					
					# VR or SSE?
					MODE = DATA[0].split(" ")[1]
				elif "NetScriptFramework" in str(DATA[2].strip()):
					# BugFix #2 -- No more support for this.
					print(".NetScriptFramework is not support, please use CrashLogger PDB.")
					os.system("pause")
					sys.exit(1)
					return None
					CrashLogger = ".NET Script Framework"
					ver_Logger = str(DATA[2])
					for SF_Line in DATA:
						# GameLibrary: SkyrimSE
						if "GameLibrary" in SF_Line:
							MODE = SF_Line.split(": ")[1] 
						# ApplicationVersion: 1.5.97.0
						if "ApplicationVersion" in SF_Line:
							ver_Skyrim = get_version_Mod(SF_Line.split(": ")[1])
							break
						#ApplicationName: SkyrimSE.exe
			except Exception:
				# Print error and exit
				print_err(eType=err_CLA.NoCrashLogger)
			finally:
				# Apply to both, if and elif...
				# Get SKSE version
				first_pass_str = ''.join(DATA)
				ver_SKSE = re.search("skse.*\d+\\.dll", first_pass_str)
				try:
					ver_SKSE = get_version_Mod(ver_SKSE.group(0))
				except Exception:
					print("NO SKSE FOUND -> Try starting the game via SKSE_Launcher.exe !!!!")
					os.system("pause")
					#sys.exit(1)
					continue
				
				# Unhandled Exception
				line_Unhandled = re.search(r"Unhandled(\s+native)?\s+exception.*", first_pass_str)
				if line_Unhandled:
					line_Unhandled = line_Unhandled.group(0)
					# todo unhandled
					UnhandledData = get_Unhandled(line_Unhandled)
				else:
					print("Fatal:\n\tCould not detect: 'Unhandled (native) exception")
					os.system("pause")
					sys.exit(1)
		# Let's open the report for writing
		thisReport = thisLOG.removesuffix(".log")  + '-REPORT.txt'
		# has to be 1 less than counted to fix 0 index
		with tqdm(total=abs(len(culprints) + 3), desc="* Solving...", unit=" issues") as progress_bar:
			with open(thisReport, "w", encoding="utf-8", errors="ignore") as REPORT:
				# Basic Header
				print(p_title(script_title), file=REPORT)
				# Just a little READ ME
				print("If you are asking others for assistance / help, ALWAYS provide the crashlog as well!\n" \
					+ "#####################################################################################\n", file=REPORT)
				# Print system basics
				# 1
				print(f"Crashlog Tool: \t\t{ver_Logger}", file=REPORT)
				print(solve_SKSE(ver_Skyrim, ver_SKSE), file=REPORT)
				progress_bar.update(1)
				# RAM
				# 2
				tRAM =get_RAM(first_pass_str)
				print(p_section("RAM") + solve_RAM(tRAM), file=REPORT)
				progress_bar.update(1)
				# Mods
				# 3
				print(solve_Mods(DATA), file=REPORT)
				# Unhandled Exception Line
				# 4
				strUnhandled = ""
				strUnhandled = p_section("Header indicators:")
				strUnhandled += f"Memory:  		{UnhandledData.mem}		{s_Count(UnhandledData.mem, DATA)}\n"
				strUnhandled += f"File:    		{UnhandledData.file}		{s_Count(UnhandledData.file, DATA)}\n"
				strUnhandled += f"Address: 		{UnhandledData.adress}			{s_Count(UnhandledData.adress, DATA)}\n"
				strUnhandled += f"Assembler:		{UnhandledData.assembler}	{s_Count(UnhandledData.assembler, DATA)}\n"
				# Print occoureces of Unhandled
				ud_list = []
				ud_list.append(UnhandledData.file)
				ud_list.append(UnhandledData.mem)
				ud_list.append(UnhandledData.adress)
				ud_list.append(UnhandledData.assembler)
				for ud in ud_list:
					if "Skyrim" in ud:
						found_match = False
						for sS in simple_Skyrim:
							check_Sky = f"{ud}+{sS}"
							tmp_val = show_issue_occourence(check_Sky, DATA, printed)
							if tmp_val is not None:
								found_match = True
								break
						if not found_match:
							tmp_val = show_issue_occourence(ud, DATA, printed)
							if tmp_val is not None:
								strUnhandled += tmp_val + "\n"
					else:
						tmp_val = show_issue_occourence(ud, DATA, printed)
						if tmp_val is not None:
							strUnhandled += tmp_val + "\n"

				print(strUnhandled, file=REPORT)
				progress_bar.update(1)
				
				# Check for missing masters
				pattern_masters = r"\.esp"
				missing_masters = re.search(pattern_masters, first_pass_str)
				if not missing_masters:
					print(p_section("Missing Masters"), file=REPORT)
					txt_missing_masters = """	1. Please check the notification of your Mod Manager!
	2. If you cant find any entries there, try LOOT.
	3. If this yields nothing, you'll have to manualy check every mod of yours if you might have missed a dependency.
"""
					print(txt_missing_masters, file=REPORT)
					
				# Start with culprints
				print(p_section("Solutions"), file=REPORT)
				c = 0
				for cul in culprints:
					# Show basic solution
					tmp_val = show_Simple(cul, DATA)
					# Goto next culprint if no simple soloution could be found
					if tmp_val == None:
						continue
					# A solution was found, print and analyze
					print(tmp_val, file=REPORT)
					# Start detailed analysis...
					if r"modules(:)" in cul.lower():
						# Reached module list, skip to avoid false positves
						# TODO modules in culprint?
						print("Skip modules")
						continue
					if re.search(r"Skyrim.*\.exe", cul):
						# Should cover both, VR and S/SE
						skyrimexe_counter = 0
						str_Skyrim = ""
						for ad in simple_Skyrim:
							addr = cul + ad
							tmp_val2 = ""
							for adLine in DATA:
								tmp_val
								if addr in adLine:
									# TODO: Verify counter for VR and regular
									if "VR" in cul:
										tmp_val = print_line(simple_VR[ad],printed,"")
										if tmp_val is not None or tmp_val != "":
											str_Skyrim += tmp_val
											skyrimexe_counter += 1
									else:
										tmp_val = print_line(simple_Skyrim[ad],printed,"")
										if tmp_val is not None or tmp_val != "":
											str_Skyrim += tmp_val
											skyrimexe_counter += 1
									tmp_val2 = print_line(adLine,printed,"")
								if tmp_val2 is not None or tmp_val2 != "":
									str_Skyrim += tmp_val2
						if skyrimexe_counter == 0:
							str_Skyrim = f"\n\tCould not find any known issues related to {cul}.\n" \
										 + f"\t{cul} _might_ be listed for the sole reason of... you're playing this game!!"
						if str_Skyrim is not None or str_Skyrim != "":
							print(str_Skyrim, file=REPORT)

					if "CompressedArchiveStream" in cul:
						str_Compressed = show_issue_occourence("CompressedArchiveStream", DATA, printed)
						print(str_Compressed, file=REPORT)
						#for gamefile in [".esp", ".esm", ".dds"]:
						#	str_Compressed = show_issue_occourence(gamefile, DATA, printed)
						#	print(str_Compressed, file=REPORT)


					if "textures" in cul:
						print(show_issue_occourence("textures", DATA, printed), file=REPORT)
					
					if "NiNode" in cul:
						ninode_lines = []
						str_Ninode = ""
						for nLine in DATA:
							ninode_lines.append(nLine)
							if "NiNode" in nLine.strip() and not any(nLine.strip() in p for p in printed):
								str_Ninode = "-" * 80 + "\n"
								str_Ninode += print_line(f"{nLine.strip()} {s_Count(nLine.strip(), DATA)}", printed, "")
								# Print some previous lines as they _might_ give more info
								str_Ninode += print_line(f"{ninode_lines[-10].strip()} {s_Count(nLine.strip(), DATA).strip()}", printed, "")
								str_Ninode += print_line(f"{ninode_lines[-8].strip()} {s_Count(nLine.strip(), DATA).strip()}", printed, "")
								str_Ninode += print_line(f"{ninode_lines[-6].strip()} {s_Count(nLine.strip(), DATA).strip()}", printed, "")
								str_Ninode += print_line(f"{ninode_lines[-5].strip()} {s_Count(nLine.strip(), DATA).strip()}", printed, "")
						print(str_Ninode, file=REPORT)

					if "mesh" in cul.lower():
						mesh_lines = []
						str_Mesh = ""
						for mLine in DATA:
							mesh_lines.append(mLine)
							if "mesh" in mLine.lower() and not any(mLine.strip() in p for p in printed):
								list_add(mLine.strip(), printed)
								str_Mesh += mLine
								str_Mesh += mesh_lines[-1]
								str_Mesh += mesh_lines[-2]
						if str_Mesh != "":
							str_Mesh += "\n"
						print(str_Mesh, file=REPORT)

					if "0x0" in cul or "0x0 on thread " in cul:
						tmp_val = ""
						tmp_val = show_issue_occourence(cul, DATA, printed)
						for engR in simple_Engine:
							tmp_val += show_Simple(engR, DATA)
							tmp_val += show_issue_occourence(engR, DATA, printed)
						print(tmp_val, file=REPORT)

					if "skee64.dll" in cul:
						for raceM in simple_Racemenu:
							tmp_val = ""
							tmp_val = show_Simple(raceM, DATA)
							if tmp_val is not None:
								tmp_val2 = ""
								tmp_val2 = show_issue_occourence(cul, DATA, printed)
								if tmp_val2 is not None:
									tmp_val += tmp_val2
							else:
								continue
							if tmp_val is not None:
								print(tmp_val, file=REPORT)

					if "HUD" in cul:
						for h in simple_HUD:
							tmp_val = ""
							tmp_val = show_Simple(h,DATA)
							if tmp_val is not None:
								print(tmp_val, file=REPORT)
						tmp_val = ""
						tmp_val = show_issue_occourence(cul,DATA,printed)
						if tmp_val is not None:
							print(tmp_val, file=REPORT)

					if "Modified by" in cul:
						tmp_val = ""
						tmp_val = show_issue_occourence(cul,DATA,printed)
						print(tmp_val, file=REPORT)

					if "XPMSE" in cul:
						tmp_val = ""
						tmp_val = show_issue_occourence(cul, DATA, printed)
						print(tmp_val, file=REPORT)

					if "hdtSMP64.dll" in cul:
						tmp_val = ""
						pattern = r"skse64_(\d+)_(\d+)_(\d+)"
						data_string = "\n".join(DATA)  # Join the list elements with a newline separator
						match = re.search(pattern, data_string)
						if match:
							ver_HDTSMP = get_version_Mod(match.group(0))
						else:
							tmp_val = "\tCould not determine HDTSMP version.\n"

						# Prepare version comparision
						tmp_val += f"\tYou are using FSMP version: {ver_HDTSMP.Full}\n"
						tmp_val += f"\tPlease ensure that this is compatible with your SKSE version: {ver_SKSE.Full}\n"

						# Lets print a recomended version ??
						# 2.0.2 =   1.6.353,  1.6.640 , 1.6.659
						if ver_HDTSMP.Full == "2.0.2" or ver_HDTSMP.Full == "2.02.02":
							tmp_val += "\n\tThis one is marked as BETA.\n" \
									+ "\tYou might want to downgrade to one of the RC: 1.50.7-rc1 or 1.50.9-rc1\n" \
									+ "\tRelease Candidates (rc) are usualy more stable than a beta.\n"
						if ver_SKSE.Full == "1.5.97":
							tmp_val += "\n\tYou should be using the FSMP version that is marked as: 1.18\n" \
									+ "\tBecause you are using a Skyrim version that is marked as Legacy.\n"

						# Its printed once, now add it to: printed
						printed.append("hdtSMP64\\Hooks")

						# Lets figure out proper FOMOD selections:
						# ## (CUDA might return false eventhough your GPU supports it, you might need to install: https://developer.nvidia.com/cuda-toolkit for a proper result):\n\t
						tmp_val += "\n\tPossible FOMOD settings for installation\n" \
								+ "\tYou might want to try different AVX options, because eventhough supported, they might cause shutter/'lag' in populated areas...\n" \
								+ "\tCPU:\n"
						# Parse AVX
						avx_list = []
						avx_list.append("avx")
						avx_list.append("avx2")
						avx_list.append("avx512")
						for ax in avx_list:
							avx_available = ""
							avx_available = ax in info_cpu['flags']
							if avx_available != "":
								tmp_val += f"\t\t{ax}:\t{avx_available}\n"
						print(tmp_val, file=REPORT)

						#TODO more keywords / culprints ?

					# Count "solved issues" and check whether more culprints are in the list...
					c += 1
					if c < len(culprints):
						print("-" * 80 + "\n", file=REPORT)
					# End of for cul in culprints
					progress_bar.update(1)


				# Finals (default handling)
				print(p_debug_status(debugList=culprints, iCount=len(culprints), iSolved=c), file=REPORT)

				# Random issues (fallback, additional, probably to figure unhandled:
				lst_random = ["File:","Name:","XPMSEWeaponStyleScaleEffect", "ID:", "BGS", "Manager"]
				print(p_section("Random 'Fallback' Checks"), file=REPORT)
				txt_Random = """How to read these results?
- They are simple keywords that may appear when you have a lot of issues.
- They do NOT have to mean anything.
- Only if the "regular" results / solutions do not help, they might provide an indication to the reason for this crash.
"""
				print(txt_Random, file=REPORT)
				for r in lst_random:
					tmp_val = ""
					tmp_val = show_issue_occourence(r,DATA,printed)
					if tmp_val is not None and tmp_val != "":
						print(tmp_val, file=REPORT)

	return

######################################
### Variables
######################################
script_path = os.path.dirname(os.path.abspath(sys.argv[0])) or None
# If true, cant have arguments (local only), if false, it might - but then needs another path detection
contains_path = bool(script_path)
logdir = None
ver_Skyrim = {}
ver_SKSE = {}
ver_HDTSMP = {}

# Do path detection if required:
#TODO: write logs to script dir?
if contains_path:
	args_possible = False
	#work_dir = script_path
	work_dir = "."
else:
	args_possible = True
	work_dir = os.path.dirname(os.path.abspath(__file__))

######################################
### Start stuff
######################################
# Get args first
workfiles = None
if len(sys.argv) == 2:
	if os.path.isdir(sys.argv[1]):
		logdir = sys.argv[1]
	else:
		print_err(err_CLA.Usage)
else:
	logdir = work_dir
# This should retrieve files, 
# and raise exception if permission is missing.
try:
	workfiles = get_crash_logs(logdir)
except Exception as err:
	# Practical tests show, this is raised on permission issue:
	print("Args: \t", err.args)
	print("Trace: \t", err.with_traceback)
	#print_error(err_CLA.NoPerm, logdir)
	#os.system("pause")
	#sys.exit(1)
# Don't call main() if there is nothing to do
if workfiles is None or len(workfiles) == 0:
	pass
	#print_error(err_CLA.NoFiles, logdir)
	#print("Chance of false positive... idk")
else:
	# Start routine / handle file by file
	main(workfiles)

# Exit properly
os.system("pause")
sys.exit(1)


# Should have added some context.. needs research... i wrote it for a reason.. just dont remember why...
# https://www.nexusmods.com/skyrimspecialedition/mods/10547
