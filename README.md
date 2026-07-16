# MGX

> Motion Gesture Execution Engine

MGX is a Windows desktop application that lets you control your computer using hand gestures captured through a webcam.

## Status

🚧 Under active development — Version 0.1.0-dev

## What MGX Does

- Detects your hand through a webcam using computer vision
- Recognizes a small set of reliable gestures (open palm, closed fist, pinch, point, peace sign)
- Maps recognized gestures to desktop actions (mouse movement, clicks, scroll, volume, media controls, browser navigation, Alt+Tab, Win+D)
- Lets you save, load, and edit gesture profiles
- Shows live diagnostics: camera FPS, recognition FPS, current gesture, active profile

## Platform

Windows only. This is the only platform supported in the current version.

## Architecture

```
Camera → Vision Engine → Gesture Recognition → Event Dispatch → Desktop Actions
                                                        ↓
                                                       GUI
```

## Tech Stack

- C++20 (GCC / MSYS2)
- Python
- CMake
- PyQt6
- OpenCV
- MediaPipe

## Roadmap

See [ROADMAP.md](ROADMAP.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [PROJECT_RULES.md](PROJECT_RULES.md).

## License

Apache License 2.0
