#!/usr/bin/python3
"""Test script to convert modelines to dot, lines and timmings in us.

This script converts a standard modeline into the
calculated output required to generate a mcu resolution.
This script was used for testing purposes
during a live event on:
Twitch https://www.twitch.tv/kabukiflux
"""

import shlex

__author__ = "KabukiFlux"
__project__ = "ModelineCalculator"
__copyright__ = "Copyright 2023, KabukiFlux"
__license__ = "MIT"
__version__ = "1.0.0"
__status__ = "Development"


# ***************** HOW TO **************************************************************
# 1- check the readme file for more info
# 2- execute and send the modeline via the command line
# ***************************************************************************************

class VideoMode:
    """videomode class"""

    hfrequency = 0.0
    vfrequency = 0.0

    def __init__(self, videomode):
        self.vm = videomode
        self.dot = videomode.copy()
        self.timings = videomode.copy()
        self.calculatedotsandlines()
        self.calculatetimings()

    # Print videomode values
    def show(self):
        if self.vm["interlace"] == 1:
            # What can I say? What do you expect in 2 hours?
            print("Unable to calculate interlaced yet")
        else:
            # Print the resulting dictionary
            print("********************** Calculated params: ********************************")
            for key, value in self.vm.items():
                dotlines = "dots" if key in ["hfront", "hsync", "hback", "hres"] else "lines"
                if value != self.timings[key]:
                    print(f"   {key:7}: {value:4} ** {self.dot[key]:4} {dotlines:5} ** {self.timings[key]} μs")
                else:
                    print(f"   {key:7}: {value} ")
            print(f"   Horizontal frequency: {round(VideoMode.hfrequency, 4):11} Hz, aprox {round(VideoMode.hfrequency, 1):8} Hz ")
            print(f"     Vertical frequency: {round(VideoMode.vfrequency, 2):11} Hz, aprox {round(VideoMode.vfrequency, 0):8} Hz")
            print("******************** END Calculated params: ******************************")
            print("****REMEMBER: you can change 'hfront' 'hback' to center horizontally *****")
            print("************* you can change 'vfront' 'vback' to center vertically *******")
            print("************* in those cases the sum of both must be equal as before *****")
            print("**************************************************************************\n")

    def calculatedotsandlines(self):
        self.dot["hfront"] = self.vm["hfront"] - self.vm["hres"]
        self.dot["hsync"] = self.vm["hsync"] - self.vm["hfront"]
        self.dot["hback"] = self.vm["htotal"] - self.vm["hsync"]
        self.dot["vfront"] = self.vm["vfront"] - self.vm["vres"]
        self.dot["vsync"] = self.vm["vsync"] - self.vm["vfront"]
        self.dot["vback"] = self.vm["vtotal"] - self.vm["vsync"]

    def calculatetimings(self):
        # Clock in Hz
        dotclock = float(self.vm["pxclk"]) * 1000000
        # Period in Us
        dotperiod = (1 / dotclock) * 1000000
        # Horizontal Frequency
        VideoMode.hfrequency = (dotclock / self.vm["htotal"])
        # Vertical Frequency
        VideoMode.vfrequency = (dotclock / (self.vm["htotal"] * self.vm["vtotal"]))
        # Dot timings in Us
        horizontal = ["hres", "hfront", "hsync", "hback", "htotal"]
        for values_horizontal in horizontal:
            self.timings[values_horizontal] = self.dot[values_horizontal] * dotperiod

        # Line timings in Us
        lineperiod = self.dot["htotal"] * dotperiod
        vertical = ["vres", "vfront", "vsync", "vback", "vtotal"]
        for values_vertical in vertical:
            self.timings[values_vertical] = self.dot[values_vertical] * lineperiod


class RetrieveData:
    """retrieve data class"""

    def __init__(self):
        self.modelineoptions = {}

        # Parameters (missing Htotal and Vtotal)
        self.parameters = [
            "mdln", "desc", "pxclk", "hres", "hfront", "hsync", "hback",
            "vres", "vfront", "vsync", "vback"
        ]

        # Specify the special parameters to detect
        self.special_parameters = ["-hsync", "+hsync", "-vsync", "+vsync", "interlace"]

        # Initialize the values for hpol, vpol, and interlace
        self.hpol = 0
        self.vpol = 0
        self.interlace = 0
        self.htotal = 0
        self.vtotal = 0

    def getinputdata(self):
        print("********* Copy the modeline and paste it on the next input: **************")
        user_input = input(f"Enter modeline: ")
        values = shlex.split(user_input)

        for values_special in values:
            if values_special.lower() in self.special_parameters:
                if values_special.lower() == "+hsync":
                    self.hpol = 1
                elif values_special.lower() == "+vsync":
                    self.vpol = 1
                elif values_special.lower() == "interlace":
                    self.interlace = 1

        # Create the dictionary
        for i in range(len(self.parameters)):
            if i < len(values):
                values_special = values[i]
                if values_special.startswith('"') and values_special.endswith('"'):
                    # Remove the quotes for string values and store in lowercase
                    values_special = values_special[1:-1].lower()
                else:
                    # Convert non-quoted values to lowercase
                    if values_special.isnumeric():
                        values_special = int(values_special)
                    else:
                        values_special = values_special.replace(",", ".")
                        values_special = values_special.lower()
                self.modelineoptions[self.parameters[i]] = values_special

        if "hback" in self.modelineoptions:
            self.htotal = self.modelineoptions["hback"]
        if "vback" in self.modelineoptions:
            self.vtotal = self.modelineoptions["vback"]

        self.modelineoptions["htotal"] = self.htotal
        self.modelineoptions["vtotal"] = self.vtotal

        # Add hpol, vpol, and interlace to the dictionary
        self.modelineoptions["hpol"] = self.hpol
        self.modelineoptions["vpol"] = self.vpol
        self.modelineoptions["interlace"] = self.interlace
        return self.modelineoptions


if __name__ == '__main__':
    rx_data = RetrieveData()
    options = rx_data.getinputdata()

    vm = VideoMode(options)
    vm.show()
