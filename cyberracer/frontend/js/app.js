/**
 * CyberRacer Main Application
 * Integrates gesture recognition, game engine, and OBI reasoning
 */

import { gestureRecognizer } from './gesture-recognizer.js';
import { gameEngine } from './game-engine.js';
import { obiInterface } from './obi-interface.js';

class CyberRacerApp {
    constructor() {
        this.gestureRecognizer = gestureRecognizer;
        this.gameEngine = gameEngine;
        this.obiInterface = obiInterface;
        this.gameRunning = false;
    }

    async initialize() {
        try {
            console.log('Initializing CyberRacer...');
            
            // Initialize OBI
            await this.obiInterface.initialize();
            
            // Initialize gesture recognizer
            await this.gestureRecognizer.initialize();
            
            // Initialize game engine
            await this.gameEngine.initialize();
            
            // Setup gesture callback
            this.gestureRecognizer.onGestureDetected((gestureData) => {
                this.onGestureDetected(gestureData);
            });

            console.log('CyberRacer initialized successfully');
        } catch (error) {
            console.error('Failed to initialize CyberRacer:', error);
        }
    }

    onGestureDetected(gestureData) {
        if (!this.gameRunning) return;

        // Update UI
        this.updateGestureUI(gestureData);

        // Update game state
        const gameState = this.gameEngine.getCarState();
        this.gameEngine.updateFromGesture(gestureData);

        // Request OBI reasoning
        this.obiInterface.requestReasoning(gestureData, gameState).then((reasoning) => {
            this.obiInterface.displayReasoning(reasoning);
        });

        // Update status panel
        this.updateStatusPanel(gestureData, gameState);
    }

    updateGestureUI(gestureData) {
        const gestureMap = {
            'OPEN_PALM': '🖐️ OPEN PALM — ACCELERATE',
            'FIST': '✊ FIST — BRAKE',
            'POINT': '☝️ POINT — STEER LEFT',
            'THUMBS_UP': '👍 THUMBS UP — STEER RIGHT',
            'PEACE': '✌️ PEACE — DRIFT',
            'NEUTRAL': '✋ NEUTRAL',
            'IDLE': '⏸️ IDLE'
        };

        const gestureText = gestureMap[gestureData.gesture] || gestureData.gesture;
        const confidencePercent = (gestureData.confidence * 100).toFixed(1);

        const gestureInfo = `
<div style="color: #00ff88; margin: 8px 0;">
    <strong>${gestureText}</strong><br>
    Confidence: <span style="color: #ffff00;">${confidencePercent}%</span><br>
    Hands Detected: <span style="color: #ffff00;">${gestureData.handsDetected}</span>
</div>
        `.trim();

        document.getElementById('gesture-info').innerHTML = gestureInfo;
    }

    updateStatusPanel(gestureData, gameState) {
        // Hand state
        const handStates = ['IDLE', 'DETECTING', 'TRACKING'];
        const handState = gestureData.handsDetected > 0 ? 'TRACKING' : 'DETECTING';
        document.getElementById('hand-state').textContent = handState;

        // Gesture label
        document.getElementById('gesture-label').textContent = gestureData.gesture;

        // Car speed (convert to km/h)
        const speedKmh = Math.abs(gameState.speed * 100).toFixed(1);
        document.getElementById('car-speed').textContent = `${speedKmh} km/h`;

        // Car position
        const posX = gameState.position.x.toFixed(1);
        const posZ = gameState.position.z.toFixed(1);
        document.getElementById('car-position').textContent = `${posX}, ${posZ}`;
    }

    startGame() {
        this.gameRunning = true;
        document.getElementById('calibration-modal').style.display = 'none';
        console.log('Game started!');
    }
}

// Global app instance
const app = new CyberRacerApp();

// Start function (called from calibration button)
async function startGame() {
    await app.initialize();
    app.startGame();
}

// Handle window resize
window.addEventListener('resize', () => {
    if (app.gameEngine.renderer) {
        const width = window.innerWidth * 0.65;
        const height = window.innerHeight - 100;
        app.gameEngine.renderer.setSize(width, height);
        app.gameEngine.camera.aspect = width / height;
        app.gameEngine.camera.updateProjectionMatrix();
    }
});

export { CyberRacerApp };
