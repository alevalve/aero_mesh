# Aero Mesh

---

## Overview

`aero_mesh` is a 3D AR application that leverages AI to convert 2D images into interactive 3D augmented-reality experiences. The project combines a Python-based AI/mesh-generation backend with a JavaScript/HTML frontend for AR display.

---

## Directory Structure

```
aero_mesh/
│
├── ar_display/              # Frontend AR rendering layer
│                            # Handles display of generated 3D meshes in AR
│
├── generation/              # AI-powered 3D mesh generation logic
│                            # Core module that processes 2D images into 3D models
│
├── mesh_revisions/          # Scripts with mesh checks and improvements
│                            # (smoothing, geometry revisions, decimation, resize)
│
├── templates/               # HTML and model templates
│
├── computer_vision/         # Depth estimation of the scene
│                            # to set meshes in specific positions
│
├── index.html               # Main entry point for the web/AR interface
├── main.py                  # Primary Python script
├── main_pipeline.py         # End-to-end pipeline orchestration (2D → 3D → AR)
├── .gitignore               # Files and folders excluded from version control
└── README                   # Project description and usage notes
```

---

## Key Files

### `main_pipeline.py`
The central orchestration script. Coordinates the full workflow: ingesting a 2D image, passing it through the generation module, applying any mesh revisions, and preparing output for AR display.

### `main.py`
A primary Python entry point. Serves as a CLI tool, a lightweight server, or a utility wrapper around the pipeline.

### `index.html`
The web frontend entry point. Combined with the heavy JavaScript usage, this is where the AR experience is rendered in the browser (possibly using WebXR, Three.js, or A-Frame).

---

## Architecture Summary

```
Input (2D Image)
       │
       ▼
 3D mesh generation     ← AI mesh generation from 2D images using Meshy
       │
       ▼
 Mesh revisions         ← Refinement & Adapting to display
       │
       ▼
 Depth Estimation       ← Obtain the depth of the place where the mesh will be displayed
       │
       ▼
 AR Display             ← AR rendering (JS/WebXR)
```

---

## Run Program

```bash
cd path/to/aero_mesh
python main.py
```
