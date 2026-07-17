# Hand Landmarker Model

This directory must contain `hand_landmarker.task`, MediaPipe's pretrained
hand-landmark model. It is not committed to the repository (binary model
asset) and is not downloaded automatically at runtime by MGX.

## Setup (one-time, per machine)

Download the model file:

https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task

Place it here as:

```
assets/models/hand_landmarker.task
```

MGX will fail to start hand detection with a clear `FileNotFoundError` if
this file is missing.
