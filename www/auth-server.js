const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const rateLimit = require('express-rate-limit');
const helmet = require('helmet');
const uuid = require('uuid');
const crypto = require('crypto');
const https = require('https');
const fs = require('fs');
const path = require('path');

const app = express();
const path = require('path');

// Security middleware
app.use(helmet());
app.use(express.json());

// Serve static files from public directory
app.use(express.static(path.join(__dirname, 'public')));

// Rate limiting
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100 // limit each IP to 100 requests per windowMs
});
app.use(limiter);

// Secret key for JWT
const JWT_SECRET = crypto.randomBytes(64).toString('hex');

// Simulated secure database (replace with real database in production)
const users = new Map();
const streamKeys = new Map();
const sessions = new Map();

// Authentication middleware
const authenticateToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) {
        return res.sendStatus(401);
    }

    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) {
            return res.sendStatus(403);
        }
        req.user = user;
        next();
    });
};

// Login endpoint with rate limiting
const loginLimiter = rateLimit({
    windowMs: 60 * 60 * 1000, // 1 hour
    max: 5 // 5 attempts per hour
});

app.post('/login', loginLimiter, async (req, res) => {
    const { username, password } = req.body;

    if (!username || !password) {
        return res.status(400).json({ error: 'Missing credentials' });
    }

    const user = users.get(username);
    if (!user) {
        return res.status(401).json({ error: 'Invalid credentials' });
    }

    try {
        if (await bcrypt.compare(password, user.password)) {
            const token = jwt.sign({ username: user.username, role: user.role }, JWT_SECRET, { expiresIn: '1h' });
            return res.json({ token });
        } else {
            return res.status(401).json({ error: 'Invalid credentials' });
        }
    } catch (error) {
        return res.status(500).json({ error: 'Internal server error' });
    }
});

// Stream key validation endpoint
app.post('/auth', async (req, res) => {
    const streamKey = req.body.key;
    
    if (!streamKey || !streamKeys.has(streamKey)) {
        return res.sendStatus(403);
    }

    const streamData = streamKeys.get(streamKey);
    if (streamData.expiresAt < Date.now()) {
        streamKeys.delete(streamKey);
        return res.sendStatus(403);
    }

    res.sendStatus(200);
});

// Generate stream key endpoint (requires authentication)
app.post('/generate-key', authenticateToken, (req, res) => {
    if (req.user.role !== 'broadcaster') {
        return res.sendStatus(403);
    }

    const streamKey = crypto.randomBytes(32).toString('hex');
    streamKeys.set(streamKey, {
        user: req.user.username,
        createdAt: Date.now(),
        expiresAt: Date.now() + (24 * 60 * 60 * 1000) // 24 hours
    });

    res.json({ streamKey });
});

// Root route
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Initialize an admin user (remove in production)
const initializeAdmin = async () => {
    const password = crypto.randomBytes(12).toString('hex');
    const hashedPassword = await bcrypt.hash(password, 10);
    
    users.set('admin', {
        username: 'admin',
        password: hashedPassword,
        role: 'broadcaster'
    });

    console.log('Admin credentials:', {
        username: 'admin',
        password: password
    });
};

const HTTP_PORT = process.env.HTTP_PORT || 3000;
const HTTPS_PORT = process.env.HTTPS_PORT || 3443;

// HTTP Server (will redirect to HTTPS)
app.listen(HTTP_PORT, () => {
    console.log(`HTTP server running on port ${HTTP_PORT}`);
});

// HTTPS Server
const httpsOptions = {
    key: fs.readFileSync('/etc/nginx/ssl/streaming.key'),
    cert: fs.readFileSync('/etc/nginx/ssl/streaming.crt')
};

https.createServer(httpsOptions, app).listen(HTTPS_PORT, () => {
    console.log(`HTTPS server running on port ${HTTPS_PORT}`);
    initializeAdmin();
});