# Animation And Keyframes

## Current State

The keyframe animation base is implemented, but it should not be considered fully reliable for all item types yet.

Canvas and 2D items can read their geometry from keyframes at the current timeline time. Video playback and item animation should run in parallel.

## Expected User Behavior

- If the user moves an element and then creates a keyframe, the current position is saved in that keyframe.
- If the playhead is already on an existing keyframe and the user moves the element, that keyframe is updated automatically.
- Moving between keyframes does not automatically create a new keyframe.

## Items That Should Work

- Players and ball: position.
- Measure lines: line points.
- Measure grid: grid vertices, dimensions, and padding.
- Straight lines, polylines, triangles, squares, and polygons: vertices.
- Circles: center, radius, height, and rotation.
- Free lines: simple path points.

## Known Limits

- Selected items are edited from their base geometry, so editing and animated preview can diverge between keyframes.
- Free-line interpolation only supports simple `M` and `L` SVG path commands.
- Circle projection between Canvas and 2D is approximate because radius is stored in image space.
- Animated grid projection can move other projected elements in ways that may surprise the user.
- Non-geometric properties are not animated yet: color, opacity, width, label, team, visibility, and time range.
- The implementation has build validation, but still needs full manual testing across all item types.

## Recommendation

Treat this as a first working version. Before calling it complete, test each item type in Canvas and 2D:

1. Create item.
2. Create first keyframe.
3. Move playhead.
4. Move item.
5. Create or update second keyframe.
6. Play timeline.
7. Check Canvas and 2D behavior.
