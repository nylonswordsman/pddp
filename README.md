# General Synopsis
* this is basically open-source text-based "we have danganronpa class trial at home" that you can make your own trials for
* really easy to use, theres no programming involved you just open jsoneditoronline and follow the template and you're good to amke a whole trial kind of

## Resources
* [jsoneditoronline](https://jsoneditoronline.org)   < what ive been using to make and edit discs
* [the github repo for this project](https://github.com/nylonswordsman/pddp)

## Todo
* make input work
* music/sfx
* either instructions or a script for making windows 10 powershell process ansi escape codes correctly
* viewing evidence descriptions somehow
* rebuttal
* split debate
* closing argument
* template disc
* maybe a disc validation script where you hand it a disc and it reads through and checks for obvious errors? low priority

## Making Discs
* i will write tips and such and conventions for making discs that i use
* you dont have to use them but its recommended because it makes it easier for players

### When to use colors
* Gold generally indicates important things people say in discussion phases and potential weak spots in debate phases
* A character's thoughts are indicated by grey text and being surrounded by parenthesis

### Validating a Disc
instructions for making sure your disc will like. work lol
* make sure initialization is the 0th phase, and that there are no more initialization phases than that
* make sure you have at least 1 piece of evidence in all your debates
* `phaseType` is case sensitive; make sure the `phaseType` values are *not* capitalize
* make sure the color codes you put have the end code after the portions you want colored
* make sure your disc file is titled correctly and does not have any spaces or unusual characters in it
* make sure your disc file is in the `discs` folder (the code will not check anywhere else in the directory for discs)
* playtest it of course. the previous steps will simply help catch broken things before you have to even troubleshoot them

### Troubleshooting

#### Error Codes, What They Mean, and What To Do
* *01: Invalid Initialization phaseType*: the first (0th) phase of the disc didn't have the `phaseType` value `initialization`. make sure it's spelled right, that it's *not* capitalized, and that it's the 0th phase according to the disc's index (NOT the phase indicator's! the index of the phase in the disc file)
* *03: 'discs' Folder Not Found*: when the program went to check for the discs folder, it didn't find it. create a folder under `pddp` and title it 'discs', then put your disc files in it. or alternatively redownload the discs folder in the repo and put it there and then put your discs in there.


## Credits
### Code
below is a list of everyone who has contributed to this project's code. contributors can feel free to add their names or usernames here
* -nylonswordsman

### Discs
below is a list of discs and their authors. feel free to add your disc's title and your name or username if you add a disc
* (there are no disc files at present.)

### Music/SFX
all of the songs and sounds in this repo (out of the box anyway) were stolen from the Danganronpa series' OST and files. below is a table of the songs as listed in the folder, their actual titles, the artists who made them, and the games they are from. the sound effects are just listed, cuz i ripped them from Spriter's Resource's sound section
* i, nylonswordsman, own ABSOLUTELY NONE of this music.
insert markdown table
