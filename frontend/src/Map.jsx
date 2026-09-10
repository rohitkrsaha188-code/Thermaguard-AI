import L from "leaflet";
import { useMemo, useRef } from "react";
import { CircleMarker, MapContainer, Marker, Popup, TileLayer, useMap, LayersControl } from "react-leaflet";

import { CLASS_COLORS, RISK_COLORS } from "./constants";

const INDUSTRIAL_ICON = new L.DivIcon({
  className: "",
  html: `<div style="
    width:10px;height:10px;
    background:#161d29;
    border:2px solid #8996a8;
    transform:rotate(45deg);
  "></div>`,
  iconSize: [10, 10],
  iconAnchor: [5, 5],
});

function MapController({ mapRef }) {
  mapRef.current = useMap();
  return null;
}

function FlyToEvent({ event }) {
  const map = useMap();
  if (event) {
    map.flyTo([event.latitude, event.longitude], Math.max(map.getZoom(), 9), { duration: 0.6 });
  }
  return null;
}

export default function Map({ events, industrialSites, selectedEvent, onSelectEvent, focusEvent }) {
  const center = useMemo(() => [21.5, 79.0], []);
  const mapRef = useRef(null);

  function handleViewDetails(evt) {
    if (mapRef.current) mapRef.current.closePopup();
    onSelectEvent(evt);
  }

  return (
    <MapContainer center={center} zoom={5} className="leaflet-container">
      <MapController mapRef={mapRef} />
      
      <LayersControl position="topright">
        <LayersControl.BaseLayer checked name="Dark Map">
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png?key=cb1_328h_1_73d0124bd69f096f2afe7cb4"
          />
        </LayersControl.BaseLayer>
        <LayersControl.BaseLayer name="Satellite">
          <TileLayer
            attribution='&copy; <a href="https://www.esri.com/">Esri</a> &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
            url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
          />
        </LayersControl.BaseLayer>
      </LayersControl>

      {industrialSites.map((site) => (
        <Marker key={site.id} position={[site.latitude, site.longitude]} icon={INDUSTRIAL_ICON}>
          <Popup>
            <div className="map-popup-title">{site.name}</div>
            <div className="map-popup-meta">{site.type.replace(/_/g, " ")}</div>
          </Popup>
        </Marker>
      ))}

      {events.map((evt) => {
        const color = CLASS_COLORS[evt.classification] || "#5b6b84";
        const isCritical = evt.risk_level === "Critical";
        const isSelected = selectedEvent?.id === evt.id;
        return (
          <CircleMarker
            key={evt.id}
            center={[evt.latitude, evt.longitude]}
            radius={isSelected ? 9 : isCritical ? 7 : 5.5}
            pathOptions={{
              color: isSelected ? "#e7ecf2" : color,
              weight: isSelected ? 2 : isCritical ? 2 : 1,
              fillColor: color,
              fillOpacity: 0.85,
            }}
          >
            <Popup>
              <div className="map-popup-title" style={{ color }}>
                {evt.classification}
              </div>
              <div className="map-popup-meta">
                {evt.id} · FRP {evt.frp ?? "—"} MW
                <br />
                Risk:{" "}
                <span style={{ color: RISK_COLORS[evt.risk_level] }}>
                  {evt.risk_level} ({evt.risk_score})
                </span>
              </div>
              <button onClick={() => handleViewDetails(evt)}>View full details</button>
            </Popup>
          </CircleMarker>
        );
      })}

      {focusEvent && <FlyToEvent event={focusEvent} />}
    </MapContainer>
  );
}
