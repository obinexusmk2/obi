# CyberRacer — Quick Start Guide

## 📦 What's Included

✓ **Complete cybernetic authentication game** with hand gesture control
✓ **9 car 3D models** (different colors and variants)  
✓ **OBI reasoning engine** for intelligent gesture interpretation
✓ **Windows P2P networking** for multiplayer support
✓ **Flask backend** with RESTful API
✓ **Real-time 3D rendering** with Three.js
✓ **MediaPipe integration** for hand gesture recognition

## 🚀 Quick Start (5 minutes)

### 1. Install Dependencies
```bash
cd cyberracer
pip install -r requirements.txt
pip install obi
```

### 2. Start Backend Server
```bash
# Windows
python backend/app.py

# Or use the startup script
./run.bat         # Windows
./run.sh          # Linux/macOS
```

Server starts on: `http://localhost:5000`

### 3. Open Game in Browser
```bash
# Open frontend/index.html in any modern browser
# Or navigate to: http://localhost:8000 (if serving with Python)
```

## 🎮 How to Play

### Hand Gestures for Control

| Gesture | Action |
|---------|--------|
| 🖐️ **Open Palm** | Accelerate |
| ✊ **Fist** | Brake |
| ☝️ **Point (Index)** | Steer Left |
| 👍 **Thumbs Up** | Steer Right |
| ✌️ **Peace (2 Fingers)** | Drift |

### Game Features
- Real-time hand tracking (30 FPS)
- OBI reasoning for gesture interpretation
- 9 different car models
- 3D racing environment
- Live confidence scoring
- Reasoning transparency

## 🏗️ Project Structure

```
cyberracer/
├── frontend/
│   ├── index.html                 (Main game UI)
│   └── js/
│       ├── gesture-recognizer.js  (Hand tracking)
│       ├── game-engine.js         (3D rendering)
│       ├── obi-interface.js       (Backend comm)
│       └── app.js                 (Main controller)
├── backend/
│   ├── app.py                     (Flask server)
│   └── network/
│       └── p2p_manager.py         (P2P networking)
├── assets/
│   └── car*.glb                   (3D car models)
├── README.md                      (Full documentation)
├── ARCHITECTURE.md                (Technical details)
└── requirements.txt               (Python dependencies)
```

## 🧠 OBI Reasoning

CyberRacer uses **Ontological Bayesian Intelligence** for gesture interpretation:

```
Hand Gesture Detection
        ↓
State Vector Creation
        ↓
Bayesian Inference
    ├─ FACT: Input summarization
    ├─ JUSTIFICATION: Constraint analysis
    └─ RATIONAL: Action selection
        ↓
Confidence Scoring (95.4% threshold)
        ↓
Action Execution
```

Example reasoning output:
```
FACT: Palm open, all fingers extended
JUSTIFY: User intent to increase velocity detected
RATIONAL: ACCELERATE
Confidence: 99.0%
```

## 🌐 API Endpoints

### Game Reasoning
```bash
POST /reason
Content-Type: application/json

{
  "gesture": "OPEN_PALM",
  "confidence": 0.95,
  "handsDetected": 1,
  "carState": {
    "speed": 0.25,
    "position": {"x": 0, "z": 10}
  }
}

# Response
{
  "action": "ACCELERATE",
  "confidence": 0.99,
  "reasoning": "FACT: ... | JUSTIFY: ... | RATIONAL: ...",
  "epistemic_state": "CONVERGED"
}
```

### Session Management
```bash
# Start session
POST /session/start
{ "player_id": "player-1" }

# End session
POST /session/end
{ "player_id": "player-1" }
```

### Network (P2P)
```bash
# Get connected peers
GET /network/peers

# Register as P2P peer
POST /network/register
{ "peer_id": "player-1", "port": 5001 }
```

## ⚙️ Configuration

### Hand Detection Sensitivity
Edit `frontend/js/gesture-recognizer.js`:
```javascript
hands.setOptions({
    minDetectionConfidence: 0.5,    // Lower = more sensitive
    minTrackingConfidence: 0.5
});
```

### Car Physics
Edit `frontend/js/game-engine.js`:
```javascript
const maxSpeed = 0.5;              // Maximum velocity
const acceleration = 0.02;         // Speed per frame
```

### OBI Confidence Threshold
Edit `backend/app.py`:
```python
obi_context = OBIContext(
    confidence_threshold=0.954,    # μ + 2σ standard deviation
    reasoning_mode="bidirectional"
)
```

## 🔧 Troubleshooting

### Hand detection not working
- ✓ Allow camera permissions in browser
- ✓ Ensure good lighting and clear hand visibility
- ✓ Check browser console for MediaPipe errors
- ✓ Try different distance from camera

### Backend connection failed
- ✓ Ensure Flask backend is running
- ✓ Check `http://localhost:5000/health` in browser
- ✓ Verify port 5000 is not in use: `netstat -an | grep 5000`
- ✓ Firewall may be blocking — check Windows Defender

### 3D car not rendering
- ✓ Verify car files exist in `assets/` folder
- ✓ Check browser WebGL support (all modern browsers have it)
- ✓ Try different browser (Chrome, Firefox, Safari)
- ✓ Clear browser cache and reload

### P2P networking not working
- ✓ Ensure port 5001 is open in Windows Firewall
- ✓ All peers must be on same network
- ✓ Check peer IP addresses match: `ipconfig` (Windows)
- ✓ Verify `p2p_manager.initialize()` is called

## 📊 System Requirements

| Component | Requirement |
|-----------|-------------|
| **Python** | 3.9+ |
| **RAM** | 512MB+ |
| **Browser** | Chrome, Firefox, Safari, Edge (all modern versions) |
| **Camera** | Webcam for hand tracking |
| **Network** | Internet for initial setup, optional for gameplay |
| **GPU** | Integrated GPU sufficient for 60 FPS |

## 🎯 Next Steps

1. **Run the game** — Follow Quick Start above
2. **Experiment with gestures** — Find what works for you
3. **Check backend logs** — See OBI reasoning in real-time
4. **Enable P2P** — Invite friends to play multiplayer
5. **Customize** — Modify gestures, cars, physics
6. **Deploy** — Run on Windows Server for production

## 📚 Full Documentation

- **README.md** — Complete feature documentation
- **ARCHITECTURE.md** — Technical system design
- **backend/app.py** — Flask API implementation
- **frontend/js/** — Frontend module details

## 💡 Tips & Tricks

- **Stable gestures** — Hold hand still for better recognition
- **Multi-hand** — Use both hands for complex controls
- **Offline mode** — Game works without backend (mock reasoning)
- **Car switching** — Database supports all 9 car models
- **P2P scaling** — Network manager supports 10+ concurrent peers

## 🛠️ Developer Notes

### Adding New Gestures
1. Update `gesture-recognizer.js` with new landmark logic
2. Train OBI model on new gesture data
3. Update action mapping in `backend/app.py`
4. Test with WebGL canvas visualization

### Extending P2P
```python
# In p2p_manager.py
p2p_manager.broadcast_message({
    'type': 'custom_event',
    'data': {...}
})
```

### Custom Car Models
1. Export 3D model as GLB format
2. Add to `assets/` folder
3. Update `game-engine.js` with file path
4. Scale factor: 0.1 (adjust as needed)

## 📞 Support

- **Issues** — Check Troubleshooting section above
- **Questions** — Review ARCHITECTURE.md for technical details
- **Contributions** — Fork/modify and test locally

## 📄 License

MIT License — See LICENSE file for details

---

**CyberRacer** — Where hand gestures meet cybernetic gaming!

Version: 1.0.0  
Last Updated: May 2026
