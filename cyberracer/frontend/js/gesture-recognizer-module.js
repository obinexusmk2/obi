/**
 * MediaPipe Hand Gesture Recognizer (ES6 Module)
 * Converts hand landmarks into game control gestures
 */

export class GestureRecognizer {
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
        // Wait for MediaPipe to be loaded from CDN
        if (!window.Hands || !window.Camera) {
            console.error('MediaPipe libraries not loaded. Using fallback...');
            this.initializeFallback();
            return;
        }

        const hands = new window.Hands({
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

        const camera = new window.Camera(this.canvasElement, {
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
        console.log('✓ MediaPipe Hand Detection initialized');
    }

    initializeFallback() {
        // Simulate hand detection for testing without MediaPipe
        console.warn('⚠ Using fallback gesture simulation (no MediaPipe)');
        this.simulateGestures();
    }

    simulateGestures() {
        // Random gesture simulation every 2 seconds
        setInterval(() => {
            const gestures = ['OPEN_PALM', 'FIST', 'POINT', 'THUMBS_UP', 'NEUTRAL'];
            const randomGesture = gestures[Math.floor(Math.random() * gestures.length)];
            
            if (this.resultsCallback) {
                this.resultsCallback({
                    gesture: randomGesture,
                    confidence: 0.85 + Math.random() * 0.14,
                    landmarks: null,
                    handsDetected: Math.random() > 0.3 ? 1 : 0
                });
            }
        }, 2000);
    }

    onResults(results) {
        const canvasCtx = this.canvasCtx;
        canvasCtx.save();
        canvasCtx.clearRect(0, 0, this.canvasElement.width, this.canvasElement.height);

        // Draw camera feed
        canvasCtx.drawImage(results.image, 0, 0, this.canvasElement.width, this.canvasElement.height);

        if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
            for (let i = 0; i < results.multiHandLandmarks.length; i++) {
                const landmarks = results.multiHandLandmarks[i];
                this.landmarks = landmarks;

                // Draw hand landmarks if drawing utils available
                if (window.drawConnectors && window.HAND_CONNECTIONS) {
                    window.drawConnectors(canvasCtx, landmarks, window.HAND_CONNECTIONS, {
                        color: '#00ff88',
                        lineWidth: 2
                    });
                    window.drawLandmarks(canvasCtx, landmarks, {
                        color: '#ffff00',
                        lineWidth: 1,
                        radius: 3
                    });
                }

                this.recognizeGesture(landmarks);
            }
        } else {
            this.currentGesture = 'IDLE';
            this.confidence = 0;
            this.landmarks = null;
        }

        canvasCtx.restore();

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
        const thumbOpen = this.isFingerOpen(landmarks, [2, 3, 4]);
        const indexOpen = this.isFingerOpen(landmarks, [6, 7, 8]);
        const middleOpen = this.isFingerOpen(landmarks, [10, 11, 12]);
        const ringOpen = this.isFingerOpen(landmarks, [14, 15, 16]);
        const pinkyOpen = this.isFingerOpen(landmarks, [18, 19, 20]);

        const openFingers = [thumbOpen, indexOpen, middleOpen, ringOpen, pinkyOpen].filter(x => x).length;

        if (openFingers === 5) {
            this.currentGesture = 'OPEN_PALM';
            this.confidence = 0.95;
        } else if (openFingers === 0) {
            this.currentGesture = 'FIST';
            this.confidence = 0.95;
        } else if (indexOpen && !thumbOpen && !middleOpen && !ringOpen && !pinkyOpen) {
            this.currentGesture = 'POINT';
            this.confidence = 0.90;
        } else if (thumbOpen && !indexOpen && !middleOpen && !ringOpen && !pinkyOpen) {
            this.currentGesture = 'THUMBS_UP';
            this.confidence = 0.90;
        } else if (indexOpen && middleOpen && !thumbOpen && !ringOpen && !pinkyOpen) {
            this.currentGesture = 'PEACE';
            this.confidence = 0.88;
        } else {
            this.currentGesture = 'NEUTRAL';
            this.confidence = 0.5;
        }
    }

    isFingerOpen(landmarks, fingerIndices) {
        const tip = landmarks[fingerIndices[2]];
        const pip = landmarks[fingerIndices[1]];
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

// Export instance
export const gestureRecognizer = new GestureRecognizer();
