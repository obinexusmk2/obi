/**
 * MediaPipe Hand Gesture Recognizer
 * Converts hand landmarks into game control gestures
 */

class GestureRecognizer {
    constructor() {
        this.hands = null;
        this.camera = null;
        this.canvasElement = document.getElementById('camera-canvas');
        this.canvasCtx = this.canvasElement.getContext('2d');
        this.resultsCallback = null;
        
        // Gesture state
        this.currentGesture = 'IDLE';
        this.confidence = 0;
        this.landmarks = null;
        
        this.initialized = false;
    }

    async initialize() {
        const hands = new Hands({
            locateFile: (file) => {
                return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
            }
        });

        hands.setOptions({
            maxNumHands: 2,
            modelComplexity: 1,
            minDetectionConfidence: 0.5,
            minTrackingConfidence: 0.5
        });

        hands.onResults(this.onResults.bind(this));

        const camera = new Camera(this.canvasElement, {
            onFrame: async () => {
                await hands.send({ image: this.canvasElement });
            },
            width: 640,
            height: 480
        });

        camera.start();
        this.hands = hands;
        this.camera = camera;
        this.initialized = true;
    }

    onResults(results) {
        this.canvasCtx.save();
        this.canvasCtx.clearRect(0, 0, this.canvasElement.width, this.canvasElement.height);

        // Draw camera feed
        this.canvasCtx.drawImage(results.image, 0, 0, this.canvasElement.width, this.canvasElement.height);

        if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
            for (let i = 0; i < results.multiHandLandmarks.length; i++) {
                const landmarks = results.multiHandLandmarks[i];
                this.landmarks = landmarks;

                // Draw hand landmarks
                drawConnectors(this.canvasCtx, landmarks, HAND_CONNECTIONS, {
                    color: '#00ff88',
                    lineWidth: 2
                });
                drawLandmarks(this.canvasCtx, landmarks, {
                    color: '#ffff00',
                    lineWidth: 1,
                    radius: 3
                });

                // Recognize gesture from landmarks
                this.recognizeGesture(landmarks);
            }
        } else {
            this.currentGesture = 'IDLE';
            this.confidence = 0;
            this.landmarks = null;
        }

        this.canvasCtx.restore();

        if (this.resultsCallback) {
            this.resultsCallback({
                gesture: this.currentGesture,
                confidence: this.confidence,
                landmarks: this.landmarks,
                handsDetected: results.multiHandLandmarks ? results.multiHandLandmarks.length : 0
            });
        }
    }

    recognizeGesture(landmarks) {
        // Calculate finger states
        const thumbOpen = this.isFingerOpen(landmarks, [2, 3, 4]);
        const indexOpen = this.isFingerOpen(landmarks, [6, 7, 8]);
        const middleOpen = this.isFingerOpen(landmarks, [10, 11, 12]);
        const ringOpen = this.isFingerOpen(landmarks, [14, 15, 16]);
        const pinkyOpen = this.isFingerOpen(landmarks, [18, 19, 20]);

        const openFingers = [thumbOpen, indexOpen, middleOpen, ringOpen, pinkyOpen].filter(x => x).length;

        // Gesture recognition logic
        if (openFingers === 5) {
            this.currentGesture = 'OPEN_PALM'; // Accelerate
            this.confidence = 0.95;
        } else if (openFingers === 0) {
            this.currentGesture = 'FIST'; // Brake
            this.confidence = 0.95;
        } else if (indexOpen && !thumbOpen && !middleOpen && !ringOpen && !pinkyOpen) {
            this.currentGesture = 'POINT'; // Steer Left
            this.confidence = 0.90;
        } else if (thumbOpen && !indexOpen && !middleOpen && !ringOpen && !pinkyOpen) {
            this.currentGesture = 'THUMBS_UP'; // Steer Right
            this.confidence = 0.90;
        } else if (indexOpen && middleOpen && !thumbOpen && !ringOpen && !pinkyOpen) {
            this.currentGesture = 'PEACE'; // Drift
            this.confidence = 0.88;
        } else {
            this.currentGesture = 'NEUTRAL';
            this.confidence = 0.5;
        }
    }

    isFingerOpen(landmarks, fingerIndices) {
        // Check if finger is extended based on landmark positions
        const tip = landmarks[fingerIndices[2]];
        const pip = landmarks[fingerIndices[1]];
        const mcp = landmarks[fingerIndices[0]];

        // Finger is open if tip is higher (lower y) than pip
        return tip.y < pip.y;
    }

    onGestureDetected(callback) {
        this.resultsCallback = callback;
    }

    getCurrentGesture() {
        return {
            gesture: this.currentGesture,
            confidence: this.confidence
        };
    }
}

// Initialize recognizer
const gestureRecognizer = new GestureRecognizer();
export { gestureRecognizer };
