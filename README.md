# Faceblur
A simple python script to detect and blur faces in images.
Made using [face_recognition](https://github.com/ageitgey/face_recognition) for the heavy lift and [PyQt5](https://pypi.org/project/PyQt5/) for the GUI

<img src="img/Faceblur-screenshot.png " width="400" />

For better usability the script can be turned into a desktop app using [Fbs](https://build-system.fman.io), the only prerequisite is
Python 3.5 or 3.6. Python 3.7 is not yet officially supported.


## Setup
Open the terminal and clone this repo:

    git clone https://github.com/tommasoltrz/FaceBlur.git

move into the repo directory:

    cd FaceBlur

Create a virtual environment in the current directory:

    python3 -m venv venv

Activate the virtual environment:

    # On MacOS
    source venv/bin/activate

Install the required libraries:

    pip3 install fbs PyQt5==5.9.2 Pillow numpy face_recognition

## Run the script
You can either directly run the script:

    python3 ./src/main/python/main.py

or you can use Fbs (recommended):

    fbs run

## Turn it into an app
If everything works correctly with `fbs run` you can proceed to freeze the script into an app

    fbs freeze

Test it using the command you'll get. for Mac:

    target/Faceblur.app/Contents/MacOS/Faceblur

You can now see your app in the target folder

## Troubleshooting
If you get the error `unable to open .../your-path/shape_predictor_68_face_landmarks.dat` simply copy and paste the folder `face_recognition_models folder` from your virtual environment into the app

    cp -R .../your-path//FaceBlur/venv/lib/python3.6/site-packages/face_recognition_models .../your-path/FaceBlur/target/Faceblur.app/Contents/MacOS

## Create installer
In order to make it easy to share you can create an installer by running

    fbs installer

## Credits
Most of this project was possible thanks to these tutorials:

[fbs-tutorial](https://build-system.fman.io)

[PyQt5-tutorial](https://build-system.fman.io/pyqt5-tutorial)


