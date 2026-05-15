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

// Import MediaPipe (loaded as external scripts in HTML)
// They will be available as window.Hands, window.Camera, etc.

// Import application modules
import { gestureRecognizer } from './gesture-recognizer.js';
import { gameEngine } from './game-engine.js';
import { obiInterface } from './obi-interface.js';
import { CyberRacerApp } from './app.js';

// Initialize and start the app
async function main() {
    const app = new CyberRacerApp();
    
    // Store globally for access from HTML
    window.app = app;
    window.gestureRecognizer = gestureRecognizer;
    window.gameEngine = gameEngine;
    window.obiInterface = obiInterface;
    
    console.log('✓ CyberRacer modules loaded');
}

// Start when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', main);
} else {
    main();
}

// Export for other modules
export { THREE, GLTFLoader };
