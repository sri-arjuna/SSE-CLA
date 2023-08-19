# Changelog

----

Version numbers apply to "releases".

Until then, its only a log of what I've changed to prepare update info on Nexus.

----

# 2023.08.20 - 1.1.0
##  CLA SSE - itself
- Fixed: tbbmalloc / low ram - now share same text (partialy)
- Fixed: regex handling for certain SKSE occourences/detections
- Added: Windows Version check to install proper Python.. idk why that is required...

## Mod Issues
- Added: (basic) Check for missing masters
- Added: Possible texture fix - Cathedral Assets Optimizer 
- Added: 2 Possible ImprovedCamera solutions

# 2023.07.10 - 1.0.1
- Fixed: actual RAM values & analysis display formating
- Fixed: switched if block to return str_Skyrim summary
- Fixed: 80% parsing display
- Fixed: Minor typos in err_CLA
- Added: xaudio
- Added: BGSSaveLoadManager (1 of 2 save game issues)
- Added: CrashLogger version (ok ok, full line)
- Changed: CLA will no longer overwrite existing crashlogs

# 2023.07.01 - 1.0-beta
- Completly rewritten code from ground up
- - Error message with pause on:
- - - Permission issue
- - - No Crashlogger detected
- - - Most common parsing issues
- - Made Console output more fancy
- - - Should help (be more comfortable) on big files
- - Supports path as argument, to read logs of other dirs. (see ReadMe.md for details)
- Added HUD section (needs fine tuning)
- Seperated XPMSE as independent issue

# 2023.06.23 - 0.9b
- Added: Covered topics count
- Fix: Print faster hdtsmp version only once
- Added: AVX detection (skiped CUDA detection, because of false-positives and exe would be over 200mb)
- Improved: Basic version check recomendations for FSMP
- Added: CompressedArchiveStream (Corrupt Texture)
- Added: Mod Count

# 2023.06.22 - 0.9a
- Hotfix: VR crashlog can be read again.

# 2023.06.22 - 0.9
- Removed: lists that also had an according dictionary
- Removed: DLC.esm entries, since I cant disable the DLC from the steam-property 'page' (SSE)
- Improved: Handler for missing SKSE
- Improved: tbbmalloc text, covering SrtCrashFix64.dll now as well.
- Improved: HUD message display (alignment)
- Added: VR, created basic framework
- Added: probably "outside quit" ADR for SkyrimSE
- Added: DynamicCollisionAdjustment
- Added: Modified by (should help to figure wrong load orders)
- Added: Lanterns (LoS II)
- Added: Chance to retrieve FSMP version


# 2023.06.19 - 0.8
- Improved: NiNode & Mesh output, prints fewer lines now (provides a counter for their respective occourences)
- Improved texts for: RaceMenu, NiNode, Mesh, hdtsmp64.dll, cbp.dll
- Added: Message if no SkyrimSE.exe issues were found
- Added: false positive disclaimer for DLC
- Added: tbbmalloc.dll 
- Added: link for Artesian Cloak xml patch
- Added: link for hdt/SMP NPC fix
- Added: link for Faster HDT-SMP
- Fixed: Message display for no_alloc
- Fixed: Parsing of files with 6 or less strings on line "Unhandled Exception" (previously was only handling 0x000000000000 specificly)


# 2023.06.17 - 0.7b
- Improved crashfile reading
- Should fix 2 different kind of reading issues

# 2023.06.16 - 0.7a
- Added: NiNode & Mesh handling
- Added: HUD Keyword

# 2023.06.15 - 0.7
- Initial Release on Nexus