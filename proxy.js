const { createProxyMiddleware } = require('http-proxy-middleware');
const express = require('express');
const app = express();

app.use('/api', createProxyMiddleware({
    target: 'http://localhost:5000',
    changeOrigin: true,
    pathRewrite: {
        '^/api': '', // remove /api prefix
    },
}));

app.listen(3000, () => {
    console.log('Proxy server is running on http://localhost:3000');
});
