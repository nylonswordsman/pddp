import sys
import pynput
import playsound
import os
import time
import json

import signal
import threading
import multiprocessing
import asyncio

#import random
os.environ['SDL_AUDIODRIVER'] = 'dsp'



"""* these variables are ANSI escape codes. when the're read in a
string they tell the terminal to ignore them and start applying a
certain modification to the text after them instead of printing
like normal
* these ones are for color. im going to use them to make the text
all pretty instead of boring black and white
* the variables won't be actually used for code but as shorthand
to make my time writing the dialogue easier
* i cant directly use the codes in the dialogue in the disc file
because they contain escape characters like backslashes which .json
files Do Not Like to contain as it turns out"""

##### NOT WINDOWS
#escRed = '\033[31m'      ## corresponds to 'STARTRED' in dialogue
#escGreen = '\033[32m'  ## corresponds to 'STARTGREEN' in dialogue
#escGold = '\033[33m'     ## corresponds to 'STARTGOLD' in dialogue
#escBlue = '\033[34m'     ## corresponds to 'STARTBLUE' in dialogue
#escPurple = '\033[1;35m' ## corresponds to 'STARTPURPLE' in dialogue
#escCyan = '\033[1;36m' ## corresponds to 'STARTCYAN' in dialogue
#escGrey = '\033[37m' ## corresponds to 'STARTGREY' in dialogue
#escEnd = '\033[m'        ## corresponds to 'ENDCOLOR' in dialogue
### stop code for the color escape codes
#escClick = '\a'          ## corresponds to 'CLICKSOUND' in dialogue
### makes a click sound
#escNewline = '\n'        ## corresponds to 'NEWLINE' in dialogue
### performs a line break

#### WINDOWS
escRed = '\x1b[1;31m'      ## corresponds to 'STARTRED' in dialogue
escGreen = '\x1b[32m'  ## corresponds to 'STARTGREEN' in dialogue
escGold = '\x1b[33m'     ## corresponds to 'STARTGOLD' in dialogue
escBlue = '\x1b[1;34m'     ## corresponds to 'STARTBLUE' in dialogue
escPurple = '\x1b[1;35m' ## corresponds to 'STARTPURPLE' in dialogue
escCyan = '\x1b[1;36m' ## corresponds to 'STARTCYAN' in dialogue
escGrey = '\x1b[37m' ## corresponds to 'STARTGREY' in dialogue
escEnd = '\x1b[m'        ## corresponds to 'ENDCOLOR' in dialogue
## stop code for the color escape codes
escClick = '\a'          ## corresponds to 'CLICKSOUND' in dialogue
## makes a click sound
escNewline = '\n'        ## corresponds to 'NEWLINE' in dialogue
## performs a line break

"""START{color} (like STARTRED or STARTGOLD) place an escape code
in dialogue and names. these codes will cause the text ahead of
them to be written in that color. ENDCOLOR will "stop" the currently
happening escape caused by the color code, returning text ahead
of it to default. use them like opening and closing parenthesis
to make certain sections of lines have color.
example: "I am STARTGOLDnot a human beingENDCOLOR!" prints the 'not
a human being' part in gold but still prints the exclamation mark
in normal black."""




currentDisc = {
    "No Disc": "There is no disc."
}

"""* the current "phase" of the wider playback/disc
* holds the current conversation or debate or what have you
* normally its considered bad practice to do what ive done here
and nest dictionaries in an array in a dictionary, but it's just
python doing a bunch of printing. it will be fine.
* should not impact performance unless you are running this on
ENIAC or something"""
currentPhase = {
    "blank": "The phase is blank."
  }
  
"""* the index of the next phase to go to within the current disc
after the current phase is finished.
* starts at 0 so it will always initialize first (initialization
phase should always be first/0th in the disc)"""
nextPhaseIndex = 0

"""the index of the line within the current phase.
keeps track of where you are in the phase"""
lineIndex = 0

allEvidence = [
    "No evidence is here.",
    "There is not any evidence.",
    "There is no evidence."
    ]
availableEvidence = [
    "availableEvidence is empty."
    ]
availableEvidenceIndex = 0

influence = 4.0

phaseInProgress = False

counterLines = {
    "Blank": "There are no counter lines."
}

failDiscussion = [
    "failDiscussuon is blank."
    ]


""""unwrap" the escape codes by replacing the written codes (like
STARTBLUE or ENDESCAPE) with their ANSI escape code counterparts"""
def unwrap(wrappedString):
    wrappedString = wrappedString.replace("STARTRED", escRed)
    wrappedString = wrappedString.replace("STARTGREEN", escGreen)
    wrappedString = wrappedString.replace("STARTGOLD", escGold)
    wrappedString = wrappedString.replace("STARTBLUE", escBlue)
    wrappedString = wrappedString.replace("STARTPURPLE", escPurple)
    wrappedString = wrappedString.replace("STARTCYAN", escCyan)
    wrappedString = wrappedString.replace("STARTGREY", escGrey)
    wrappedString = wrappedString.replace("ENDCOLOR", escEnd)
    wrappedString = wrappedString.replace("CLICKSOUND", escClick)
    wrappedString = wrappedString.replace("NEWLINE", escNewline)
    return wrappedString

"""makes the given string lowercase and strips it of unnecessary
whitespace at the ends. useful for capturing like phrases and such
because it helps make sure the user's input and the expected/
possible inputs are similar"""
def adapt(targetString):
    targetString = str(targetString.lower().strip())
    return targetString

def with_ordinal_indicator(number=int):
    ## 11, 12, and 13 all end in 'th' because English Bad
    for thing in range(11, 13):
        if number == thing:
            return (str(number) + "th")
    ## numbers with 1 at the end gain 'st'
    if str(number).endswith("1"):
        return (str(number) + "st")
    ## numbers with 2 at the end gain 'nd'
    if str(number).endswith("2"):
        return (str(number) + "nd")
    ## numbers with 3 at the end gain 'rd'
    if str(number).endswith("3"):
        return (str(number) + "rd")
    ## numbers ending with anything else gain 'th'
    else:
        return (str(number) + "th")

def say(lineToSay):
    ## alias speaker & speech to make more readable
    speaker = lineToSay["speaker"]
    speech = lineToSay["speech"]
    ## call and print pretty-ized versions of speaker and speech
    print("[" + unwrap(speaker) + "]> " + unwrap(speech))


"""* for when you want to throw an error, but you wanna make it
:sparkles: pretty :sparkles:.
* accepts a lone string, a list of strings, and a boolean
* use the lone string, the title, to indicate roughly what happened
* use the list to give some short bullet points giving more info
on what went wrong and/or to give the user an idea of what to
do next, e.g. 'Please retry after inserting disc' and stuff
* use the boolean to indicate whether the program should continue
doing what its doing or step back to the main menu"""
def throw_error(errorTitle=str, errorInfo=list, returnToPlayerMenu=bool):
    ## make a big sound (more copies of this code (\a) makes it louder. layering!)
    print('\a\a\a\a\a\a\a\a')
    ## print the title of the error prefixed with a pretty red tag...
    if errorTitle != None:
        print(escRed + "[ERROR] " + errorTitle + escEnd)
    ## ... if it's there. if it's not do nothing
    else:
        pass
    ## print every string in the list errorInfo prefixed with
    ## a pretty blue tag
    if errorInfo != None:
        for info in errorInfo:
            print (escBlue + " [i] " + escEnd + info)
    else:
        pass
    if returnToPlayerMenu == True:
        print(escGold + " [!] " + escEnd + "Returning to player menu...")
        player_menu()
    else:
        pass

"""honestly this one is kind of pointless. i just wanted to make
it more pretty :p"""
def please_wait(text=str):
    ## print the given text but with some fancy colors and a lil formatting
    text = (escBlue + " [ Please wait... | " + text + " ]" + escEnd)
    return text

def enter_to_continue(waitingMessage="(Press enter to continue...)"):
    input(escGrey + str(waitingMessage) + escEnd)
    ## fancily print a string containing two escape codes that respectively move one line up and clear the whole line
    ## (this gets rid of the message after enter is pressed)
    sys.stdout.write("\033[F\033[2K")
    


def heal_influence(healing=float):
    global influence
    ## increment influence by healing (add healing to influence)
    influence += healing
    healthBar = ""
    for pip in range(int((influence) / .5)):
            healthBar += " ■"
    visualHealing = ""
    for pip in range(int((healing) / .5)):
            visualHealing += " □"
    print(escGreen + " [ Influence Gained:" + healthBar + escBlue + visualHealing + escGreen + " (Remaining: " + str(influence + healing) + ") ]" + escEnd)
    
def damage_influence(damage=float):
    global influence
    ## decrement influence by damage (subtract damage from influence)
    influence -= damage
    healthBar = ""
    for pip in range(int((influence) / .5)):
            healthBar += " ■"
    visualDamage = ""
    for pip in range(int((damage) / .5)):
            visualDamage += " ▫"
    print(escRed + " [ Influence Lost:" + healthBar + escPurple + visualDamage + escRed + " (Remaining: " + str(influence) + ") ]" + escEnd)



def startup():
    ## what good program doesn't have a lil splash art?
    ## spaced weird so that it doesn't overlap and become unreadable in the editor
    print(escPurple + "      ╔═════════════════════════════════════════════════════╗" + escEnd)

    print(escCyan + " ═════╣ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ ║" + escEnd)

    print(escCyan + "   ╔══╣ ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ╔╦╦╦╦╝" + escEnd)
    
    print(escBlue + " ══╬══╣ ▒▒▒▒▒ [ Playback Debate Disc Player v0 ] ▒▒▒▒▒ ║" + escEnd)

    print(escCyan + "   ╚══╣ ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ╚╩╩╩╩╗" + escEnd)
    
    print(escCyan + " ═════╣ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ ║" + escEnd)

    print(escPurple + " ═════╩═════════════════════════════════════════════════════╝" + escEnd)
    
    ## say instructions
    print(escRed + "\a\a\a\n\nPlease see 'README.md' before proceeding further.\n\n" + escEnd)
    time.sleep(.3)
    player_menu() ## would go to main menu but main menu doesnt really have a use



""" this main menu code is unused. i dont really have a use for it :p"""
def main_menu():
    print(escBlue + "   [ Please select an option to continue. ] " + escEnd)
    print("1: Play a disc")
    print("2: placeholder option")
    try:
        if adapt(input()) == "1":
            player_menu()
        elif adapt(input()) == "2":
            pass
        else:
            throw_error(None, ["Please type the number corresponding to a listed option."], True)
    except ValueError:
        throw_error(None, ["Please type a number."], True)

"""* the "player" in this function's name refers to like a disc
player not like a player character
* this function handles getting the player ready to actually do
the playing of a disc file, and once its done with that it starts
reading the first phase of the disc and taking it as the starting
values and such of some things (like your evidence and influence)
* it is also supposed to instruct the user on how to insert a disc,
make sure the disc it's been given is valid, and give some tips
on how to potentially fix a disc file if it's broken but. eh."""
def player_menu():
    ## check whether or not the discs folder exists
    if os.path.exists("./discs/") == True:
        ## if it does exist and program picks it up, yay. move on
        pass
    elif os.path.exists("./discs/") != True:
        ## if it does not exist or read, oh no.
        ## tells the user it doesn't exist and tells them to make a
        ## new one and try again. also returns to main menu
        throw_error("03: The 'discs' Folder Does Not Exist!", ["Please create a new one and restart the program."], False)

    ## ask the user to type the name of a disc; store it
    discFile = str(input("Please insert a disc file into the 'discs' folder, and then enter the name of the disc file.\nType 'tutorial' for the included turorial disc.\n"))
    ## restate what the user input and confirm
    print("The disc you wish to play is:\n" + escGold + "discs/" + discFile + ".json" + escEnd)
    print("Is this correct? (\033[1;32mY\033[m/\033[31mN\033[m)") ## i tried to be fancy and hardcode these escape codes. ill fix it later when its on github
    confirmation = adapt(str(input())) ## ask for the actual confirmation; convert the input into a string and then clean it up
    ## if confirmation is negative, effectively reset the player by returning to the player menu
    if confirmation == 'n':
        print(escGold + " [!] " + escEnd + "Returning to player menu...")
        player_menu()
    ## if confirmation is affirmative, 
    elif confirmation == 'y':
        if os.path.isfile("discs/" + discFile + ".json") == True:
            print(please_wait("Please do not remove the disc."))
            print(please_wait("Loading disc..."))
            ## this is kind of convoluted but python gonna python /shrug
            ## basically load the disc *file* into the player so that
            ## python can actually use it
            discToLoad = open("discs/" + discFile + ".json", "r")
            global currentDisc
            global currentPhase
            global influence
            global allEvidence
            global nextPhaseIndex
            global counterLines
            global failDiscussion
            currentDisc = json.load(discToLoad)
            currentPhase = currentDisc[0]
            if currentPhase["phaseType"] == "initialization":
                print(please_wait("Loading initializing data..."))
                ## load misc data it will need later
                print(please_wait("Setting influence..."))
                influence = currentPhase["startingInfluence"]
                print(please_wait("Loading evidence..."))
                allEvidence = currentPhase["evidence"]
                print(please_wait("Loading counter lines..."))
                counterLines = currentPhase["counterLines"]
                print(please_wait("Loading fail discussion..."))
                failDiscussion = currentPhase["failDiscussion"]
                ## print off the titlecard
                print("\n") ## spacer
                for line in currentPhase["discTitlecard"]:
                    print(unwrap(line))
                print("\n") ## spacer
                ## print off the exposition monologue
                print(unwrap(currentPhase["exposition"]))
                transition_phase()
            else:
                throw_error("01: Invalid Initialiation phaseType!", ["The first/0th phase should always be initialization.", "The phase type value is either missing or incorrect.", "The disc may be formatted incorrectly.", "Refer to the manual for more information."], True)

        else:
            throw_error("That path does not contain a disc!", ["Please retry after inserting the disc.", "Ensure you typed the disc's name exactly right.", "Do not include the extention ('.json').", "The file's name is case-sensitive."], True)
    else: ## throw an error if user inputs something that isnt 'y' or 'n'
        throw_error("Unexpected input!", ["Please try again.", "Use 'y' or 'n'."], True)



def transition_phase():
    ## prepare self by grabbing global variables. if it doesnt do this python gets confused and assumes we're trying to create new variables which makes it throw a KeyError and/or ValueError at runtime
    global lineIndex
    global availableEvidenceIndex
    global currentDisc
    global currentPhase
    global nextPhaseIndex
    ## reset most of the variables controlling indexes of things
    ## to prevent skipping into the middle of things or crashing
    lineIndex = 0
    availableEvidenceIndex = 0
    ## increment nextPhaseIndex by 1 so that it equals the next
    ## phase instead of the one we just switched to
    nextPhaseIndex += 1
    ## load the next phase by its index
    currentPhase = currentDisc[nextPhaseIndex]
    ## really missing match statements right now...
    ## check what type of phase the current one is and prepare accordingly
    if currentPhase["phaseType"] == "discussion":
        ## splash text
        print(escGrey + "\n        ═   ═   ═  ═ ═ ═ ═ ═ ═  ═   ═   ═")
        print("                " + escEnd + with_ordinal_indicator(nextPhaseIndex) + " - Discussion" + escGrey + "          ")
        print("                  Listen close...")
        print("        ═   ═   ═  ═ ═ ═ ═ ═ ═  ═   ═   ═" + escEnd + "\n")
        ## call handler for discussion phases
        enter_to_continue()
        discussion()
    elif currentPhase["phaseType"] == "choice":
        ## splash text
        print(escRed + "\n        ═   ═   ═  ═ ═ ═ ═ ═ ═  ═   ═   ═")
        print("                  " + escEnd + with_ordinal_indicator(nextPhaseIndex) + " - Choice" + escRed + "          ")
        print("                Choose carefully...")
        print("        ═   ═   ═  ═ ═ ═ ═ ═ ═  ═   ═   ═" + escEnd + "\n")
        ## call handler for choice phases
        choice(True)
    elif currentPhase["phaseType"] == "mass_debate":
        ## splash text
        print(escPurple + "\n        ═   ═   ═  ═ ═ ═ ═ ═ ═  ═   ═   ═")
        print("               " + escEnd + with_ordinal_indicator(nextPhaseIndex) + " - Mass Debate" + escPurple + "          ")
        print("            Comprehend, countermand...")
        print("        ═   ═   ═  ═ ═ ═ ═ ═ ═  ═   ═   ═" + escEnd + "\n")
        ## call handler for mass debate phases
        enter_to_continue()
        mass_debate(True)
#    #these dont work yet
#    elif currentPhase["phaseType"] == "split_debate":
#        pass
#    elif currentPhase["phaseType"] == "closing_argument":
#        pass
#    elif currentPhase["phaseType"] == "rebuttal":
#        pass
    elif currentPhase["phaseType"] == "initialization":
        throw-error("Unexpected Initialization Phase!", ["An initialization phase was started out of order.", "Initialization should always be the 0th phase.", "Never call initialization more than once.", "Refer to the manual for more information."])
    else:
        throw_error("Invalid phase type!", ["The phaseType value is either missing or incorrect.", "The disc may be formatted incorrectly.", "Refer to the manual for more information."], True)

def restart_phase():
    ## reset most of the variables controlling indexes of things
    ## to prevent skipping into the middle of things or crashing
    global lineIndex
    global availableEvidenceIndex
    lineIndex = 0
    availableEvidenceIndex = 0
    ## call the handler for the current phase type, restarting it
    global currentPhase
    exec(currentPhase["phaseType"] + "(False)")

def deadlock():
    global failDiscussion
    ## splash text
    print(escPurple + "\n        ═   ═   ═  ═ ═ ═ ═ ═ ═  ═   ═   ═")
    print("                 " + escEnd + "XXth - Deadlock" + escPurple)
    print("           There's nothing you can say...")
    print("        ═   ═   ═  ═ ═ ═ ═ ═ ═  ═   ═   ═" + escEnd + "\n")
    deadlockLineIndex = 0
    endThreshold = ((len(failDiscussion)) - 1)
    while deadlockLineIndex <= endThreshold:
        if deadlockLineIndex < endThreshold:
            say(failDiscussion[deadlockLineIndex])
            ## use the length of the line in characters divided by a number and converted to a float (for more precision) as the amount of time in seconds to wait before timing out. number is bigger here to enhance dramatic effect
            deadlockWaitTimeConstant = 16
            time.sleep(float(len(failDiscussion[deadlockLineIndex]["speech"])/deadlockWaitTimeConstant))
            ## increment deadlockLineIndex to continue
            deadlockLineIndex += 1
        elif deadlockLineIndex == endThreshold: ## ask if you want to restart when it hits the threshold
            say(failDiscussion[deadlockLineIndex])
            break
    ## wait for the player's input to close
    enter_to_continue("(Press enter to close...)")
    sys.exit()
    


def discussion():
    ## start the yapping part of the discussion
    discussion_iterator = threading.Thread(target=iterate_through_discussion(currentPhase), name='DiscussionIterator')
    ## start the thing that watches for input during discussion
    discussion_overseer = threading.Thread(target=oversee_discussion(), name='DiscussionOverseer')
#    await asyncio.gather([iterate_through_discussion(currentPhase), oversee_discussion(currentPhase)])

def iterate_through_discussion(thisPhase):
    global lineIndex
    global phaseInProgress
    ## restart threshold equals length of this phase in lines.
    ## -1 because arrays/lists start counting from 0 and len() starts counting from 1
    restartThreshold = (len(thisPhase["lines"]) - 1)
    phaseInProgress = True
    while phaseInProgress:
        while lineIndex <= restartThreshold:
            ## transition to next phase when it hits the threshold
            if lineIndex == restartThreshold:
                say(thisPhase["lines"][lineIndex])
                enter_to_continue("(Press enter to proceed...)")
                transition_phase()
            else:
                say(thisPhase["lines"][lineIndex])
            ## use the length of the line in characters divided by a number and converted to a float (for more precision) as the amount of time in seconds to wait before timing out
            discussionWaitTimeConstant = 30.0
            time.sleep(float(len(thisPhase["lines"][lineIndex]["speech"])/discussionWaitTimeConstant))
#            time.sleep(.2) ##comment out the above two lines and uncomment this one to make testing more tolerable
            ## increment lineIndex to continue
            lineIndex += 1

def oversee_discussion():
    global phaseInProgress
    while phaseInProgress:
        pass
        ## sift through events for key presses, and sift through those for space or enter specifically
#        for event in pygame.event.get():
#            if event.type == pygame.KEYDOWN:
#                if event.key == pygame.K_SPACE:
#                    print("space pressed")
#                if event.key == pygame.K_RETURN:
#                    print("enter pressed")
        ## cap fps at 30 because anything beyond that is simply unnecessary
#        clock.tick(30)


def choice(intro=bool):
    global currentPhase
    global counterLines
    global failDiscussion
    if intro == True:
        print(escRed + " > [ " + currentPhase["prompt"] + " ] < " + escEnd)
    iterationNumber = 1
    for choice in currentPhase["choices"]:
        print(escRed + "  [ " + str(iterationNumber) + " : ]  " + escEnd + choice)
        iterationNumber += 1
    try:
        guess = int(input(escGrey + "Choose by number...\n" + escEnd))
        if (guess - 1) < 0:
            sys.stdout.write("\x1b[F\x1b[2K")
            for iteration in range(iterationNumber):
                sys.stdout.write("\x1b[F\x1b[2K")
            restart_phase()
        if (guess - 1) >= iterationNumber:
            sys.stdout.write("\x1b[F\x1b[2K")
            for iteration in range(iterationNumber):
                sys.stdout.write("\x1b[F\x1b[2K")
            restart_phase()
    except IndexError:
        sys.stdout.write("\x1b[F\x1b[2K")
        for iteration in range(iterationNumber):
            sys.stdout.write("\x1b[F\x1b[2K")
        restart_phase()
    except ValueError:
        sys.stdout.write("\033[F\033[2K")
        for iteration in range(iterationNumber):
            sys.stdout.write("\x1b[F\x1b[2K")
        restart_phase()
    try:
        if currentPhase["responses"][guess - 1] == "CORRECTANSWER":
            say(counterLines["AgreeSuccess"])
            heal_influence(1)
            transition_phase()
        else:
            say(currentPhase["responses"][guess - 1])
            time.sleep(.6)
            print("\a\a\a\a")
            damage_influence(1)
            time.sleep(1)
    except IndexError:
        sys.stdout.write("\x1b[F\x1b[2K")
        for iteration in range(iterationNumber):
            sys.stdout.write("\x1b[F\x1b[2K")
        restart_phase()
    except ValueError:
        sys.stdout.write("\x1b[F\x1b[2K")
        for iteration in range(iterationNumber):
            sys.stdout.write("\x1b[F\x1b[2K")
        restart_phase()
    ## start failure sequence if influence is less than or equal to 0
    if influence <= 0.0:
        deadlock()
    else:
        restart_phase()


def mass_debate(intro=bool):
    ## intro
    if intro == True:
        ## let the teacher know this stuff is broken as hell
        print(escRed + "\nsorry, mass debate doesn't work. no time to work on it\nit acts like basically a discussion but broken a little which isnt how its supposed to work\ni know for a fact its broken as hell but eh. what am i gonna do. hopefully it passes\n" + escEnd)
        ## nab the specific evidence for this phase
        global availableEvidence
        global currentPhase
        availableEvidence = currentPhase["availableEvidence"]
        ## print out a representation
        for evidence in availableEvidence:
            print("\a\a\a" + intro_truth_bullet(evidence))
            time.sleep(.4)
        time.sleep(2)
        # threading attempt
    ## start the yapping part of the debate
    mass_debate_iterator = threading.Thread(target=iterate_through_mass_debate(currentPhase), name='MassDebateIterator')
    ## start the thing that watches for input during debate
    mass_debate_overseer = threading.Thread(target=oversee_mass_debate(currentPhase), name='MassDebateOverseer')
    mass_debate_iterator.start()
    mass_debate_overseer.start()
#        # asyncio attempt
#    await asyncio.gather(*[iterate_through_mass_debate(currentPhase), oversee_mass_debate(currentPhase)])
        # multiprocessing attempt
#    mass_debate_iterator = multiprocessing.Process(target=iterate_through_mass_debate(currentPhase))
#    mass_debate_overseer = multiprocessing.Process(target=oversee_mass_debate(currentPhase))
#    mass_debate_iterator.start()
#    mass_debate_overseer.start()
#    mass_debate_iterator.join()
#    mass_debate_overseer.join()


def iterate_through_mass_debate(thisPhase):
    global lineIndex
    global phaseInProgress
    ## reset lineIndex just in case
    lineIndex = 0
    ## restart threshold equals length of this phase in lines.
    ## -1 because arrays/lists start counting from 0 and len() starts counting from 1
    restartThreshold = (len(thisPhase["lines"]) - 1)
    phaseInProgress = True
    while phaseInProgress:
        while lineIndex <= restartThreshold:
            ## restart phase when it hits the threshold
            if lineIndex == restartThreshold:
                say(thisPhase["lines"][lineIndex])
                time.sleep(2.5)
                phaseInProgress = False
                closing_thought(thisPhase)
            else:
                say(thisPhase["lines"][lineIndex])
            ## debate phases use a fixed amount of time instead of depending on the length of the lines. 
            ## this is because having unpredictable timing is bad when you have to time things right
            time.sleep(2.5)
            ## increment lineIndex to continue
            lineIndex += 1
    print("iterator ended")

def oversee_mass_debate(thisPhase):
    global lineIndex
    global phaseInProgress
    global availableEvidence
    global availableEvidenceIndex
    while phaseInProgress:
        pass
        ## sift through events for key presses, and sift through those for space or enter specifically
#        for event in pygame.event.get():
#            if event.type == pygame.KEYDOWN:
#                if event.key == pygame.K_SPACE:
#                    print("space pressed")
#                    ## if you're on the last evidence wrap back around to the first evidence
#                    if availableEvidenceIndex == len(availableEvidence):
#                        availableEvidenceIndex = 0
#                    else:
#                        availableEvidenceIndex += 1
#                    print(truth_bullet(availableEvidence[availableEvidenceIndex]))
#                if event.key == pygame.K_RETURN:
#                    print("enter pressed")
#        ## cap fps at 30 because anything beyond that is simply unnecessary
#        clock.tick(30)
    print("overseer ended")


"""this is used to make debates more pretty"""
def truth_bullet(evidence):
    global availableEvidence
    global availableEvidenceIndex
    bullet = (escCyan + "►  │[ " + escBlue + evidence + escCyan + " (" + str(availableEvidenceIndex+1) + "/" + str(len(availableEvidence)) + ") ] > »" + escEnd)
    return bullet

"""like truth_bullet() but it doesnt display the index"""
def intro_truth_bullet(evidence):
    global availableEvidence
    bullet = (escCyan + "►  │[ " + escBlue + evidence + escCyan + " ] > »" + escEnd)
    return bullet

"""this in particular is a roundabout way to prevent input from the
player when i dont want them to when restarting"""
def closing_thought(thisPhase):
    closingThoughtLineIndex = 0
    restartThreshold = (len(thisPhase["closingThought"]) - 1)
    closingThoughtInProgress = True
    while closingThoughtInProgress:
        while closingThoughtLineIndex <= restartThreshold:
            ## restart phase when it hits the threshold
            if closingThoughtLineIndex == restartThreshold:
                say(thisPhase["closingThought"][closingThoughtLineIndex])
                time.sleep(2.5)
                enter_to_continue("Press enter...")
                restart_phase()
            else:
                say(thisPhase["closingThought"][closingThoughtLineIndex])
            ## debate phases use a fixed amount of time instead of depending on the length of the lines. 
            ## this is because having unpredictable timing is bad when you have to time things right
            time.sleep(2.5)
            ## increment lineIndex to continue
            closingThoughtLineIndex += 1




#class DiscussionInputWatcher:
#    timeoutTime = 0.1
#    def timeOut():
    

#        input_watcher = DiscussionInputWatcher()
#        threading.Thread(target=input_watcher, name='DiscussionInputWatcher')
#        input_watcher.timeoutTime = float(len(entry["speech"])/13)
#        print(input_watcher.timeoutTime)


#def discussion_watch_for_input(timeoutTime):
#    timeoutTimer()

    ## aliasing time.time(). threadTime represents the amount of time the thread has existed for, as a float
#    threadTime = time.time()
    ## while the amount of time the thread has existed for is less than the time it takes for it to time out, do the following
    ## in other words while it hasn't timed out yet, do the following
#    while threadTime <= timeoutTime:
#        print(str(threadTime))
    
#    ## call for the player to put in an input
#    playerInput = input()
#    ## if player input is JUST the enter key print enter
#    if playerInput == '':
#        print('enter')
#    ## if player input is EXACTLY space + enter print space + enter
#    elif playerInput == ' ':
#    ## if it was neither of those report bad input
#    else:
#        print('bad input')

#### ==================== on program start
#threading.Thread(target=watch_for_input(), name='InputWatcher')
startup()