const mqtt = require('mqtt');
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const iotEndpoint = 'a2r4mm3a3xnjy9-ats.iot.ap-south-1.amazonaws.com';
const privateKeyPath = path.resolve(__dirname, './private.pem.key');
const clientCertPath = path.resolve(__dirname, './certificate.pem.crt');
const caCertPath = path.resolve(__dirname, './AmazonRootCA1.pem');

const app = express();
app.use(cors());
app.use(bodyParser.json());

// Initialize MQTT client
const initMqttClient = () => {
  const options = {
    key: fs.readFileSync(privateKeyPath),
    cert: fs.readFileSync(clientCertPath),
    ca: fs.readFileSync(caCertPath),
    clientId: 'client_' + Math.random().toString(36).substring(7),
    host: iotEndpoint,
    port: 8883,
    protocol: 'mqtts',
    keepalive: 60,
    reconnectPeriod: 1000,
    connectTimeout: 30 * 1000,
    protocolId: 'MQTT',
    protocolVersion: 4,
    clean: true
  };

  const client = mqtt.connect(`mqtts://${iotEndpoint}:8883`, options);

  client.on('error', (err) => {
    console.log('Connection Error:', err);
  });

  client.on('reconnect', () => {
    console.log('Reconnecting...');
  });

  client.on('connect', () => {
    console.log('Connected to AWS IoT MQTT broker');
  });

  client.on('message', (topic, message) => {
    console.log(`Received message: ${message.toString()} on topic: ${topic}`);
    // Send message to all SSE clients
    sseClients.forEach(client => client.res.write(`data: ${message.toString()}\n\n`));
  });

  return client;
};

const sseClients = [];

app.get('/events', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  // Add the client to the list
  const client = { res };
  sseClients.push(client);

  // Remove client when connection is closed
  req.on('close', () => {
    sseClients.splice(sseClients.indexOf(client), 1);
  });
});

const client = initMqttClient();

app.post('/publish', (req, res) => {
  const { topic, payload } = req.body;
  if (client && client.connected) {
    client.publish(topic, payload, { qos: 0 }, (err) => {
      if (err) {
        res.status(500).send('Publish error');
        console.error('Publish error:', err);
      } else {
        res.status(200).send('Message published');
      }
    });
  } else {
    res.status(500).send('MQTT Client is not connected');
  }
});

app.post('/subscribe', (req, res) => {
  const { topic } = req.body;
  if (client && client.connected) {
    client.subscribe(topic, { qos: 0 }, (err) => {
      if (err) {
        res.status(500).send('Subscribe error');
        console.error('Subscribe error:', err);
      } else {
        res.status(200).send('Subscribed to topic');
      }
    });
  } else {
    res.status(500).send('MQTT Client is not connected');
  }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
