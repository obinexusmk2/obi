/**
 * OBI Interface
 * Communicates with backend OBI reasoning engine
 */

class OBIInterface {
    constructor() {
        this.backendUrl = 'http://localhost:5000';
        this.connected = false;
        this.lastReasoning = null;
    }

    async initialize() {
        try {
            // Check if backend is available
            const response = await fetch(`${this.backendUrl}/health`, {
                method: 'GET',
                timeout: 2000
            });
            this.connected = response.ok;
        } catch (error) {
            console.warn('OBI Backend not available, using mock mode');
            this.connected = false;
        }
    }

    async requestReasoning(gestureData, gameState) {
        const payload = {
            gesture: gestureData.gesture,
            confidence: gestureData.confidence,
            handsDetected: gestureData.handsDetected,
            carState: gameState,
            timestamp: Date.now()
        };

        if (this.connected) {
            try {
                const response = await fetch(`${this.backendUrl}/reason`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });

                if (response.ok) {
                    this.lastReasoning = await response.json();
                    return this.lastReasoning;
                }
            } catch (error) {
                console.warn('OBI request failed:', error);
                return this.mockReasoning(payload);
            }
        }

        return this.mockReasoning(payload);
    }

    mockReasoning(payload) {
        // Simulated OBI reasoning when backend is unavailable
        const { gesture, confidence } = payload;
        
        let action = 'IDLE';
        let reasoning = '';

        if (gesture === 'OPEN_PALM') {
            action = 'ACCELERATE';
            reasoning = `FACT: Palm open, all fingers extended. JUSTIFY: User intent to increase velocity detected. RATIONAL: ${action}`;
        } else if (gesture === 'FIST') {
            action = 'BRAKE';
            reasoning = `FACT: Hand closed (fist). JUSTIFY: Braking gesture recognized with ${(confidence * 100).toFixed(1)}% confidence. RATIONAL: ${action}`;
        } else if (gesture === 'POINT') {
            action = 'STEER_LEFT';
            reasoning = `FACT: Index finger extended. JUSTIFY: Left directional control indicated. RATIONAL: ${action}`;
        } else if (gesture === 'THUMBS_UP') {
            action = 'STEER_RIGHT';
            reasoning = `FACT: Thumb extended upward. JUSTIFY: Right directional control indicated. RATIONAL: ${action}`;
        } else {
            action = 'NEUTRAL';
            reasoning = `FACT: ${gesture} gesture detected. JUSTIFY: No immediate action required. RATIONAL: ${action}`;
        }

        return {
            action: action,
            confidence: confidence,
            reasoning: reasoning,
            bias_parameter: 1 - confidence,
            epistemic_state: 'CONVERGED'
        };
    }

    displayReasoning(reasoning) {
        if (!reasoning) return;

        const reasoningText = `
<span class="confidence">CON: ${(reasoning.confidence * 100).toFixed(1)}%</span> | 
<span class="action">${reasoning.action}</span>
${reasoning.reasoning}
        `.trim();

        document.getElementById('obi-reasoning').innerHTML = reasoningText;
    }

    getLastReasoning() {
        return this.lastReasoning;
    }
}

const obiInterface = new OBIInterface();
