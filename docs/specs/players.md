# Players

Add A Tab Players in the left side panel, after Measure.


In Tab Players:
- add a button (Player) that  place  a "+" in the canvas video.
- add a button (Ball) that  place  a "+" in the canvas video.
   
Ball Block has a color picker.
By changing the color picker, all the ball items from the list change the color automatically


Player item in 2d view is a circle with the team color
Ball item in 2d view is a circle with the  color o color picke from Item panel
 

By adding a player:
- an Item is added to the list Items and timeline.
  Add label to the shape +.
  Name of Items will be displayed small on the canvas video
- an Item `Ball` is added to the list Items and timeline.
  

# Teams a colors
In Players Panel on the left side
there is a block `Teams` headline
and 2 colors pickes for Guest and Home teams


By adding a player, in the right panel,  by Player item is posible to edit
- label: free input text, for letters, name or number of player
- team select : dropdown: guest, home 


# 2D/ 3D

If not allready implementd
Add a 3 state switch element in the `.media-stage__actions`
The switch control and split the `.media-stage__video`
- left state : canvas-video
- right state: 2d aereal representation of the drawed field and players positioned based on the grid proyection.
   players ars dots with same Item coor as in the Items panels. and position is based on Items and timeline.
   chrono element is displayed on the 2d view too, straigline measures items are displayed too.
   no other draw elements are displayed, draw elements, are no displayed, just measure elements
- center stated: splited view, sinchronized by moving Items position, and change proyection playes and mesaure elements


RULES
Keep components clear





