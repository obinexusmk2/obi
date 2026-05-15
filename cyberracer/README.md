# CyberRacer — Cybernetic Authentication Game

**A hand gesture-controlled 3D racing game powered by OBI reasoning and P2P networking**

## Overview

CyberRacer is an innovative cybernetic authentication interface that combines:

- **MediaPipe Hand Gesture Recognition** — Real-time hand tracking and gesture detection
- **OBI (Ontological Bayesian Intelligence)** — Advanced reasoning framework for gesture interpretation
- **Three.js 3D Rendering** — Real-time 3D car visualization with 9 car variants
- **Windows P2P Networking** — Peer-to-peer multiplayer support
- **Flask Backend** — RESTful API for game state management and reasoning

## Installation

### Prerequisites

- Python 3.9 or later
- Node.js + npm (optional, for frontend development)
- Windows 10/11 (for full P2P networking support)

### Setup

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
pip install obi  # OBI SDK
```

2. **Start the backend server:**
```bash
python backend/app.py
```

The server will start on `http://localhost:5000`

3. **Open the frontend:**
```bash
# Open frontend/index.html in a web browser
# Or serve with Python:
cd frontend
python -m http.server 8000
# Visit http://localhost:8000
```

## Game Controls

### Hand Gestures

| Gesture | Action | Input |
|---------|--------|-------|
| **Open Palm** 🖐️ | Accelerate | All 5 fingers extended |
| **Fist** ✊ | Brake | All fingers closed |
| **Point** ☝️ | Steer Left | Index finger only |
| **Thumbs Up** 👍 | Steer Right | Thumb extended up |
| **Peace** ✌️ | Drift | Index + Middle extended |

### Game Features

- **Real-time hand tracking** with 30+ FPS detection
- **OBI-powered reasoning** for gesture interpretation
- **Multiple car variants** (9 different color schemes)
- **95.4% confidence threshold** for action execution
- **Epistemic audit trail** for reasoning transparency

## Architecture

### Frontend (`frontend/`)

```
index.html              — Main HTML interface with MediaPipe setup
js/
├── gesture-recognizer.js  — MediaPipe hand detection & gesture parsing
├── game-engine.js         — Three.js 3D rendering and physics
├── obi-interface.js       — OBI backend communication
└── app.js                 — Main application controller
```

### Backend (`backend/`)

```
app.py                  — Flask API server with OBI reasoning
network/
└── p2p_manager.py     — Windows P2P networking manager
obi/
└── (OBI integration)
assets/
├── car*.glb           — 9 different car 3D models
```

## API Endpoints

### Game Reasoning

**POST** `/reason`
- Takes gesture data and game state
- Returns OBI reasoning result with action and confidence
- Example:
```json
{
  "gesture": "OPEN_PALM",
  "confidence": 0.95,
  "handsDetected": 1,
  "carState": {
    "speed": 0.25,
    "position": {"x": 0, "z": 10}
  }
}
```

### Session Management

**POST** `/session/start` — Initialize game session
**POST** `/session/end` — End game session

### Network

**GET** `/network/peers` — List connected peers
**POST** `/network/register` — Register as P2P peer

## OBI Integration

CyberRacer uses the **OBI Framework** for intelligent gesture reasoning:

1. **Probe Internal** — Converts raw hand landmarks to state vector
2. **Bayesian Inference** — Calculates confidence and bias parameters
3. **Rhetorical Reasoning** — Applies FACT→JUSTIFICATION→RATIONAL pipeline
4. **Action Execution** — Executes commands at 95.4% confidence threshold

Example OBI Output:
```
FACT: Palm open, all fingers extended
JUSTIFY: User intent to increase velocity detected
RATIONAL: ACCELERATE
Confidence: 99.0%
```

## P2P Networking (Windows)

Enable multiplayer racing with peer-to-peer networking:

```python
from backend.network.p2p_manager import p2p_manager

# Initialize P2P
p2p_manager.initialize()

# Register peer
p2p_manager.register_peer('player-1', '192.168.1.100', 5001)

# Broadcast game state
p2p_manager.broadcast_message({
    'type': 'game_state',
    'player': 'player-1',
    'position': [10, 0],
    'gesture': 'OPEN_PALM'
})
```

## Car Models

9 different car variants included:

- **carred.glb** — Red
- **carblue.glb** — Blue
- **cargreen.glb** — Green (variant 1 & 2)
- **caryellow.glb** — Yellow (variant included)
- **carwhite.glb** — White
- **carblack.glb** — Black

Switch cars in-game or via the backend API.

## Configuration

Edit `frontend/index.html` and `backend/app.py` to customize:

- Hand detection sensitivity
- Car acceleration/braking rates
- P2P server port (default: 5001)
- OBI confidence threshold (default: 95.4%)

## Troubleshooting

### Backend connection failed
- Ensure Flask backend is running: `python backend/app.py`
- Check firewall allows port 5000

### Hand detection not working
- Allow camera permissions in browser
- Ensure good lighting and clear hand visibility
- Check MediaPipe library loaded (console for errors)

### 3D car not rendering
- Verify car GLB files in `assets/` folder
- Check browser WebGL support
- Clear browser cache

### P2P networking issues
- Ensure Windows firewall allows port 5001
- Check network connectivity between peers
- Use same network subnet for direct connection

## Future Enhancements

- [ ] Multiplayer leaderboards
- [ ] Voice commands integration
- [ ] Advanced gesture recognition (AI-based)
- [ ] Terrain obstacles and challenges
- [ ] Power-up system
- [ ] Cross-platform networking (Linux/macOS)

## License

MIT License - See LICENSE file

## Author

**Nnamdi Michael Okpala (OBINexus)**  
Email: okpalan@protonmail.com

## References

- [OBI Framework](https://github.com/obinexusmk2/obi)
- [MediaPipe Hands](https://google.github.io/mediapipe/solutions/hands.html)
- [Three.js](https://threejs.org/)
- [Flask](https://flask.palletsprojects.com/)

---

**CyberRacer** — Where cybernetic authentication meets racing entertainment
