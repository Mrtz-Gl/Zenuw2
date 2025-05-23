# Portable Balance Lab (PBL)

> Portable Balance Lab course material for students

The Portable Balance Lab (PBL) is a practical course that teaches students how to create their own balance lab from raw components and software. This repository contains all of the learner-facing course material.


# <a name="getting-started"></a> 🚀 Getting Started

In this course, we will work with Python. To get used to this, all lectures are delivered through Jupyter notebooks. This way, you can view, modify, and run all code samples in the Jupyter viewer (i.e. just like Matlab Livescripts).

To get started, follow these steps:

1. **Download a Copy of this Repository**:

    1. Go to the [releases](../../releases) page and download a `zip` of the latest release
       (unless a specific version is specified)
    2. Unzip the course content somewhere (e.g. on your `Desktop`)

2. **Get Jupyter**:

    1. Download and Install Anaconda: https://www.anaconda.com/products/distribution
    2. Boot the Anaconda Navigator (e.g. via the Start bar)
    3. Boot Jupyter through the navigator UI
    4. This should open Jupyter a browser window. Jupyter notebooks (`.ipynb` files) can be opened through this UI.

3. **Open a PBL Lecture**:

    1. In the Jupyter UI, browse to wherever you unzipped this repository:

        * e.g. #1 click `Downloads` then `pbl-main`
        * e.g. #2 click `Desktop` then `pbl-main`
        * e.g. #3 click `OneDrive` then `Desktop` then `pbl-main`

    2. Browse to a specific lecture `.ipynb` file

         * e.g. click `PBL start-up session (students) (21-22)` then `PBL_Lab0_Manual_2022.ipynb`

Once you are satisfied that you can load a Jupyter notebook, you can then go through the course materials.


# 👩‍🏫 Course Materials

The course material is split into lectures (`L`), sensor practicals (`S`), and extra content (`X`):

- You should go through all lectures (`L1`, `L2`, **and** `L3`)
- You will be assigned one of four possible practicals (`S1`, `S2`, `S3`, **or** `S4`)
- All practicals require setting up a Raspberry Pi (`S0`)
- Some practicals may ask you to go through extra content (`X`)


## `L`: Lectures

It is recommended that you go through all of the lecture material (`L1`-`L3`). These ensure you know enough Python to get through the practical material (`S1`-`S5`).

> **⚠️ Warning ⚠️**: You should open the lecture's Jupyter notebooks (`.ipynb` files) in your own local copy of this repository (see: [Getting Started](#getting-started)). The preview links here don't let you *run* the example code.

| ID | Title |
| -- | ----- |
| L1 | [Python: Basics](L1_PythonBasics/L1_PythonBasics.ipynb) |
| L2 | [Python: functions, classes, and writing files](L2_PythonClassesAndWritingFiles/L2_PythonClassesAndWritingFiles.ipynb) |
| L3 | [Python: GUIs and Hardware Interfacing](L3_PythonGUIsAndHardware/L3_PythonGUIsAndHardware.ipynb) |


## `S`: Sensor Practicals

You will be asigned one of four possible lab practicals (`S1`-`S4`). All lab practicals require setting up the Raspberry Pi (`S0`). After setting up the Raspberry Pi, you only need to use the materials related to the practical you have been assigned (`S1`-`S4`).

| ID | Title | Notes |
| -- | ----- | ----- |
| S0 | [Set up the Raspberry Pi](S0_SetUpRaspberryPi/S0_SetUpRaspberryPi.ipynb) | **All lab practicals (`S1`-`S4`) require doing this first** |
| S1 | [Pose Estimation](S1_PoseEstimation/S1_PoseEstimation.ipynb) | |
| S2 | [IMU](S2_IMU/S2_IMU.ipynb) | |
| S3 | [Force Plate](S3_ForcePlate/S3_ForcePlate.ipynb) | |
| S4 | [EMG](S4_EMG/S4_EMG.ipynb) | |


## `X`: eXtra Content

These materials are extra notes/examples that parts of the course may refer to.

| ID | Title | Notes |
| -- | ----- | ----- |
| X0 | [Software Setup](X0_SoftwareSetup/README.md) | Explains how the software used in the PBL course is setup |
| X1 | [Writing CSV Files](X1_WritingCSVFiles/X1_WritingCSVFiles.ipynb) | Explains how to write CSV data to a file |
| X2 | [Generating Timestamped Filenames](X2_GeneratingTimestampedFilenames/X2_GeneratingTimestampedFilenames.ipynb) | Explains how to generate timestamped filenames |


# F&Q

### Where is the Schedule?

This repository only contains core course materials. Schedules should be made available by your teachers via their teaching platform of choice (e.g. in TU Delft, Brightspace).

# Acknowledgements

The PBL lab wouldn't be possible without organization and support from a bunch of people. Here's an
alphabetical list of some of them:

- Reinier van Antwerpen (R.vanAntwerpen@tudelft.nl): Hardware support (3D printing), 2022 & 2023
- Jacques Brenkman (J.A.Brenkman@tudelft.nl): Hardware support (electronics and PCB design), 2023
- Judith Cueto Fernandez (@JudCF, j.cuetofernandez@tudelft.nl): Teaching Assistant, 2023
- Jinne Geelen (@JinneGeelen, J.E.Geelen@tudelft.nl): Founding lab designer and implementer, 2022
- Koen Jongbloed (k.j.p.jongbloed@outlook.com): Teaching Assistant, 2022; Hardware support, 2023
- Adam Kewley (@adamkewley, a.kewley@tudelft.nl): Software support and open-sourcing, 2022 & 2023
- Eline van der Kruk (@evanderkruk, E.vanderKruk@tudelft.nl): Course lecturer, 2022 & 2023
- Janne Luijten (@JanneLuijten, j.a.m.luijten@tudelft.nl): Teaching Assistant, 2022 & 2023 - Teacher, 2024
- Fred Roeling (f.q.c.roeling@tudelft.nl): IT and networking support, 2022 & 2023
