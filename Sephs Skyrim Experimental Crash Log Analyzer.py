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
### Imports
######################################
import os
import os.path
import sys
import datetime
import time
import re

#import platform

######################################
### Initialize Global Variables 
######################################
global thisReport, REPORT, thisLOG, LOG
global thisMEM, thisFile, thisFileAdd, thisAssembler
global script_name, script_version, script_date
global RAM, STACK, REGISTERS
global list_ignores, high_chance
list_ignores = ["skse64_loader.exe", "SkyrimSE.exe"]
high_chance = ["skee64.dll", "Trishape", "Ninode", "mesh" ]
script_name = "SSE CLA - Sephs Skyrim Experimental Crash Log Analyzer"
script_version = "0.2"
script_date = "2023.04.23"
REPORT = ""
thisMEM = ""
thisFile = ""
thisFileAdd = ""
thisAssembler = ""
RAM = ""
STACK = ""
REGISTERS = ""

######################################
### Functions : Tools
######################################
# Actualy write the report
def f_Report_Save(REPORT, thisReport):
    with open(thisReport, 'w') as file:
        file.write(REPORT)


# Clear
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


# Return the timestamp
def s_get_time():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


# Get 1 input
def s_get_input(msg):
    # Loop until the user enters exactly 1 character
    while True:
        # Prompt the user to enter input
        user_input = input(msg)

        # Check that the input is exactly 1 character
        if len(user_input) == 1:
            return user_input

# Warn if possible RAM issue:
def s_issue_ram(LOG):
    RAM = "\n"
    match = re.search(r'PHYSICAL MEMORY: (\d+\.\d+) GB/(\d+\.\d+) GB', LOG)
    if match:
        used_ram = float(match.group(1))
        available_ram = float(match.group(2))

        # Check if the RAM usage is in the 1.5 GB range of the available RAM
        if abs(used_ram - available_ram) <= 1.5:
            RAM += "# RAM (critical):\n***There is a very high chance that the main reason for the crash was lack of ram: " + str(used_ram) + "/" + str(available_ram) + "***"
        elif abs(used_ram - available_ram) <= 2.0:
            RAM += "# RAM (maybe, probably not):\n*Allthough unlikely, there is a slim chance that the crash might have happend due to lack of ram: " + str(used_ram) + "/" + str(available_ram) + "*"
        else:
            RAM += "# RAM (all good):\n*It is absolute unlikely that the crash was due to RAM.*"
        RAM += "\n"
    return RAM

# Continue
def my_continue():
    input("Press [ENTER] to continue")


def f_file_input():
    # Ask the user to enter the filename or drag and drop the file
    file_path = input("Enter the filename or drag and drop the file here: ").strip('"')
    # Check if the file exists
    if not os.path.isfile(file_path):
        # If the filename does not include a path, check if it exists in the same directory as the script
        if os.path.isfile(os.path.join(os.path.dirname(__file__), file_path)):
            file_path = os.path.join(os.path.dirname(__file__), file_path)
        # Check if the file exists with an absolute path
        elif os.path.isabs(file_path) and os.path.isfile(file_path):
            pass
        else:
            print("File not found. Please provide the absolute path to the file.")
            return f_file_input()
    # Return the file path
    return os.path.abspath(file_path)


######################################
### Functions : Menu
######################################
def p_menu_main(filename=None):
    if not filename:
        filename = f_file_input()
    if not filename:
        print("No filename provided. Exiting in 5 seconds...")
        time.sleep(5)
        exit()
    while True:
        clear_console()
        p_print_menu_header()
        s_issue_ram(thisLOG)
        print("\n==== Main Menu ====")
        print("1. Call")
        print("2. Register")
        print("3. Stack")
        print("4. Show Report")
        print("5. Save Report")
        print("6. Exit")
        choice = s_get_input("Enter your choice: ")
        if choice == "1":
            s_parse_CallStack(filename)
            my_continue()
        elif choice == "2":
            s_parse_Register(filename)
            my_continue()
        elif choice == "3":
            s_parse_Stack(filename)
            my_continue()
        elif choice == "4":
            p_Report_Show()
            my_continue()
        elif choice == "5":
            f_Report_Save(REPORT,thisReport)
            print("Report saved to: "+thisReport)
            my_continue()
        elif choice == "6":
            exit()
        else:
            print("Invalid choice. Please choose again.")


######################################
### Functions : Print Stuff
######################################

# Print a reusable header
def p_print_menu_header():
    print(script_name+" ("+script_version+") / "+script_date)
    print("-------------------------------------------------------------------------\n")

# Prints the provided text to console, interpreting markdown syntax.
def p_console_MD(text):
    bold = '\033[1m'
    italic = '\033[3m'
    underline = '\033[4m'
    reset = '\033[0m'

    lines = text.split('\n')
    for line in lines:
        if line.startswith('#'):
            level = min(line.count('#'), 6)
            header_text = line[level:].strip()
            header_line = '=' * len(header_text)
            print(f'{bold}{header_text}{reset}\n{bold}{header_line}{reset}')
        elif line.startswith('---'):
            print('-' * 80)
        else:
            line = line.replace('**', bold).replace('__', underline).replace('*', italic)
            print(line)

def p_Report_Show():
    print(thisLOG)


######################################
### Functions : Parsing
######################################
# Parse the header of the crash log
def s_parse_Header():
    global thisMEM, thisFile, thisFileAdd, thisAssembler, thisLOG
    REPORT = "___C R A S H L O G  -  R E P O R T___\n\n"
    REPORT += "Original:\t"+thisLOG+"\n"
    with open(thisLOG) as f:
        for i in range(12):
            line = f.readline()
            if "Skyrim " in line:
                REPORT += "GameVer:\t"+line+"\n"
            elif "Unhandled exception" in line:
                parts = line.split(" at ")
                subparts = parts[1].split(" ")
                
                thisMEM = subparts[0]
                thisFile = subparts[1].split('+')[0]
                thisFileAdd = subparts[1].split("+")[1][:6]
                thisAssembler = parts[1].split("\t")[1]
            elif "physical memory" in line:
                break
            else:
                pass
    # Indicators
    REPORT += "\n# Indicators\n- Address: "+thisMEM+"\n- File: "+thisFile+"\n- Add: "+thisFileAdd+"\n- Assembler: "+str(thisAssembler)+"\n----\n"

    return REPORT


# Parse the Call Stack section
def s_parse_CallStack(LOG):
    global thisMEM, thisFile, thisFileAdd, thisAssembler, list_ignores, high_chance
    calls = [thisMEM.strip(), thisFile.strip(), thisFileAdd.strip(), thisAssembler.strip()]

    REPORT = "\n\n# Probable Call Stack\n"
    REPORT_HC = ""
    match = re.search(r'PROBABLE CALL STACK:\s*\n(.*?)(?=REGISTERS:)', LOG, re.DOTALL)

    if match:
        stack = match.group(1)
        for call in calls:
            if call in list_ignores:
                REPORT += f"{call}\n\t\t*Ignored because it is unlikely the cause! (part of: list_ignores)*\n\n"
                continue

            VAR = ""
            call_pattern = re.compile(call, re.IGNORECASE)
            count = 0
            for line in stack.split('\n'):
                if call_pattern.search(line):
                    VAR = line.strip()
                    count += 1
            if count > 1:
                REPORT += f"{call}:\n\tFound {count} occurrences\n\t**NOTE:**\n\t*Only because this file appeared often does not mean it was the cause, it might just have been 'the final straw' to 'break the camels back'!*\n\n"
                if call in high_chance:
                    REPORT += f"\t--> *Very high chance of causing the issue! (its from the main indicators above and also part of: high_chance)* <--\n"
            elif count == 1:
                REPORT += f"{call}:\n\t{VAR}\n\n"
            else:
                REPORT += f"{call}\n\tNo occurrences of were found in Call Stack\n\n"

        hc_set = set()
        for pattern in high_chance:
            hc_pattern = re.compile(pattern, re.IGNORECASE)
            for line in stack.split('\n'):
                if hc_pattern.search(line) and pattern not in hc_set:
                    REPORT_HC += f"{pattern}\n\t*High chance of causing the issue! (part of: high_chance)*\n"
                    hc_set.add(pattern)

        if REPORT_HC:
            REPORT += "# Call Stack : High Chances\n"
            REPORT += REPORT_HC

    REPORT += "----\n"
    return REPORT


# Parse the register section
def s_parse_Register(LOG):
    REPORT = ""
    match = re.search(r'REGISTERS:\s*\n(.*)', LOG, re.DOTALL)
    if match:
        registers_section = match.group(1)
        register_lines = registers_section.split('\n')

        # Loop through all the lines in the "REGISTERS:" section and parse each line
        for line in register_lines:
            pass
    return REPORT


######################################
### Parse log file
######################################

p_print_menu_header()
if len(sys.argv) > 1:
    # Loop through all arguments except the first one (which is the script name)
    for arg in sys.argv[1:]:
        thisLOG = arg
        with open(thisLOG, 'r') as f:
            LOG = f.read()
        
        thisReport = thisLOG.replace(".log", "_report.md")
        REPORT = ""
        thisMEM = ""
        thisFile = ""
        thisFileAdd = ""
        thisAssembler = ""
        REPORT = s_parse_Header()
        REPORT += s_issue_ram(LOG)
        REPORT += s_parse_Register(LOG)
        REPORT += s_parse_CallStack(LOG)
        print(REPORT)
    my_continue()
else:
    # Retrieve filename for menu use:
    thisLOG = f_file_input()
    thisReport = thisLOG.replace(".log", "_report.md")
    print(thisLOG)
    my_continue()
    REPORT = ""
    thisMEM = ""
    thisFile = ""
    thisFileAdd = ""
    thisAssembler = ""
    s_issue_ram(thisLOG)
    # Show Menu
    p_menu_main(thisLOG)
    my_continue()
