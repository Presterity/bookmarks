const express = require('express'),
	path = require('path'),
	app = express();

const PORT = process.env.PORT || 8090;

app.use(express.static(path.join(__dirname, 'public')));

app.listen(PORT, function () {
	console.log(`listening on port ${PORT}`);
});
