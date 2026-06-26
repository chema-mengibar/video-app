# Grid Propagation

## Goal

Add a new optional feature called **Grid Propagation**.

The application already supports field calibration using four vertices (A, B, C, D) and a homography transform.

The current Grid tool only visualizes the calibrated rectangle.

The new feature should extend the calibrated area into an infinite world grid.

## UI

Add a checkbox below the existing Grid Item in Items panel to activate the feature.:
Add 2 inputs: for number of propagation by axis.
add a 3x3 square buttons, to set the direccion of the propagation, set the origin

For example: center
```
| | | |
-------
| |x| |
-------
| | | |
-------
```


For example: current rectangle isthe top-right corner limit
```
| | |x|
-------
| | | |
-------
| | | |
-------
```


```txt
☑ Grid Propagation
```

When enabled, the application should generate additional grid cells outside the calibrated rectangle.

## Behavior

The calibrated rectangle represents a known world area:

```txt
B ---- D
|      |
|      |
A ---- C
```

For example:

```txt
AB = 60m
AC = 30m
```

This rectangle becomes the origin tile.

When Grid Propagation is enabled, create neighboring tiles in all directions using the same world coordinate system.

Example:

```txt
+----+----+----+
|    |    |    |
+----+----+----+
|    |CAL.|    |
+----+----+----+
|    |    |    |
+----+----+----+
```

## Implementation

Do not recalculate perspective.

Do not compute new vanishing points.

Do not extend image-space edges.

Use the existing homography.

Generate additional world-space coordinates outside the calibrated area and project them using the existing worldToImage() transformation.

Example:

```ts
for (let x = -120; x <= 180; x += 10) {
  ...
}

for (let y = -90; y <= 120; y += 10) {
  ...
}
```

The projected lines should naturally follow the existing perspective because the homography is already applied.

## Rendering

Draw:

* vertical grid lines
* horizontal grid lines
* optional cell labels

Only render lines that intersect the visible canvas.

## Configuration

Add settings:

```txt
Grid Size (m)
[ 1 ]
[ 2 ]
[ 5 ]
[10 ]

Grid Propagation
☑ Enabled
```

## Expected Result

The user calibrates a single rectangle.

The application automatically visualizes a much larger perspective-correct grid around that rectangle, allowing players and measurements to be placed outside the original calibration area while remaining in the same world coordinate system.
