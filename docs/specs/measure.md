# Measure tool


on the left panel add a Tab "Measure"
Tools on the panel

1) Field vertices:
x4 vertices to delimite the field with x,y inputs and move active button
Segments real dimensions x2 inputs AB, AC:
   A-----B
   |     |
   C-----D
allow to set the real dimension in meters

2) Tools
- Lineal mesaure:
 based on the real proportions and the pixel dimension, allow to dra a straig line and a real measurement label in the center of the line is displayed




# Perspective Measurement Correction

## Problem

The current implementation appears to assume a uniform pixel-to-meter scale across the image. This approach is not mathematically correct when the camera view contains perspective distortion.

In a perspective projection:

* 100 pixels near the camera do not represent the same real-world distance as 100 pixels farther away.
* Distances measured directly in image coordinates become increasingly inaccurate depending on their position within the frame.

## Required Solution

Implement a **planar homography (projective transformation)** using the four corners of the playing field.

### Calibration

The user defines four corresponding points:

```ts
const imagePoints = [
  A, // top-left corner in image
  B, // top-right corner in image
  C, // bottom-left corner in image
  D, // bottom-right corner in image
];
```

And the real-world dimensions:

```ts
const fieldWidth = 28.65;  // meters
const fieldHeight = 15.24; // meters
```

These correspond to the real-world coordinate system:

```ts
const worldPoints = [
  [0, 0],
  [28.65, 0],
  [0, 15.24],
  [28.65, 15.24],
];
```

Using these point pairs, compute a homography matrix that transforms:

```txt
Image coordinates (x, y)
          ↓
World coordinates (X, Y) in meters
```

## Distance Measurement

Before calculating any distance, convert both image points into world coordinates:

```ts
const p1World = imageToWorld(p1);
const p2World = imageToWorld(p2);
```

Then calculate the distance in the real-world coordinate system:

```ts
const distance = Math.sqrt(
  (p2World.x - p1World.x) ** 2 +
  (p2World.y - p1World.y) ** 2
);
```

## Scope

The system only needs to support measurements on the ground plane (court, field, rink, etc.).

No height estimation or 3D reconstruction is required.

## Expected Result

Measurements between any two points located on the playing surface should remain accurate regardless of their position in the image, even when strong perspective distortion is present.

## Implementation Notes

If OpenCV is available, use:

* `cv.findHomography()`
* `cv.perspectiveTransform()`

instead of applying linear scale factors directly to screen coordinates.

The homography should be computed once during calibration and reused for all subsequent measurements.
