#!/usr/bin/env python3
"""
P2P Network Manager for Windows
Handles peer-to-peer connections for CyberRacer
"""

import socket
import threading
import json
from dataclasses import dataclass
from typing import Dict, List, Callable
from datetime import datetime

@dataclass
class Peer:
    """Represents a connected peer"""
    peer_id: str
    host: str
    port: int
    connected_at: str
    last_heartbeat: str

class P2PManager:
    """Manages peer-to-peer connections"""
    
    def __init__(self, local_port: int = 5001):
        self.local_port = local_port
        self.peers: Dict[str, Peer] = {}
        self.server_socket = None
        self.running = False
        self.message_callbacks: List[Callable] = []
        self.lock = threading.Lock()
        
    def initialize(self):
        """Start P2P server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', self.local_port))
        self.server_socket.listen(5)
        self.running = True
        
        # Start accepting connections in background
        threading.Thread(target=self._accept_connections, daemon=True).start()
        print(f"[P2P] Server initialized on port {self.local_port}")
        
    def register_peer(self, peer_id: str, host: str, port: int) -> bool:
        """Register a new peer"""
        with self.lock:
            if peer_id not in self.peers:
                peer = Peer(
                    peer_id=peer_id,
                    host=host,
                    port=port,
                    connected_at=datetime.now().isoformat(),
                    last_heartbeat=datetime.now().isoformat()
                )
                self.peers[peer_id] = peer
                print(f"[P2P] Peer registered: {peer_id} @ {host}:{port}")
                return True
        return False
    
    def unregister_peer(self, peer_id: str) -> bool:
        """Unregister a peer"""
        with self.lock:
            if peer_id in self.peers:
                del self.peers[peer_id]
                print(f"[P2P] Peer unregistered: {peer_id}")
                return True
        return False
    
    def broadcast_message(self, message: dict, exclude_peer: str = None) -> int:
        """Broadcast message to all peers"""
        sent_count = 0
        message_data = json.dumps(message).encode('utf-8')
        
        with self.lock:
            for peer_id, peer in self.peers.items():
                if exclude_peer and peer_id == exclude_peer:
                    continue
                
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    sock.connect((peer.host, peer.port))
                    sock.sendall(message_data + b'\n')
                    sock.close()
                    sent_count += 1
                except Exception as e:
                    print(f"[P2P] Failed to send to {peer_id}: {e}")
        
        return sent_count
    
    def send_to_peer(self, peer_id: str, message: dict) -> bool:
        """Send message to specific peer"""
        with self.lock:
            if peer_id not in self.peers:
                return False
            
            peer = self.peers[peer_id]
            message_data = json.dumps(message).encode('utf-8')
            
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect((peer.host, peer.port))
                sock.sendall(message_data + b'\n')
                sock.close()
                
                # Update heartbeat
                peer.last_heartbeat = datetime.now().isoformat()
                return True
            except Exception as e:
                print(f"[P2P] Failed to send to {peer_id}: {e}")
                return False
    
    def register_message_callback(self, callback: Callable):
        """Register callback for received messages"""
        self.message_callbacks.append(callback)
    
    def get_peers(self) -> List[Dict]:
        """Get list of connected peers"""
        with self.lock:
            return [
                {
                    'peer_id': peer.peer_id,
                    'host': peer.host,
                    'port': peer.port,
                    'connected_at': peer.connected_at
                }
                for peer in self.peers.values()
            ]
    
    def get_peer_count(self) -> int:
        """Get number of connected peers"""
        with self.lock:
            return len(self.peers)
    
    def _accept_connections(self):
        """Accept incoming peer connections"""
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, client_address),
                    daemon=True
                ).start()
            except Exception as e:
                if self.running:
                    print(f"[P2P] Error accepting connection: {e}")
    
    def _handle_client(self, client_socket, client_address):
        """Handle incoming connection from peer"""
        try:
            data = client_socket.recv(4096).decode('utf-8').strip()
            if data:
                message = json.loads(data)
                
                # Call registered callbacks
                for callback in self.message_callbacks:
                    try:
                        callback(message, client_address)
                    except Exception as e:
                        print(f"[P2P] Callback error: {e}")
        except Exception as e:
            print(f"[P2P] Error handling client: {e}")
        finally:
            client_socket.close()
    
    def shutdown(self):
        """Shutdown P2P server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print("[P2P] Server shutdown")

# Global P2P manager instance
p2p_manager = P2PManager()
