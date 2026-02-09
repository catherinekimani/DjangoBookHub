const express = require('express')
const app = express()

// Middleware logs each request
app.use((req, res, next) => {
	console.log('Request received');
});

// Route handler responds to /users
app.get('/users', (req, res) => {
	res.send('User list');
});

// Start the server
app.listen(3000, () => {
	console.log('Server is running on port 3000');
})