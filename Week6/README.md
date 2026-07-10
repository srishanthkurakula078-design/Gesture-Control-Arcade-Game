
# Week 6 (Gesture Controlled Snake Game)

This week you will integrate your gesture detection logic from Weeks 3-4 with the keyboard Snake game from Week 5. The result will be a fully gesture-controlled Snake game.

Everything about the game logic (grid, snake movement, food, score, rendering) was already explained in the Week 5 README. This README focuses on **what changed** i.e. the gesture detection, how it connects to the game, and how the two parts work together as one merged loop.

---

## NOTE

The code below is provided for your reference so that nothing feels abstract. We would recommend you to try your own gesture logic (you can even use different gestures to move the snake, to pause, resume or to restart.)

---

## Demo Video

To watch the final outcome, click [here](https://drive.google.com/file/d/10evb8SchauuTJZxf2N66SNIeY0uLaQMB/view?usp=sharing)
> Please convert the .mov file to .mp4 if you are unable to open it

---

## How Gesture + Game Integration Works

There are different ways to combine gesture detection with a game. Here are the two most common:

### Approach 1: Merged Single Loop (what we used)

Both webcam processing and game logic run inside one `while True` loop, one after another every frame.

```
while True:
    → read webcam frame
    → detect gesture
    → update direction based on gesture
    → move snake
    → draw game
    → show webcam window
```

Simple to understand and write, easy to debug since everything happens in sequence, and works perfectly for Snake since it is a slow-paced game. The only tradeoff is that the game speed is tied to the webcam frame rate (~18fps when a hand is visible). For Snake this is completely fine.

### Approach 2: Threading (Advanced concept)

Gesture detection runs in a background thread that continuously updates a shared variable. The game loop reads that variable independently at its own speed.

```
Thread 1 (background):          Thread 2 (main):
→ read webcam frame             → read shared_gesture
→ detect gesture          →→→   → move snake
→ update shared_gesture         → draw game at 60fps
→ repeat                        → repeat
```

Smoother gameplay since the game runs at full 60fps regardless of MediaPipe's speed. However it involves `threading` and shared variables. It is an advanced concept. In our project we will follow Approach 1. You can try this on your own if you want, but only after completing Approach 1. 

---

## The Key Insight

> The game does not care where direction commands come from. In Week 5, `direction` was set by arrow keys. This week, `direction` is set by gesture output instead. Everything else in the game stays exactly the same.

---

## Code Walkthrough: What's New in Week 6

The Week 5 code explained the game logic in detail. Below is a focused explanation of every new line added this week for gesture integration.

---

### New Imports

```python
import cv2 as cv
import mediapipe as mp
import math
```

`cv2` handles the webcam capture and the separate "Vision Tracking Feedback" window that shows your hand. `mediapipe` does the hand detection. `math` is needed for `atan2` and `degrees`, the angle calculation behind pointing direction detection. 

---

### MediaPipe Setup

```python
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode
```

These four lines create short variable names for deeply nested MediaPipe classes so we don't have to type the full path every time. This is the same pattern from your `landmarks.py` nothing new here.

```python
options = HandLandmarkerOptions(
    base_options = BaseOptions(model_asset_path = "hand_landmarker.task"),
    running_mode = VisionRunningMode.IMAGE,
    num_hands = 1
)
```

Configures the hand detector. `model_asset_path = "hand_landmarker.task"` loads the pre-trained MediaPipe model from the same folder as the script. `VisionRunningMode.IMAGE` means we manually feed one frame at a time inside the loop (simplest mode). `num_hands = 1` limits detection to one hand. It is a cleaner gesture logic and avoids confusion with two-hand input.

---

### Webcam Initialization

```python
cap = cv.VideoCapture(0)
```

Opens your webcam. `0` means the first/default camera. This is placed inside `main()` right after `pygame.init()` so both pygame and the webcam start up together before the game loop begins.

---

### Gesture Stability Variables

```python
stable_gesture  = "NONE"
previous_gesture = "NONE"
gesture_counter = 0
STABILITY_FRAMES = 4
```

These four variables implement the stability filter, the mechanism that prevents a single misread frame from yanking the snake in a random direction.

- `stable_gesture`: the gesture the game actually acts on. Only updated after enough consecutive matching frames.
- `previous_gesture`: the gesture detected in the previous frame. Used to count consecutive matches.
- `gesture_counter`: counts how many consecutive frames the same gesture has appeared.
- `STABILITY_FRAMES = 4`: a gesture must appear 4 frames in a row before it's trusted. At ~18fps with a hand visible, that's about 0.22 seconds which fast enough to feel responsive, slow enough to ignore single-frame misreads.

## Initial Failure

When we were integrating gestures with the game, we didn't consider the stability factor. We moved the snake in the detected gesture's direction. The issue we faced was: while changing the direction from say point down to point right, the hand moved through 2 other gestures i.e. point left and point up (if you are using your right hand). Due to this the snake used to respond immediately to the gesture and move to the left and then upwards. Since this behaviour is undesirable, we introduced the stability factor. 

---

### HandLandmarker Context Manager

```python
with HandLandmarker.create_from_options(options) as landmarker:
    while True:
```

`with ... as landmarker:` initializes the MediaPipe hand detector and wraps the entire game loop inside it. The `with` block guarantees that MediaPipe's resources (memory, model weights) are properly loaded before the loop starts and properly cleaned up when the loop ends, even if it ends due to an error. The entire `while True` loop is indented one level inside this block, meaning MediaPipe stays active for the entire game session.

---

### Phase 1: Webcam Capture

```python
success, frame = cap.read()
if not success:
    print("Camera not found")
    break
```

`cap.read()` grabs one frame from the webcam. It returns two values: `success` (True/False depending on whether the camera is working) and `frame` (the image as a NumPy array). If the camera fails or disconnects, `success` is False and we break the loop to stop the program cleanly.

```python
frame = cv.flip(frame, 1)
```

Flips the frame horizontally. `1` means horizontal flip. Without this, the webcam feed is mirrored i.e. moving your right hand moves the on-screen hand to the left. Flipping makes it feel like a real mirror, which is more intuitive.

```python
rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
```

Converts the image from BGR to RGB. OpenCV reads images in BGR order by default. MediaPipe expects RGB. The visual image looks identical, only the channel order in memory changes. If you skip this, colors get misinterpreted and hand detection breaks or gives wrong results.

```python
mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
```

Wraps the NumPy array in a MediaPipe `Image` object. The new MediaPipe tasks API doesn't accept raw NumPy arrays directly, it needs this wrapper. `mp.ImageFormat.SRGB` tells it this is a standard RGB image (as opposed to grayscale or floating point).

```python
result = landmarker.detect(mp_image)
```

Runs the hand detection model on this frame. Returns a `HandLandmarkerResult` object containing `result.hand_landmarks` (list of detected hands, each hand being a list of 21 landmarks), `result.handedness` (left/right classification), and `result.hand_world_landmarks` (3D coordinates in real-world meters). 

```python
angle = 0.0
```

Sets a safe default value for `angle` before entering the hand detection block. If no hand is detected this frame and `angle` was never assigned, referencing it later would cause a crash. This default prevents that.

---

### Hand Landmark Processing

```python
if result.hand_landmarks:
```

`result.hand_landmarks` is a list: empty `[]` if no hand detected, non-empty if at least one hand was found. Everything inside this block only runs when a hand is visible.

```python
handLms = result.hand_landmarks[0]
```

Since `num_hands=1`, we only ever have one hand. `[0]` picks the first (and only) hand's landmark list, which is a list of 21 `NormalizedLandmark` objects, each with `.x`, `.y`, `.z` coordinates normalized between 0 and 1.

```python
handedness_label = result.handedness[0][0].display_name
handedness_label = "Left" if handedness_label == "Right" else "Right"
```

`result.handedness[0][0].display_name` gives `"Left"` or `"Right"` as MediaPipe sees it. The second line swaps them, because the frame was flipped with `cv.flip(frame, 1)`, what MediaPipe thinks is the left hand appears on the right side of the screen and vice versa. Swapping corrects this so `handedness_label` matches what you actually see on screen.

```python
thumb_tip, thumb_ip = handLms[4], handLms[3]
index_tip, index_mcp = handLms[8], handLms[5]
```

Extracts specific landmarks by their index number. MediaPipe's 21 landmarks have fixed indices: landmark 4 is always the thumb tip, 3 is the thumb IP joint, 8 is the index fingertip, 5 is the index MCP (knuckle) joint. These four are the ones needed for finger counting and angle calculation.

```python
fingers_up = []
if handedness_label == "Right":
    fingers_up.append(thumb_tip.x < thumb_ip.x)
else:
    fingers_up.append(thumb_tip.x > thumb_ip.x)
```

Builds a list of True/False for each finger: True means extended, False means folded. The thumb is handled separately because it extends sideways (horizontally) rather than upward. For the right hand, the thumb tip should be to the left of (smaller x than) the IP joint when extended. For the left hand, the direction is reversed.

```python
for tip_id, pip_id in [(8,6), (12,10), (16,14), (20,18)]:
    fingers_up.append(handLms[tip_id].y < handLms[pip_id].y)
```

Checks the remaining four fingers (index, middle, ring, pinky) using y-coordinate comparison. Each tuple is `(tip_landmark_index, pip_landmark_index)`. If the fingertip's y-coordinate is less than (above, since y increases downward in image coordinates) its PIP joint's y-coordinate, the finger is extended - `True` is appended. This logic works the same for both left and right hands.

```python
count = sum(fingers_up)
```

`sum()` on a list of booleans counts the `True` values (since `True = 1`, `False = 0`). This gives the total number of extended fingers, used to detect FIST (0 fingers) and OPEN PALM (5 fingers).

---

### Gesture Classification

```python
if count == 0:
    gesture = "FIST"
elif count == 5:
    gesture = "OPEN PALM"
else:
    if -60 <= angle <= 60:
        gesture = "POINT RIGHT"
    elif 60 < angle < 120:
        gesture = "POINT UP"
    elif angle >= 120 or angle <= -120:
        gesture = "POINT LEFT"
    else:
        gesture = "POINT DOWN"
```

FIST and OPEN PALM are checked first using finger count, these are unambiguous regardless of hand angle. For everything else (1-4 fingers up), pointing direction is detected using the angle of the index finger.

The angle buckets work because `atan2` returns:
- 0° when pointing right
- 90° when pointing up
- ±180° when pointing left
- -90° when pointing down

Each bucket spans roughly ±30-60° around its cardinal direction, so small wobbles in your hand don't accidentally flip the detected gesture.

---

### Angle Calculation

```python
dx = index_tip.x - index_mcp.x
dy = index_mcp.y - index_tip.y
angle = math.degrees(math.atan2(dy, dx))
```

`dx` and `dy` form a vector from the base of the index finger (MCP joint, the knuckle) to its tip, pointing in the same direction your finger points.

`dy = index_mcp.y - index_tip.y` (note: MCP minus tip, not tip minus MCP). This flip is intentional, in image coordinates y increases downward, so a finger pointing upward has a smaller y at the tip than at the base. By subtracting tip from base, we convert to the conventional math sense where "up" is positive, making the `atan2` angle buckets work as expected.

`math.atan2(dy, dx)` computes the angle of this vector in radians, correctly handling all four quadrants (unlike plain `atan` which only handles two). `math.degrees()` converts from radians to degrees for easier reasoning.

---

### Stability Filter

```python
if gesture == previous_gesture:
    gesture_counter += 1
else:
    gesture_counter = 1
    previous_gesture = gesture

if gesture_counter >= STABILITY_FRAMES:
    stable_gesture = gesture
```

This filter prevents a single misread frame from yanking the snake in a random direction.

- If this frame's `gesture` matches `previous_gesture`, increment the counter, the same gesture is holding steady.
- If it's different, reset the counter to 1 and update `previous_gesture`, a new gesture started.
- Only once the same gesture appears for `STABILITY_FRAMES` (4) consecutive frames does it get promoted to `stable_gesture`, the variable the game actually acts on.

This means a gesture that lasts only 1-3 frames (a misread, or a brief accidental pose during a transition) never reaches `stable_gesture` and the game ignores it.

---

### Phase 2: Gesture to Game Action

```python
if not game_started:
    if stable_gesture == "FIST":
        game_started = True
        snake, direction, food, score = reset_game()
        stable_gesture = "NONE"
        last_move_time = pygame.time.get_ticks()
        MOVE_DELAY = MOVE_DELAY_START
```

On the welcome screen, only FIST is checked. When detected, `game_started = True` flips the flag, a fresh game is initialized, `stable_gesture` is manually cleared to `"NONE"` so the FIST doesn't re-trigger on the very next frame, and the timer and speed are reset.

```python
elif game_over:
    if stable_gesture == "FIST":
        snake, direction, food, score = reset_game()
        game_over = False
        stable_gesture = "NONE"
        last_move_time = pygame.time.get_ticks()
        MOVE_DELAY = MOVE_DELAY_START
```

On the game over screen, FIST restarts the game. `game_over = False` removes the game over overlay and resumes the game loop. Same cleanup pattern as above.

```python
else:
    if stable_gesture == "OPEN PALM":
        is_paused = True
    elif stable_gesture in ["POINT UP", "POINT DOWN", "POINT LEFT", "POINT RIGHT"]:
        is_paused = False
```

During active gameplay, OPEN PALM pauses. Any pointing gesture automatically resumes, so there's no separate "resume" gesture needed, you just point where you want to go and the game unpauses instantly.

```python
    if not is_paused:
        if stable_gesture == "POINT UP" and direction != (0, 1):
            direction = (0, -1)
        elif stable_gesture == "POINT DOWN" and direction != (0, -1):
            direction = (0, 1)
        elif stable_gesture == "POINT LEFT" and direction != (1, 0):
            direction = (-1, 0)
        elif stable_gesture == "POINT RIGHT" and direction != (-1, 0):
            direction = (1, 0)
```

This is the core gesture-to-game connection, the exact lines that replace what arrow keys were doing in Week 5. `direction` is set to the same `(col_change, row_change)` tuples as before, just triggered by `stable_gesture` instead of `event.key`. The `direction !=` checks prevent the snake from reversing directly into itself (e.g. if moving right, POINT LEFT is ignored).

---

### Webcam HUD Window

```python
cv.putText(frame, f"Gesture: {stable_gesture}", (10, 50),
           cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
cv.imshow("Vision Tracking Feedback", frame)
```

`cv.putText` draws the currently detected gesture name onto the webcam frame. Arguments: image, text string, position (x=10, y=50 from top-left), font, font scale, color (red in BGR), thickness. `cv.imshow` opens a second window showing the annotated webcam feed so you can see what gesture is being detected in real time. This is your visual feedback loop, essential for debugging when gestures aren't registering as expected.

```python
if cv.waitKey(1) & 0xFF == ord('q'):
    break
```

`cv.waitKey(1)` is required by OpenCV to actually render the webcam window, without it the window won't update even if `cv.imshow` is called. It waits 1ms for a keypress and returns the key code. `& 0xFF` masks to the last 8 bits for cross-platform compatibility. `ord('q') = 113`. Pressing Q from the webcam window breaks the loop and exits.

---

### Cleanup

```python
cap.release()
cv.destroyAllWindows()
pygame.quit()
```

After the loop ends (Q pressed or camera failed):
- `cap.release()` releases the webcam so other programs can use it. Without this, the camera stays locked even after the script ends.
- `cv.destroyAllWindows()` closes the "Vision Tracking Feedback" OpenCV window. Without this it may hang open.
- `pygame.quit()` shuts down pygame cleanly.

---

## Importance of `pygame.time.get_ticks()`

If you remove `pygame.time.get_ticks()` and the delta-time condition cheking, the snake will move forward by one grid cell on **every single frame** processes by your webcam. Following are the consequences if you remove it: 

1. **The bottleneck becomes your webcam:** Your main game loop is driven directly be `success, frame = cap.read()`. Most standard webcams capture videos at 30 FPS or 60 FPS (It can be even less such as 18 or 20 FPS). With the time check, the loop runs at 30/60 FPS (or whatever speed your webcam is running at) to keep the camera feed and gesture recognition smooth, but the snake is restricted to moving only once every `MOVE_DELAY` milliseconds (e.g. 150ms, which is roughly 6.6 times per second). **Without the time check the snake will move 30 to 60 times per second**.

2. **The game will be unplayable:** At 30-60 movements per second, the snake will cross your entire 30-column grid in less than a second. It will crash into a wall or its own tail almost instantly before you even have a chance to change your hand gesture. 

3. **Variable game speed:** Webcam frame rates fluctuate depending on your computer's CPU load and lighting conditions. Without a time anchor, your snake would randomly speed up in bright rooms (where the camera hits max FPS) and slow down in dark rooms or when MediaPipe encounters a heavy processing spike. 

Keeping `pygame.time.get_ticks()` is essential. It completely decouples your **gameplay speed** (the physics of the snake) from your hardware processing speed (the webcam and computer frame rate).

## Gesture → Game Action Map

| Gesture | Action |
|---------|--------|
| FIST | Start game / Restart after game over |
| POINT UP | Move snake up |
| POINT DOWN | Move snake down |
| POINT LEFT | Move snake left |
| POINT RIGHT | Move snake right |
| OPEN PALM | Pause (point in any direction to resume) |

---

## Checkpoint 4 (End of Week 6)

Submit a **screen recording** of your gesture-controlled Snake game running. The recording should show:
- Your hand visible in the webcam window
- The snake responding to your pointing gestures
- At least one full game (start → play → game over → restart)

---


