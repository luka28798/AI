const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use("/summarize",
    createProxyMiddleware( { target: "http://localhost:5000" ,changeOrigin: true})
  );
};