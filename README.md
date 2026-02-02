## Mesh library for Blender

## Overview
This add-on offers quick and easy access to old 3D-models, 
enabling them to be searched through categorized libraries and imported directly into the active
work file, all without leaving the current workspace.

##### Note: This project started back in 2021 and I continued it in my data structures course in 2025. <br >Since then Blender has added new feature that makes this add-on unnecessary but it still is a pet project of mine I might return to at some point in the future.


## Installation

### Prerequisites
Blender 2.8 or newer is installed.
You have existing mesh library. Library files in this repository are mock files that are meant to demonstrate the use of this add on, they contain only primary meshes like cubes and spheres. 
The mesh library files and mesh names should match to the expamples given in my_mesh_library files in this repository for the searches to work. 

##### Note: This installation is written for Blender version 4.3.2.


1. On line 455 in my_library_add_on.py alter the file path to match the path to folder containing your mesh library.
2. Open blender and navigate to edit -> preferences.
3. Open add-ons and choose install from disk.

## Use guide 

- Open up the menu by pressing ”N” key, or by small arrow on right hand side.
- When clicking a category, pop up should open and choosing a model from a list, it should bring it in view.
- You can delete object by selecting (edge turns yellow or orange) and press x or delete.
- Options is by default closed, But through it you can add a new category, first give a name in inputfield, 
then select a parent category for it from the dropdown. 
- Press create and list should update automatically. Might need two clicks.
