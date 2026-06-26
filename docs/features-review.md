# Features Review

Short review of all implemented features.

## Desktop App Shell

**Panel:** Full app window.
**Ubication in UI:** Whole screen.
**Functionality:** Opens the built frontend inside a desktop window.
**Description:** Starts a local media server, creates the API bridge, and loads the app UI.
**Related services:** Backend `ApiBridge`, `VideoStreamServer`; frontend `ServiceRegistry`.
**Click road:** Run app -> desktop window opens.

## Resizable Layout

**Panel:** Main workspace.
**Ubication in UI:** Left tools, center stage, right inspector, bottom timeline.
**Functionality:** Resize panels.
**Description:** Drag vertical or horizontal dividers to change panel size.
**Related services:** Frontend `App.vue`, `ResizeHandler`.
**Click road:** Drag divider between panels.

## Load Video Or Image

**Panel:** Center stage toolbar.
**Ubication in UI:** Upload button and empty stage button.
**Functionality:** Load a local video or image.
**Description:** User can choose media from the desktop file picker or browser file input.
**Related services:** Backend `ApiBridge.choose_media_file`, `VideoStreamServer`; frontend `VideoTimelineService`, `ProjectDataService`.
**Click road:** Center stage -> upload icon -> choose file.

## Media Playback

**Panel:** Center stage toolbar.
**Ubication in UI:** Bottom toolbar under the video.
**Functionality:** Play, pause, seek, frame step, go start.
**Description:** Controls current time for the loaded video. Images get a default 10 second duration.
**Related services:** Frontend `VideoTimelineService`, `MediaStage`.
**Click road:** Center toolbar -> play, step, back, forward, start buttons.

## Playback Speed

**Panel:** Center stage toolbar.
**Ubication in UI:** Speed slider at left side of stage toolbar.
**Functionality:** Change playback speed.
**Description:** User can set speed from 0.25x to 4x.
**Related services:** Frontend `VideoTimelineService`.
**Click road:** Center toolbar -> speed slider.

## Time Edit

**Panel:** Center stage toolbar.
**Ubication in UI:** Time label in stage toolbar.
**Functionality:** Jump to typed time.
**Description:** Click the time text, type seconds or time format, and apply with Enter or blur.
**Related services:** Frontend `VideoTimelineService`, `MediaStage`.
**Click road:** Center toolbar -> click time -> type value -> Enter.

## Stage Zoom And Pan

**Panel:** Center stage.
**Ubication in UI:** Video canvas area and `100%` button.
**Functionality:** Zoom, pan, reset zoom.
**Description:** Mouse wheel zooms the media. Space/right-click drag pans when zoomed. `100%` resets.
**Related services:** Frontend `MediaStage`.
**Click road:** Wheel on stage -> hold Space and drag -> click `100%`.

## Stage View Modes

**Panel:** Center stage toolbar.
**Ubication in UI:** View switch: `Canvas`, `Split`, `2D`.
**Functionality:** Switch media view.
**Description:** Show video canvas only, video plus 2D court, or only 2D court.
**Related services:** Frontend `MediaStage`, `Court2DView`, `MeasureService`.
**Click road:** Center toolbar -> click `Canvas`, `Split`, or `2D`.

## Draw Tools

**Panel:** Left Tools panel.
**Ubication in UI:** `Draw` tab.
**Functionality:** Draw shapes over media.
**Description:** Supports free line, straight line, polyline, triangle, square, polygon, and circle.
**Related services:** Frontend `DrawItemsService`, `ProjectDataService`; backend `ProjectDataService`.
**Click road:** Left panel -> `Draw` -> choose tool -> drag on video.

## Draw Style

**Panel:** Left Tools panel.
**Ubication in UI:** `Draw` tab under active tool settings.
**Functionality:** Set color, opacity, and width.
**Description:** New draw items use the selected style.
**Related services:** Frontend `DrawItemsService`.
**Click road:** Left panel -> `Draw` -> set color, opacity, width.

## Polyline Finish

**Panel:** Center stage.
**Ubication in UI:** Video canvas.
**Functionality:** Create multi-point lines.
**Description:** Each click adds a point. Enter or clicking outside finishes the polyline.
**Related services:** Frontend `DrawItemsService`, `MediaStage`.
**Click road:** Left panel -> `Draw` -> polyline -> click points -> Enter.

## Item Selection

**Panel:** Center stage and right inspector.
**Ubication in UI:** Click item on canvas or item row.
**Functionality:** Select an overlay item.
**Description:** Selected items show handles and editable fields.
**Related services:** Frontend `DrawItemsService`, `MeasureService`, `InspectorPanel`.
**Click road:** Click overlay item or Right panel -> `Items` -> click row.

## Move And Edit Draw Items

**Panel:** Right Inspector and center stage.
**Ubication in UI:** `Items` tab and canvas handles.
**Functionality:** Move items and edit points.
**Description:** Move whole shapes, drag points, resize circles, edit oval height, and rotate ovals.
**Related services:** Frontend `DrawItemsService`, `InspectorPanel`, `MediaStage`.
**Click road:** Right panel -> `Items` -> move/cursor button -> drag on canvas.

## Item Visibility

**Panel:** Right Inspector.
**Ubication in UI:** `Items` tab eye button.
**Functionality:** Show or hide an item.
**Description:** Hidden items do not display on the stage or export.
**Related services:** Frontend `ProjectDataService`, `DrawItemsService`, `MeasureService`.
**Click road:** Right panel -> `Items` -> eye icon.

## Item Delete

**Panel:** Right Inspector.
**Ubication in UI:** `Items` tab trash button.
**Functionality:** Delete an item.
**Description:** Removes the selected item from the project. Deleting a measure grid also removes related measure lines.
**Related services:** Frontend `DrawItemsService`; backend `ProjectDataService`.
**Click road:** Right panel -> `Items` -> trash icon.

## Item Style Editing

**Panel:** Right Inspector.
**Ubication in UI:** `Items` tab expanded item.
**Functionality:** Edit label, color, width, opacity, fill mode, fill opacity.
**Description:** Changes saved item appearance and names.
**Related services:** Frontend `DrawItemsService`, `ProjectDataService`.
**Click road:** Right panel -> `Items` -> expand item -> edit fields.

## Measure Grid

**Panel:** Left Tools panel and center stage.
**Ubication in UI:** `Measure` tab, Grid button.
**Functionality:** Add real field calibration grid.
**Description:** Adds a 4-point grid used to convert image points to real meters.
**Related services:** Frontend `MeasureService`, `ProjectDataService`.
**Click road:** Left panel -> `Measure` -> Grid.

## Measure Dimensions

**Panel:** Left Tools panel.
**Ubication in UI:** `Measure` tab, `AB m` and `AC m`.
**Functionality:** Set real field size.
**Description:** Updates grid width and height in meters.
**Related services:** Frontend `MeasureService`.
**Click road:** Left panel -> `Measure` -> edit `AB m` or `AC m`.

## Chess Grid

**Panel:** Right Inspector.
**Ubication in UI:** `Items` tab, measure grid settings.
**Functionality:** Show chess grid overlay.
**Description:** Draws an 8x8 projected grid inside the calibrated field.
**Related services:** Frontend `MeasureService`, `MediaStage`.
**Click road:** Right panel -> `Items` -> expand Measure Grid -> check `Chess grid`.

## Linear Measure

**Panel:** Left Tools panel and center stage.
**Ubication in UI:** `Measure` tab, Linear measure button.
**Functionality:** Measure distance in meters.
**Description:** Draws a line and displays measured meters using the grid calibration.
**Related services:** Frontend `MeasureService`, `MediaStage`, `Court2DView`.
**Click road:** Left panel -> `Measure` -> Linear measure -> drag on video.

## Chrono

**Panel:** Left Tools panel and center stage.
**Ubication in UI:** `Measure` tab, Chrono button.
**Functionality:** Add timer overlay.
**Description:** Shows elapsed time during the item time range.
**Related services:** Frontend `MeasureService`, `VideoTimelineService`; backend `VideoEditorService`.
**Click road:** Left panel -> `Measure` -> Chrono.

## Delay

**Panel:** Left Tools panel and right Inspector.
**Ubication in UI:** `Measure` tab Delay button; `Items` tab delay fields.
**Functionality:** Add freeze delay in playback/export time.
**Description:** Adds a paused segment and shows a pause indicator during that range.
**Related services:** Frontend `MeasureService`, `VideoTimelineService`; backend `VideoEditorService`.
**Click road:** Left panel -> `Measure` -> Delay -> edit in Right panel `Items`.

## Player Marker

**Panel:** Left Tools panel and center stage.
**Ubication in UI:** `Players` tab, Player button.
**Functionality:** Add player marker.
**Description:** Places a plus marker on the video and maps it to the 2D court.
**Related services:** Frontend `MeasureService`, `Court2DView`; backend `VideoEditorService`.
**Click road:** Left panel -> `Players` -> Player -> click on video.

## Ball Marker

**Panel:** Left Tools panel and center stage.
**Ubication in UI:** `Players` tab, Ball button.
**Functionality:** Add ball marker.
**Description:** Places a ball marker on the video and maps it to the 2D court.
**Related services:** Frontend `MeasureService`, `Court2DView`; backend `VideoEditorService`.
**Click road:** Left panel -> `Players` -> Ball -> click on video.

## Team And Marker Style

**Panel:** Left Tools panel and right Inspector.
**Ubication in UI:** `Players` tab colors and marker size; `Items` tab selected player.
**Functionality:** Set team colors, ball color, marker size, and team.
**Description:** Updates player and ball marker look.
**Related services:** Frontend `MeasureService`, `ProjectDataService`.
**Click road:** Left panel -> `Players` -> edit colors/size; or Right panel -> `Items` -> team fields.

## 2D Court View

**Panel:** Center stage.
**Ubication in UI:** `Split` or `2D` view.
**Functionality:** Show top-down court.
**Description:** Shows court lines, measured lines, player dots, ball dot, and chrono using the calibration grid.
**Related services:** Frontend `Court2DView`, `MeasureService`, `VideoTimelineService`.
**Click road:** Center toolbar -> `Split` or `2D`.

## Events

**Panel:** Right Inspector and center toolbar.
**Ubication in UI:** `Events` tab and Add event button.
**Functionality:** Add, edit, jump, delete, and clear events.
**Description:** Stores event labels at current time. Active event is highlighted near the playhead time.
**Related services:** Frontend `EventsService`, `ProjectDataService`; backend `ProjectDataService`.
**Click road:** Right panel -> `Events` -> Add event / Jump / Delete.

## Timeline Playhead

**Panel:** Bottom Timeline.
**Ubication in UI:** Time ruler and red cursor.
**Functionality:** Scrub current time.
**Description:** Drag playhead to change current time. Playback pauses while dragging.
**Related services:** Frontend `TimelinePanel`, `VideoTimelineService`.
**Click road:** Bottom timeline -> drag playhead.

## Timeline Display Mode

**Panel:** Bottom Timeline.
**Ubication in UI:** Header button `Show frames` / `Show time`.
**Functionality:** Switch ruler labels.
**Description:** Shows time labels or frame labels at 30 fps.
**Related services:** Frontend `TimelinePanel`.
**Click road:** Bottom timeline -> `Show frames` or `Show time`.

## Timeline Scale

**Panel:** Bottom Timeline.
**Ubication in UI:** Header `Scale` slider.
**Functionality:** Zoom timeline width.
**Description:** Increases or decreases timeline horizontal scale.
**Related services:** Frontend `TimelinePanel`.
**Click road:** Bottom timeline -> Scale slider.

## Timeline Item Bars

**Panel:** Bottom Timeline.
**Ubication in UI:** Rows under the time ruler.
**Functionality:** Move or trim item time range.
**Description:** Drag bar to move item. Drag left/right handles to change start/end.
**Related services:** Frontend `TimelinePanel`, `ProjectDataService`.
**Click road:** Bottom timeline -> drag item bar or bar handle.

## Timeline Event Markers

**Panel:** Bottom Timeline.
**Ubication in UI:** Small markers on ruler.
**Functionality:** Jump to event.
**Description:** Click event marker to move playhead to event time.
**Related services:** Frontend `TimelinePanel`, `EventsService`.
**Click road:** Bottom timeline -> click event marker.

## Cut Range

**Panel:** Right Inspector.
**Ubication in UI:** `Cut` tab, From and To fields.
**Functionality:** Set export range.
**Description:** User can type times or set From/To from current playhead time.
**Related services:** Frontend `CutService`, `VideoTimelineService`, `ProjectDataService`.
**Click road:** Right panel -> `Cut` -> edit From/To or click `Now`.

## Cut Export

**Panel:** Right Inspector.
**Ubication in UI:** `Cut` tab, Save cut button.
**Functionality:** Export a video clip.
**Description:** Saves an MP4 clip with visible overlays, speed option, quality option, and delay handling.
**Related services:** Backend `VideoEditorService`, `ApiBridge`; frontend `CutService`.
**Click road:** Right panel -> `Cut` -> set range -> `Save cut`.

## Export Progress And Cancel

**Panel:** Right Inspector.
**Ubication in UI:** `Cut` tab during export.
**Functionality:** Show progress, estimated time, and cancel export.
**Description:** Polls backend export status every 500 ms. User can cancel active export.
**Related services:** Backend `VideoEditorService`; frontend `CutService`.
**Click road:** Right panel -> `Cut` -> Save cut -> Cancel.

## Open Export Folder

**Panel:** Right Inspector.
**Ubication in UI:** `Cut` tab after export.
**Functionality:** Open output folder.
**Description:** Opens Windows Explorer at the exported clip folder.
**Related services:** Backend `ApiBridge.open_path_in_explorer`; frontend `CutService`.
**Click road:** Right panel -> `Cut` -> `Open in Explorer`.

## Project Auto Save

**Panel:** Whole app.
**Ubication in UI:** Behind all edits.
**Functionality:** Save project data.
**Description:** Saves events, items, measure data, and cut data to a JSON file next to the media file.
**Related services:** Backend `ProjectDataService`; frontend `ProjectDataService`.
**Click road:** Load media -> edit any feature -> saved automatically.

## Local Media Streaming

**Panel:** Backend support.
**Ubication in UI:** Used by loaded media in center stage.
**Functionality:** Serve local video/image to frontend.
**Description:** Streams media over localhost with range request support for video playback.
**Related services:** Backend `VideoStreamServer`, `ApiBridge`; frontend `VideoTimelineService`.
**Click road:** Upload/select local media -> media appears in stage.

## Legacy Bookmark API

**Panel:** Backend API only.
**Ubication in UI:** No active UI panel found in current frontend.
**Functionality:** Save and load bookmark lists.
**Description:** Backend can store `.bookmarks.json` files, but current UI uses Events instead.
**Related services:** Backend `BookmarkService`, `ApiBridge`; frontend old `BookmarkService`.
**Click road:** Not exposed in current main UI.

## Legacy Drawing API

**Panel:** Backend API only.
**Ubication in UI:** No active UI panel found in current frontend.
**Functionality:** Save and load drawing JSON files.
**Description:** Backend can store `.drawings.json` files. Current implemented overlay data is saved in project JSON.
**Related services:** Backend `DrawService`, `ApiBridge`; frontend `DrawItemsService`.
**Click road:** Not exposed as separate current UI action.
