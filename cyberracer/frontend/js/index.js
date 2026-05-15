/**
 * CyberRacer Entry Point
 * Imports Three.js and other dependencies from npm
 */

// Import Three.js components
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

// Make THREE and GLTFLoader globally available
window.THREE = THREE;
window.GLTFLoader = GLTFLoader;

// Import application modules
import { gestureRecognizer } from './gesture-recognizer.js';
import { gameEngine } from './game-engine.js';
import { obiInterface } from './obi-interface.js';
import { CyberRacerApp } from './app.js';

// Global app instance
let appInstance = null;

// Initialize and start the app
async function main() {
    appInstance = new CyberRacerApp();

    // Store globally for access from HTML
    window.app = appInstance;
    window.gestureRecognizer = gestureRecognizer;
    window.gameEngine = gameEngine;
    window.obiInterface = obiInterface;

    console.log('CyberRacer modules loaded');
}

// startGame function exposed to HTML onclick handler
window.startGame = async function() {
    if (!appInstance) {
        console.error('App not initialized yet');
        return;
    }
    await appInstance.initialize();
    appInstance.startGame();
};

// Start when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', main);
} else {
    main();
}

// Export for other modules
export { THREE, GLTFLoader };
