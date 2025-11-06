const express = require('express');
const sqlite3 = require('sqlite3');
const crypto = require('crypto');
const app = express();

// Intentionally vulnerable database connection
const db = new sqlite3.Database('./streams.db');

// Weak key generation
const generateStreamKey = () => {
    return crypto.randomBytes(8).toString('hex');
};

// Vulnerable stream key validation
app.post('/auth', express.json(), (req, res) => {
    const { streamKey } = req.body;
    
    // Intentionally vulnerable SQL query
    const query = `SELECT * FROM streams WHERE key = '${streamKey}'`;
    
    db.get(query, (err, row) => {
        if (err) {
            console.error(err);
            return res.status(500).json({ error: 'Database error' });
        }
        
        // Race condition vulnerability
        setTimeout(() => {
            if (row) {
                // Weak token generation
                const token = crypto.createHash('md5')
                    .update(streamKey + Date.now().toString())
                    .digest('hex');
                    
                res.json({ success: true, token });
            } else {
                res.status(403).json({ error: 'Invalid stream key' });
            }
        }, Math.random() * 1000);
    });
});

// Vulnerable stream metadata endpoint
app.get('/stream/:id/metadata', (req, res) => {
    const streamId = req.params.id;
    const query = `SELECT metadata FROM streams WHERE id = ${streamId}`;
    
    db.get(query, (err, row) => {
        if (err || !row) {
            return res.status(404).json({ error: 'Stream not found' });
        }
        
        // Intentionally vulnerable metadata parsing
        try {
            const metadata = JSON.parse(row.metadata);
            res.json(metadata);
        } catch (e) {
            res.status(500).json({ error: 'Invalid metadata' });
        }
    });
});

app.listen(8080, () => {
    console.log('Auth server running on port 8080');
});