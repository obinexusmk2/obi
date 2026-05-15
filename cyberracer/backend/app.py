#!/usr/bin/env python3
"""
CyberRacer Backend
OBI-based cybernetic authentication game server
Handles gesture reasoning and P2P networking
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime
from obi import OBIContext, ReasoningResult

app = Flask(__name__)
CORS(app)

# Initialize OBI Context
obi_context = OBIContext(
    confidence_threshold=0.954,
    reasoning_mode="bidirectional"
)

class GameState:
    """Track game session state"""
    def __init__(self):
        self.sessions = {}
        self.player_count = 0

game_state = GameState()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'cyberracer-backend',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/reason', methods=['POST'])
def reason():
    """
    Main OBI reasoning endpoint
    Takes gesture data and game state, returns reasoning result
    """
    try:
        data = request.get_json()
        
        gesture = data.get('gesture', 'IDLE')
        confidence = data.get('confidence', 0)
        hands_detected = data.get('handsDetected', 0)
        car_state = data.get('carState', {})
        
        # Create OBI state from input
        raw_data = {
            'gesture': gesture,
            'confidence': confidence,
            'hands_detected': hands_detected,
            'car_speed': car_state.get('speed', 0),
            'car_position': car_state.get('position', {}),
            'timestamp': data.get('timestamp')
        }
        
        # Probe internal state (data → state)
        state_vector = obi_context.probe_internal(raw_data)
        
        # Perform Bayesian inference
        reasoning_result = obi_context.infer(state_vector)
        
        # Map OBI action to game command
        action_map = {
            'ACCELERATE': 'ACCELERATE',
            'BRAKE': 'BRAKE',
            'STEER_LEFT': 'STEER_LEFT',
            'STEER_RIGHT': 'STEER_RIGHT',
            'NEUTRAL': 'IDLE'
        }
        
        game_action = action_map.get(reasoning_result.action, 'IDLE')
        
        response = {
            'action': game_action,
            'confidence': float(reasoning_result.confidence),
            'reasoning': format_reasoning(reasoning_result),
            'bias_parameter': float(reasoning_result.bias_parameter),
            'epistemic_state': reasoning_result.epistemic_state,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/session/start', methods=['POST'])
def start_session():
    """Initialize a new game session"""
    try:
        data = request.get_json()
        player_id = data.get('player_id')
        
        game_state.sessions[player_id] = {
            'started_at': datetime.now().isoformat(),
            'gestures_processed': 0,
            'distance_traveled': 0
        }
        
        return jsonify({
            'session_id': player_id,
            'status': 'initialized',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/session/end', methods=['POST'])
def end_session():
    """End a game session"""
    try:
        data = request.get_json()
        player_id = data.get('player_id')
        
        if player_id in game_state.sessions:
            session = game_state.sessions[player_id]
            session['ended_at'] = datetime.now().isoformat()
            
            return jsonify({
                'status': 'completed',
                'session': session,
                'timestamp': datetime.now().isoformat()
            }), 200
        
        return jsonify({'error': 'Session not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/network/peers', methods=['GET'])
def get_peers():
    """List connected peers (for P2P networking)"""
    return jsonify({
        'peers': [],
        'player_count': len(game_state.sessions),
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/network/register', methods=['POST'])
def register_peer():
    """Register a peer for P2P connection"""
    try:
        data = request.get_json()
        peer_id = data.get('peer_id')
        host = request.remote_addr
        port = data.get('port')
        
        return jsonify({
            'status': 'registered',
            'peer_id': peer_id,
            'host': host,
            'port': port,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def format_reasoning(result):
    """Format OBI reasoning result as readable text"""
    from obi.sdk.core.context import ReasoningResult
    
    reasoning = result.reasoning_chain if hasattr(result, 'reasoning_chain') else {}
    
    fact = reasoning.get('fact', 'Unknown')
    justification = reasoning.get('justification', 'Unknown')
    rational = reasoning.get('rational', result.action)
    
    return f"FACT: {fact} | JUSTIFY: {justification} | RATIONAL: {rational}"

if __name__ == '__main__':
    print("╔═══════════════════════════════════════════════════╗")
    print("║         CYBERRACER — Backend Service              ║")
    print("║       OBI Cybernetic Authentication Engine         ║")
    print("╚═══════════════════════════════════════════════════╝")
    print("\nStarting backend on http://localhost:5000")
    print("Make sure OBI SDK is installed: pip install obi\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
