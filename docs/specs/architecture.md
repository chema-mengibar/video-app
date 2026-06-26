# Data
By open a video file,
a file will be created for the sorage fo events and layers.
Events ar time markers with a label, time_from
Layers or items containe a visual drawed elements that will be displayed in the aplicaction in front the video:
lines, polygons, circles as visual elements for analyse video and actions.


By open a video will be check if a file exist
same name of the video + `.json`
jsn data will be loaded and can be edited by backend and frontend.
The process to save data can be evaluated, each x seconds, or on change with bouncing.

# Services

Backend adn fronted are structured by domain services:
- Draw Service
- Marks /Events Service
- TimeLine Video reprodccion Service
- Save Video Cut