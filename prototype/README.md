# Thermaguard AI - Standalone Prototype

This folder contains a lightweight, fully standalone, static HTML/JS/CSS prototype of the Thermaguard AI dashboard. 

## Purpose
This prototype is designed specifically for **hackathon demonstrations and quick previews**. It completely bypasses the need for the Python backend, PostgreSQL database, or React development servers. It uses hardcoded, realistic demo data to guarantee a flawless presentation, even in environments with restrictive firewalls or unstable internet connections.

## Features Demonstrated
- **Interactive Map:** Powered by Leaflet, featuring both CARTO Dark Matter and Esri World Imagery Satellite base layers.
- **Mock Data Visualization:** Renders color-coded industrial fires, gas flares, and agricultural fires based on risk level.
- **Interactive Side Panel:** Click on any alert or map marker to view detailed properties.
- **Before & After Satellite Slider:** Demonstrates our integration with the NASA GIBS API to fetch and overlay historical satellite imagery of the fire location.

## How to Run

1. Open this `prototype/` folder in your file explorer.
2. Double-click on `index.html`.
3. It will open instantly in your default web browser. No terminals, no installations, no servers required!
