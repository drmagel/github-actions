/**
 * Version Manager UI - API Helper and Context
 */

const API_BASE = '/v1';

// Auth Context
const AuthContext = React.createContext(null);
const useAuth = () => React.useContext(AuthContext);

// API Helper
const api = {
    async get(endpoint) {
        const res = await fetch(`${API_BASE}${endpoint}`);
        if (!res.ok) throw new Error(`API Error: ${res.status}`);
        return res.json();
    },
    async post(endpoint, data) {
        const res = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error(`API Error: ${res.status}`);
        return res.json();
    },
    async put(endpoint, data = null) {
        const options = { method: 'PUT' };
        if (data) {
            options.headers = { 'Content-Type': 'application/json' };
            options.body = JSON.stringify(data);
        }
        const res = await fetch(`${API_BASE}${endpoint}`, options);
        if (!res.ok) throw new Error(`API Error: ${res.status}`);
        return res.json();
    },
    async delete(endpoint) {
        const res = await fetch(`${API_BASE}${endpoint}`, { method: 'DELETE' });
        if (!res.ok) throw new Error(`API Error: ${res.status}`);
        return res.json();
    }
};

