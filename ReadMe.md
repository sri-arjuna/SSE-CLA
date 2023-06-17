CLA SSE - Sephs Skyrim Experimental Crash Log Analyzer
-------------------------------------------------------

# Goal:
- Get an easy-to-read indication of the most probable cause for the crash.
- Provide a list of 1 or more possible culprits (reasons) 
- Print/Summarize original lines only once for easier debugging
- Shorten the things to read compared to original (raw) crash log file


----

# Reason:
- Got tired of reading crash logs and there is nothing available like that for Skyrim.
- So I decided to write one myself.


----

# Requirements:
* [Crash Logger](https://www.nexusmods.com/skyrimspecialedition/mods/59596) or [Crash Logger SSE AE VR - PDB support](https://www.nexusmods.com/skyrimspecialedition/mods/59818)
* [Python 3.3 or higher](https://www.python.org/downloads/) (this applies to the py script version only, obviously.)


***Note:*** *if you are using my [Skyrim SE collection for Vortex](https://next.nexusmods.com/skyrimspecialedition/collections/1bxi7n), you only need to make sure that python is installed. (if you use the github version)*

### PS:
*** While Crash Logger is listed as mandatory, I've added **basic** support for the NetScriptFramework, so that the scripot (should) run without failing. 
However, the NetScriptFramework is __not__ supported as such.***

----

# Installation:
* Download file
* Extract to \<My Games\>\Skyrim \<Version\>\SKSE
* Make sure you have at least Python 3.3 installed on your system (See notes in Requirements)

----

# Usage:
* Double click on the python file.
* Double click on the generated reports.
* Fix issues
* Profit

### Important:

Depending on the security settings of your system, Windows might block access for the script (as it needs read/write access).
Be sure to give it the according permission, if required, there will be a notification right of the clock in the windows taskbar.

Also, if the script / exe fails to execute, please send me the console output and the original crashlog.

https://www.youtube.com/watch?v=SFw9HArJ-QI

----

# Experimental:
- Allthough I'm able to read multiple code languages, I've never written anything in python.
- Basicly, this is my "Hello World"


----

# License:
GNU GPL v2 --> [LICENSE](./LICENSE)


----

# Credits
- Bethesda for Skyrim
- the Ostim community for their guide on how to read the Crashlogs and providing me textfiles with notes on solutions.
