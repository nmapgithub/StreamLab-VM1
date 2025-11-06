const express = require('express');
const router = express.Router();
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// Vulnerable session management
const sessions = new Map();

// Weak encryption key
const ENCRYPTION_KEY = Buffer.from('4447534553494F4E', 'hex');

// Vulnerable function to encrypt stream data
function encryptStreamData(data) {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv('aes-128-cbc', ENCRYPTION_KEY, iv);
    let encrypted = cipher.update(JSON.stringify(data), 'utf8', 'hex');
    encrypted += cipher.final('hex');
    return { encrypted, iv: iv.toString('hex') };
}

// Vulnerable stream management endpoints
router.post('/streams/create', (req, res) => {
    const { name, quality } = req.body;
    const streamKey = crypto.randomBytes(16).toString('hex');
    
    // Intentionally vulnerable file operations
    const streamConfig = {
        name,
        quality,
        key: streamKey,
        created: Date.now(),
        // Part of the flag embedded in stream config
        metadata: Buffer.from('STREAM_FLAG{p4rt_1_0f_4}').toString('base64')
    };
    
    fs.writeFileSync(
        path.join(__dirname, 'streams', `${name}.json`),
        JSON.stringify(streamConfig)
    );
    
    res.json({ success: true, streamKey });
});

// Vulnerable stream key validation
router.get('/streams/:streamId/validate', (req, res) => {
    const { streamId } = req.params;
    const { token } = req.query;
    
    // Intentionally vulnerable path traversal
    const configPath = path.join(__dirname, 'streams', `${streamId}.json`);
    
    try {
        const config = JSON.parse(fs.readFileSync(configPath));
        
        // Weak token validation
        if (token === crypto.createHash('md5').update(config.key).digest('hex')) {
            const { encrypted, iv } = encryptStreamData(config);
            res.json({ success: true, data: encrypted, iv });
        } else {
            res.status(403).json({ error: 'Invalid token' });
        }
    } catch (err) {
        res.status(500).json({ error: 'Stream configuration error' });
    }
});

// Vulnerable stream control endpoint
router.post('/streams/:streamId/control', (req, res) => {
    const { streamId } = req.params;
    const { action, params } = req.body;
    
    // Intentionally vulnerable command injection
    if (action === 'transcode') {
        const cmd = `ffmpeg -i rtmp://localhost/live/${streamId} ${params}`;
        require('child_process').exec(cmd, (error, stdout, stderr) => {
            res.json({ success: true, output: stdout });
        });
    } else {
        res.status(400).json({ error: 'Invalid action' });
    }
});

module.exports = router;