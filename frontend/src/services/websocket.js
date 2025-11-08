class WebSocketService {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;
        this.listeners = new Map();
        this.clientId = `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    connect() {
        if (this.ws?.readyState === WebSocket.OPEN) return;
        const wsUrl = `ws://localhost:8000/ws/${this.clientId}`;
        this.ws = new WebSocket(wsUrl);
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.reconnectAttempts = 0;
        };
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.notifyListeners(data.type, data);
        };
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.reconnect();
        };
    }
    reconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnect attempts reached');
            return;
        }
        this.reconnectAttempts++;
        setTimeout(() => {
            console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);
            this.connect();
        }, this.reconnectDelay * this.reconnectAttempts);
    }
    on(eventType, callback) {
        if (!this.listeners.has(eventType)) {
            this.listeners.set(eventType, []);
        }
        this.listeners.get(eventType).push(callback);
    }
    off(eventType, callback) {
        if (!this.listeners.has(eventType)) return;
        const callbacks = this.listeners.get(eventType);
        const index = callbacks.indexOf(callback);
        if (index > -1) callbacks.splice(index, 1);
    }
    notifyListeners(eventType, data) {
        if (!this.listeners.has(eventType)) return;
        this.listeners.get(eventType).forEach(callback => callback(data));
    }
    send(message) {
        if (this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        }
    }
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
}
export default new WebSocketService();
