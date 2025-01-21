// Import the WebSocket library
import WebSocket, { WebSocketServer } from 'ws';

// Types
type PlayerData = {
    socket: WebSocket;
    data: Record<string, any>;
};

type GameState = {
    players: Record<string, PlayerData>;
};

type Message = {
    type: string;
    payload?: any;
    playerId?: any;
};

// Server setup
const PORT = 8080;
const wss = new WebSocketServer({ port: PORT });
console.log(`WebSocket server running on ws://localhost:${PORT}`);

// Game state
const gameState: GameState = {
    players: {},
};

// Basic authentication (e.g., username/password or token validation)
function authenticatePlayer(token: string): boolean {
    // In a real implementation, validate the token securely.
    return !!token && token.startsWith("player_"); // Example: token starts with 'player_'
}

// Broadcast message to all connected clients
function broadcast(message: Message): void {
    wss.clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify(message));
        }
    });
}

// Handle incoming messages from a player
function handleMessage(playerId: string, message: string): void {
    try {
        const data: Message = JSON.parse(message);
        // Example: Handle different message types
        if (data.type === 'update') {
            gameState.players[playerId].data = data.payload;
            console.log(`Player ${playerId} updated state:`, data.payload);
        } else {
            console.log(`Unhandled message type from player ${playerId}:`, data.type);
        }
    } catch (error) {
        console.error(`Error handling message from player ${playerId}:`, error);
    }
}

// Game loop (runs independently of message handling)
function gameLoop(): void {
    // Example: Update the game state periodically
    console.log("Game loop tick");
    // Broadcast game state to all players
    broadcast({ type: 'game_state', payload: gameState });
}

setInterval(gameLoop, 1000); // Run the game loop every second

// WebSocket event handling
wss.on('connection', (ws, req) => {
    const token = req.url?.split('?token=')[1]; // Extract token from query string

    if (token === undefined || !authenticatePlayer(token)) {
        ws.send(JSON.stringify({ type: 'error', message: 'Authentication failed' }));
        ws.close();
        return;
    }

    const playerId: string = token; // Use token as the player ID (simplified)
    gameState.players[playerId] = { socket: ws, data: {} };

    console.log(`Player ${playerId} connected.`);
    broadcast({ type: 'player_joined', playerId });

    // Handle incoming messages
    ws.on('message', (message: string) => handleMessage(playerId, message));

    // Handle player disconnect
    ws.on('close', () => {
        console.log(`Player ${playerId} disconnected.`);
        delete gameState.players[playerId];
        broadcast({ type: 'player_left', playerId });
    });

    // Send initial connection acknowledgment
    ws.send(JSON.stringify({ type: 'connected', playerId }));
});
