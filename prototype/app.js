const MOCK_EVENTS = [
  { id: "TG-1001", latitude: 22.75, longitude: 71.82, classification: "Industrial Fire", frp: 120.5, confidence: 95, acquisition_time: "2026-09-08T10:00:00Z", risk_level: "Critical" },
  { id: "TG-1002", latitude: 23.55, longitude: 72.22, classification: "Gas Flare / Persistent Thermal Source", frp: 45.2, confidence: 80, acquisition_time: "2026-09-09T14:30:00Z", risk_level: "High" },
  { id: "TG-1003", latitude: 20.10, longitude: 79.50, classification: "Agricultural Fire", frp: 12.0, confidence: 60, acquisition_time: "2026-09-10T08:15:00Z", risk_level: "Medium" },
  { id: "TG-1004", latitude: 21.05, longitude: 85.12, classification: "Natural / Forest Fire", frp: 8.5, confidence: 55, acquisition_time: "2026-09-10T09:20:00Z", risk_level: "Low" }
];

const map = L.map('map', { zoomControl: false }).setView([21.5, 79.0], 5);
L.control.zoom({ position: 'topleft' }).addTo(map);

// CARTO Dark Layer
const darkLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png?key=cb1_328h_1_73d0124bd69f096f2afe7cb4', {
  attribution: '&copy; CARTO'
}).addTo(map);

// Esri Satellite Layer
const satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
  attribution: '&copy; Esri'
});

L.control.layers({"Dark Map": darkLayer, "Satellite": satelliteLayer}, {}, {position: 'topright'}).addTo(map);

// Add markers
MOCK_EVENTS.forEach(evt => {
  const color = evt.risk_level === 'Critical' ? '#ef4444' : evt.risk_level === 'High' ? '#f97316' : evt.risk_level === 'Medium' ? '#eab308' : '#10b981';
  const marker = L.circleMarker([evt.latitude, evt.longitude], {
    color: color,
    fillColor: color,
    fillOpacity: 0.8,
    weight: 2,
    radius: evt.risk_level === 'Critical' ? 8 : 6
  }).addTo(map);

  marker.on('click', () => showDetails(evt));
});

// Render sidebar alerts
const alertsContainer = document.getElementById('alerts-container');
MOCK_EVENTS.filter(e => e.risk_level === 'Critical' || e.risk_level === 'High').forEach(evt => {
  const div = document.createElement('div');
  div.className = `alert-card ${evt.risk_level.toLowerCase()}`;
  div.innerHTML = `<div class="alert-title">${evt.classification}</div><div class="alert-meta">${evt.id} · FRP: ${evt.frp} MW</div>`;
  div.onclick = () => showDetails(evt);
  alertsContainer.appendChild(div);
});

// Detail Panel Logic
let miniMapInstance = null;
let afterTileLayer = null;

function showDetails(evt) {
  const panel = document.getElementById('details-panel');
  const color = evt.risk_level === 'Critical' ? '#ef4444' : evt.risk_level === 'High' ? '#f97316' : evt.risk_level === 'Medium' ? '#eab308' : '#10b981';
  
  const afterDate = new Date(evt.acquisition_time);
  const beforeDate = new Date(afterDate.getTime() - 5 * 24 * 60 * 60 * 1000);
  
  const afterDateStr = afterDate.toISOString().split("T")[0];
  const beforeDateStr = beforeDate.toISOString().split("T")[0];

  const formattedDate = afterDate.toLocaleString("en-IN", {
    day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit"
  });

  panel.innerHTML = `
    <div class="detail-header">
      <div>
        <div class="detail-id">${evt.id}</div>
        <div style="color: ${color}; font-weight: 500;">${evt.classification}</div>
      </div>
      <button class="close-btn" onclick="closeDetails()">×</button>
    </div>
    <div class="detail-body">
      <div class="detail-row"><span class="k">Latitude</span><span class="v">${evt.latitude}</span></div>
      <div class="detail-row"><span class="k">Longitude</span><span class="v">${evt.longitude}</span></div>
      <div class="detail-row"><span class="k">Acquisition time</span><span class="v">${formattedDate}</span></div>
      <div class="detail-row"><span class="k">Detection confidence</span><span class="v">${evt.confidence}%</span></div>
      <div class="detail-row"><span class="k">FRP</span><span class="v">${evt.frp} MW</span></div>
      <div class="detail-row"><span class="k">Risk Level</span><span class="v" style="color: ${color}">${evt.risk_level}</span></div>
      
      <div class="satellite-before-after">
        <div style="font-size: 13px; font-weight: bold; color: #8996a8; margin-bottom: 10px;">SATELLITE VIEW (BEFORE / AFTER)</div>
        <div id="mini-map"></div>
        <div class="slider-container">
          <span style="font-size: 12px; color: #fff;" id="slider-label-before">Before</span>
          <input type="range" id="opacity-slider" min="0" max="1" step="0.01" value="1" oninput="updateOpacity(this.value)">
          <span style="font-size: 12px; color: #ef4444;" id="slider-label-after">After</span>
        </div>
      </div>
    </div>
  `;
  
  panel.classList.add('open');

  // Initialize mini map
  if (miniMapInstance) {
    miniMapInstance.remove();
  }

  miniMapInstance = L.map('mini-map', {
    center: [evt.latitude, evt.longitude],
    zoom: 7,
    maxZoom: 9,
    zoomControl: false,
    dragging: false,
    scrollWheelZoom: false,
    doubleClickZoom: false
  });

  L.tileLayer(`https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_SNPP_CorrectedReflectance_TrueColor/default/${beforeDateStr}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg`, {
    maxZoom: 9
  }).addTo(miniMapInstance);

  afterTileLayer = L.tileLayer(`https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_SNPP_CorrectedReflectance_TrueColor/default/${afterDateStr}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg`, {
    maxZoom: 9,
    opacity: 1
  }).addTo(miniMapInstance);

  L.circleMarker([evt.latitude, evt.longitude], { color: '#ef4444', radius: 6, fillOpacity: 0, weight: 2 }).addTo(miniMapInstance);
}

window.closeDetails = function() {
  document.getElementById('details-panel').classList.remove('open');
};

window.updateOpacity = function(val) {
  if (afterTileLayer) {
    afterTileLayer.setOpacity(parseFloat(val));
  }
  document.getElementById('slider-label-before').style.color = val < 0.5 ? '#ef4444' : '#fff';
  document.getElementById('slider-label-after').style.color = val > 0.5 ? '#ef4444' : '#fff';
};
