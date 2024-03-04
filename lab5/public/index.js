const map = L.map('map').setView([48.074308, -103.603161], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

fetch('/pins')
  .then(response => response.json())
  .then(pins => {
    temp = 0
    pins.forEach(pin => {
      temp+=1
      // Check if both latitude and longitude are present and valid
      if (pin.latitude !== null && pin.longitude !== null) {
        coordinates = getCoordinates(pin.latitude, pin.longitude);
        latitude = coordinates.latitude
        longitude = coordinates.longitude
        // Check if conversion was successful
        if (!isNaN(latitude) && !isNaN(longitude)) {
          const marker = L.marker([latitude, longitude]).addTo(map);
          marker.bindPopup(`<b>${pin.well_number}</b><br>
          Well Name: ${pin.well_name}<br>
          API: ${pin.api}<br>
          Date Stimulated: ${pin.date_stimulated}<br>
          Top (ft): ${pin.top_ft}<br>
          Bottom (ft): ${pin.bottom_ft}<br>
          Stimulation Stages: ${pin.stimulation_stages}<br>
          Volume: ${pin.volume} ${pin.volume_units}<br>
          Acid Percentage: ${pin.acid_percent}<br>
          Type of Treatment: ${pin.type_treatment}<br>
          Proppant (lbs): ${pin.lbs_proppant}<br>
          Max Treatment Pressure: ${pin.max_treatment_pressure}<br>
          Max Treatment Rate: ${pin.max_treatment_rate}
          Closest City: ${pin.ClosestCity}<br> 
          Well Type: ${pin.WellType}<br> 
          Well Status: ${pin.WellStatus}<br> 
          Oil Produced: ${pin.OilProduced}<br> 
          Gas Produced: ${pin.GasProduced}<br> 
          Operator: ${pin.Operator}<br> 
          Location: ${pin.Location}`);
        } else {
          console.error(`Invalid latitude or longitude for pin with title: ${pin.title}`);
        }
      } else {
        console.error(`Latitude or longitude missing for pin with title: ${pin.title}`);
      }
    });
    console.log(`${temp} wells plotted`)
  })
  .catch(error => console.error('Error fetching pins:', error));

// Function to convert degrees, minutes, and seconds to decimal degrees
function getCoordinates(latStr, lonStr) {
  // Split latitude and longitude strings into parts
  const latParts = latStr.replace("°", "").replace("'", "").replace("N", "").split(' ');
  const lonParts = lonStr.replace("°", "").replace("'", "").replace("W", "").split(' ');

  // Extract degree, minute, and second components for latitude
  const latDeg = parseFloat(latParts[0]);
  const latMin = parseFloat(latParts[1]) || 0;
  const latSec = parseFloat(latParts[2]) || 0;

  // Extract degree, minute, and second components for longitude
  const lonDeg = parseFloat(lonParts[0]);
  const lonMin = parseFloat(lonParts[1]) || 0;
  const lonSec = parseFloat(lonParts[2]) || 0;

  // Determine direction for latitude and longitude
  const latDirection = latStr.includes('N') ? 1 : -1;
  const lonDirection = lonStr.includes('E') ? 1 : -1;

  // Calculate latitude and longitude in decimal degrees
  const latitude = latDirection * (latDeg + latMin/60 + latSec/3600);
  const longitude = lonDirection * (lonDeg + lonMin/60 + lonSec/3600);

  return { latitude, longitude };
}
