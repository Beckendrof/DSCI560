const express = require('express');
const mysql = require('mysql');
const path = require('path');
const app = express();
const port = 3000;

app.use(express.static(path.join(__dirname, '..', 'public')));  

const db = mysql.createConnection({
  host: 'localhost',
  user: 'raydiant_user',
  password: 'StrongPassword123!',
  database: 'raydiant',
  authSwitchHandler: function ({ pluginName, pluginData }, cb) {
    if (pluginName === 'caching_sha2_password') {
      // Use the older 'mysql_native_password' authentication method
      cb(null, Buffer.from('StrongPassword123!'));
    } else {
      // Use the default method
      cb(new Error('Unsupported authentication method'));
    }
  }
});

db.connect((err) => {
  if (err) {
    console.error('Error connecting to MySQL:', err);
  }
});

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '..', 'public', 'index.html'));
});

app.get('/pins', (req, res) => {
  db.query('SELECT * FROM data', (error, results) => {
    if (error) {
      console.error('Error fetching pins:', error);
      res.status(500).json({ error: 'Internal Server Error' });
    } else {
      const pinsData = results.map(pin => ({
        api: pin.api,
        latitude: pin.latitude,
        longitude: pin.longitude,
        well_name: pin.well_name,
        well_number: pin.well_number,
        date_stimulated: pin.date_stimulated,
        top_ft: pin.top_ft,
        bottom_ft: pin.bottom_ft,
        stimulation_stages: pin.stimulation_stages,
        volume: pin.volume,
        volume_units: pin.volume_units,
        acid_percent: pin.acid_percent,
        type_treatment: pin.type_treatment,
        lbs_proppant: pin.lbs_proppant,
        max_treatment_pressure: pin.max_treatment_pressure,
        max_treatment_rate: pin.max_treatment_rate,
        ClosestCity: pin.ClosestCity, 
        WellType: pin.WellType, 
        WellStatus: pin.WellStatus, 
        OilProduced: pin.OilProduced, 
        GasProduced: pin.GasProduced, 
        Operator: pin.Operator, 
        Location: pin.Location 
      }));
      res.json(pinsData);
    }
  });
});

app.listen(port, () => {
  console.log(`Web app is running at http://localhost:${port}`);
});
