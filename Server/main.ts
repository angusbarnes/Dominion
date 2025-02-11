// Import the WebSocket library
import WebSocket, { WebSocketServer } from 'ws';
import express from 'express';
import test_string from './lib/db';
import fs from 'fs';

// Load or initialize player data storage
const PLAYER_DATA_FILE = 'player_data.json';
let playerDataStore: Record<string, { balance: number; energy: number; maxEnergy: number }> = {};

if (fs.existsSync(PLAYER_DATA_FILE)) {
    playerDataStore = JSON.parse(fs.readFileSync(PLAYER_DATA_FILE, 'utf8'));
}

// Save player data to file
function savePlayerData() {
    console.log(JSON.stringify(playerDataStore, null, 2))
    fs.writeFileSync(PLAYER_DATA_FILE, JSON.stringify(playerDataStore, null, 2));
}

// Types
type PlayerData = {
    socket: WebSocket;
};

type GameState = {
    players: Record<string, PlayerData>;
};

type Message = {
    type: MessageType;
    playerId: string | number;
    payload?: any;
};

enum MessageType {
    DEPLOY_UNITS = "DEPLOY",
    UPDATE_BALANCE = "BALANCE",
    QUERY_BALANCE = "QUERY_BALANCE",
    PLACE_TILE = "PLACE",
    UPDATE_ENTITY = "UPDATE",
    GAME_STATE = "STATE",
    PLAYER_LIST = "LIST",
    QUERY_ENERGY = "QUERY_ENERGY",
    UPDATE_ENERGY = "ENERGY",
    SERVER_EVENT = "SERVER_EVENT"
}

// Server setup
const PORT = 8079;
const app = express();
app.use(express.json());

// Simple in-memory user store (replace with database in a real application)
const users: Record<string, string> = {
    "player1": "password123",
    "player2": "securepass"
};

// Generate a basic authentication token
function generateAuthToken(username: string): string {
    return `player_${username}_${Date.now()}`;
}

// Authentication endpoint
app.post('/auth', (req: any, res: any) => {
    const { username, password } = req.body;

    if (users[username] && users[username] === password) {
        const token = generateAuthToken(username);
        res.json({ success: true, token });
    } else {
        res.status(401).json({ success: false, message: "Invalid credentials" });
    }
});

// Start HTTP server
app.listen(PORT, () => {
    console.log(`HTTP server running on http://localhost:${PORT}`);
});

// WebSocket server
const wss = new WebSocketServer({ port: PORT + 1 }); // WebSockets on a different port
console.log(`WebSocket server running on ws://localhost:${PORT + 1} ${test_string}`);

// Game state
const gameState: GameState = {
    players: {}
};

// Basic authentication (e.g., username/password or token validation)
function authenticatePlayer(token: string): boolean {
    return !!token && token.startsWith("player_");
}

// Broadcast message to all connected clients
function broadcast(message: Message): void {
    wss.clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify(message));
        }
    });
}

// Game loop (runs independently of message handling)
function gameLoop(): void {
    // Example: Update the game state periodically
    //console.log("Game loop tick");
    // Broadcast game state to all players
    broadcast({ type: MessageType.SERVER_EVENT, playerId: 0, payload: {type: "balance_add", amount: 2}});

    Object.entries(playerDataStore).forEach(([id, data]) => {
        playerDataStore[id].balance += 2;
    });

    savePlayerData();
}

setInterval(gameLoop, 1000); // Run the game loop every second

// Handle incoming messages from a player
function handleMessage(playerId: string, message: string): void {
    try {
        const data: Message = JSON.parse(message);
        
        switch (data.type) {
            case MessageType.UPDATE_BALANCE:
                if (playerDataStore[playerId]) {
                    playerDataStore[playerId].balance = data.payload.balance;
                }
                break;
            
            case MessageType.QUERY_BALANCE:
                gameState.players[playerId].socket.send(JSON.stringify({
                    type: MessageType.UPDATE_BALANCE,
                    playerId,
                    payload: { balance: playerDataStore[playerId]?.balance || 100 }
                }));
                break;
            
            case MessageType.UPDATE_ENERGY:
                if (playerDataStore[playerId]) {
                    playerDataStore[playerId].energy = data.payload.energy;
                }
                break;
            
            case MessageType.QUERY_ENERGY:
                gameState.players[playerId].socket.send(JSON.stringify({
                    type: MessageType.UPDATE_ENERGY,
                    playerId,
                    payload: { energy: playerDataStore[playerId]?.energy || 6, maxEnergy: playerDataStore[playerId]?.maxEnergy || 6 }
                }));
                break;
            
            default:
                console.log(`Unhandled message type from player ${playerId}:`, data.type);
        }
    } catch (error) {
        console.error(`Error handling message from player ${playerId}:`, error);
    }
}

// WebSocket event handling
wss.on('connection', (ws, req) => {
    const token = req.url?.split('?token=')[1];
    console.log(`Attempted socket connection with token=${token}`);

    if (token === undefined || !authenticatePlayer(token)) {
        ws.send(JSON.stringify({ type: 'error', message: 'Authentication failed' }));
        ws.close();
        console.log(`token=${token} connection attempt was rejected`);
        return;
    }

    const playerId: string = token;
    if (!playerDataStore[playerId]) {
        playerDataStore[playerId] = { balance: 100, energy: 6, maxEnergy: 6 };
        savePlayerData();
    }

    gameState.players[playerId] = { socket: ws };

    console.log(`Player ${playerId} connected.`);
    broadcast({ type: MessageType.PLAYER_LIST, playerId });

    // Handle incoming messages
    ws.on('message', (message: string) => handleMessage(playerId, message));

    // Handle player disconnect
    ws.on('close', () => {
        console.log(`Player ${playerId} disconnected.`);
        delete gameState.players[playerId];
        broadcast({ type: MessageType.PLAYER_LIST, playerId });
    });

    // Send initial player data
    ws.send(JSON.stringify({ type: MessageType.UPDATE_BALANCE, playerId, payload: { balance: playerDataStore[playerId].balance, energy: playerDataStore[playerId].energy, maxEnergy: playerDataStore[playerId].maxEnergy } }));
});
