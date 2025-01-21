"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
// Import the WebSocket library
const ws_1 = __importStar(require("ws"));
// Server setup
const PORT = 8080;
const wss = new ws_1.WebSocketServer({ port: PORT });
console.log(`WebSocket server running on ws://localhost:${PORT}`);
// Game state
const gameState = {
    players: {},
};
// Basic authentication (e.g., username/password or token validation)
function authenticatePlayer(token) {
    // In a real implementation, validate the token securely.
    return !!token && token.startsWith("player_"); // Example: token starts with 'player_'
}
// Broadcast message to all connected clients
function broadcast(message) {
    wss.clients.forEach(client => {
        if (client.readyState === ws_1.default.OPEN) {
            client.send(JSON.stringify(message));
        }
    });
}
// Handle incoming messages from a player
function handleMessage(playerId, message) {
    try {
        const data = JSON.parse(message);
        // Example: Handle different message types
        if (data.type === 'update') {
            gameState.players[playerId].data = data.payload;
            console.log(`Player ${playerId} updated state:`, data.payload);
        }
        else {
            console.log(`Unhandled message type from player ${playerId}:`, data.type);
        }
    }
    catch (error) {
        console.error(`Error handling message from player ${playerId}:`, error);
    }
}
// Game loop (runs independently of message handling)
function gameLoop() {
    // Example: Update the game state periodically
    console.log("Game loop tick");
    // Broadcast game state to all players
    broadcast({ type: 'game_state', payload: gameState });
}
setInterval(gameLoop, 1000); // Run the game loop every second
// WebSocket event handling
wss.on('connection', (ws, req) => {
    var _a;
    const token = (_a = req.url) === null || _a === void 0 ? void 0 : _a.split('?token=')[1]; // Extract token from query string
    if (token === undefined || !authenticatePlayer(token)) {
        ws.send(JSON.stringify({ type: 'error', message: 'Authentication failed' }));
        ws.close();
        return;
    }
    const playerId = token; // Use token as the player ID (simplified)
    gameState.players[playerId] = { socket: ws, data: {} };
    console.log(`Player ${playerId} connected.`);
    broadcast({ type: 'player_joined', playerId });
    // Handle incoming messages
    ws.on('message', (message) => handleMessage(playerId, message));
    // Handle player disconnect
    ws.on('close', () => {
        console.log(`Player ${playerId} disconnected.`);
        delete gameState.players[playerId];
        broadcast({ type: 'player_left', playerId });
    });
    // Send initial connection acknowledgment
    ws.send(JSON.stringify({ type: 'connected', playerId }));
});
