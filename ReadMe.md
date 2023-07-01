CLA SSE - Sephs Skyrim Experimental Crash Log Analyzer
-------------------------------------------------------

# Goal:
- Obtain a user-friendly indication of the most likely cause of the crash.
- Present a list of one or more potential culprits (reasons).
- Condense the information from the original crash log file for easier debugging.

----

# Reason:
- Addressing the need for a more accessible method of analyzing crash logs in Skyrim.
- Developed this tool to streamline the process.

----

# FYI - Experimental:
- An introductory project to familiarize myself with crash log analysis.
- Limited knowledge of memory addresses.
- Community-driven solutions.

----

# Requirements:
* General:
* * Recomended: [Crash Logger SSE AE VR - PDB support](https://www.nexusmods.com/skyrimspecialedition/mods/59818)
* * Alternative: [Crash Logger](https://www.nexusmods.com/skyrimspecialedition/mods/59596)
* Github:
* * Get Python script: from [GitHub](https://github.com/sri-arjuna/SSE-CLA)
* * [Python 3.3 or higher](https://www.python.org/downloads/) 
* * Multiple imports (sys, os, re, time, enum, cpuinfo, multiprocessing, tqdm, dataclass )
* Nexus:
* * Get compiled version: [CLA SSE](https://www.nexusmods.com/skyrimspecialedition/mods/89860)


### PS:
*While Crash Logger is mandatory, I've added basic support for the NetScriptFramework to ensure the script runs without issues.* 

*However, please note that the NetScriptFramework is not officially supported, and will result on weird and incomplete results.*

----

# Installation:
* Download file
* Extract to \<My Games\>\Skyrim \<Version\>\SKSE
* Double click the file.

### Alternative:

- You can download the tool to any directory you want.
- Start it like: 
- - python.exe CLA_SSE.py "C:\Path with spaces\to\logs"
- - CLA_SSE.exe "C:\Path with spaces\to\logs"
- This will read the log files from that path, and write the reports there too.
- Note that you still need to have write permission to do so.

----

# Usage:
* Double click on the python file.
* Double click on the generated reports.
* Fix issues
* Profit

----

# License:
GNU GPL v2 --> [LICENSE](./LICENSE)

----

# Credits
- Bethesda for Skyrim
- the Ostim community for their guide on how to read the Crashlogs and providing me textfiles with notes on solutions.
- the Python Discord community for their help and patience
