# Panels

## Distribution
```
tools | video/canvas | events/items/cut
-----------------------------------
timeline
```




# Panel: Tools

visible in: DRAW_MODE
position: top-left

A set of buttons that allow to select different draw tools:
- free line
- straight line
- polyline
- triangle
- square
- polygon
- circle

A default configuration before add an element to the canvas:
line width, color, etc..

By click on canvas panel a element will be added


# Panel: Video
visible in: PLAY_MODE
position: top-center

display the video
in this panel is a toobar in bottom position inside the panel with:
- velocity control: range 0.25 - 4
- play buttons:
    - second back
    - second forward
    - frame back
    - frame forward
    - play
    - play backwards direction reproduction

- current time
- button add events
- button cut video
- button DRAW_MODE activate

# Panel: Canvas
Allow to draw in a layer
visible in: DRAW_MODE
position: top-center

display the video
in this panel is a toobar in bottom position inside the panel with:
- velocity control: range 0.25 - 4
- play buttons:
    - second back
    - second forward
    - frame back
    - frame forward
    - play
    - play backwards direction reproduction

- current time
- from time - to time  (editable)
- button PLAY_MODE activate

# Panel: Events
visible always: on click in Tab
position: top-right

List o saved events
- name of the event (editabe on click)
- from time
- button: jump to, on click jump the time to the from_time
- 
# Panel: Cut
visible always: on click in Tab
position: top-right

Allow to save a selected range of video
- time_from (input + current timeline time)
- time_to (input) >  button Now in same row, pass the current timeline time to the input
- save button: filename same as original video with date_from in name

# Panel: Items
visible always: on click in Tab
On click on a item in the time line item, the items will be displayed, and his properties
Buttons:
- move: by drag move the position of the element in the canvas, relative on lcik button position on screen 

# Panel: Timeline
Display a timeline of the video time
list of elements
list of events o the time
