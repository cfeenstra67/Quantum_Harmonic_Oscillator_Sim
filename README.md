There are two ways to download this program.

The first would be to download the Windows executable (.exe) directly and run it directly.  Be warned, however, that the file is very large, about 200MB.  Also, it does take a considerable amount of time (~15 seconds) to boot up.  If you aren't worried about storage, however, this is probably the easier option.

The second is to run the python script directly.  In order to do this, you must have python 3 installed on your machine.  The oldest version I've tested it with is python 3.4.2, however it should work fine with any version of python 3. You should also have pip installed.  In order to install the necessary packages, it's a good idea to create a virtual environment where you can install them and easily remove them later if desired.  First, you should download the "script" folder, and from a Terminal or Command Prompt ```cd``` to the folder on your machine (ex. ```cd ~/Downloads/script/```).  Then:

1. Create a virtual environment using ```virtualenv <name>```.  For Mac: use ```venv <name>```, you won't be able to run the script properly otherwise.
2.  Activate the virtual environment: ```source <virtualenv name>/bin/activate```
3.  Install the required packages: ```pip3 install -r requirements.txt```
4.  Run the script! ```python3 QHO_Demo.py``` (or, if you'd like to run it in the background and continue using your command line: ```python3 QM_Demo.py &```
5.  When you're done, deactivate the virtual environment using simply ```deactivate```.

If you don't mind having the packages installed on your machine for future use, just do 3&4.
