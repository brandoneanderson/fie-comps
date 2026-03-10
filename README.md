# FIE COMPS  
**Malicious Browser Extension Detection and Classification**  
Isha Patel, Francisco Arenas, and Ekow Anderson  
Winter 2026

## Overview
This project analyzes Chrome browser extensions to help detect potentially malicious behavior. Our system combines **static analysis** of extension files with **machine learning classification** to produce an interpretable security assessment.

The scanner examines components such as:

- `manifest.json`
- JavaScript files
- HTML files
- CSS files

It extracts security-related features, runs them through our analysis pipeline, and generates a classification or risk-based result.

## Project Goals
The main goals of this project are to:

- Detect suspicious or malicious browser extension behavior
- Extract meaningful security features from extension code
- Apply machine learning models for classification
- Provide an understandable output that can help users evaluate extension risk

## Features
- Chrome extension download and analysis pipeline
- Static parsing of extension source files
- Feature extraction from:
  - Manifest permissions
  - JavaScript behavior
  - HTML structure
  - CSS properties
- Machine learning models for final classification
- Risk scoring / prediction reporting
- Integration between local web interface and VM-based analysis environment

## Project Structure
A general overview of the repository:

```text
fie-comps/
├── parser/                # Main parsing and analysis pipeline
├── Scanners/              # File-specific scanners/parsers
├── ML/                    # Machine learning models and scoring
├── public/                # Frontend assets
├── server.js              # Local web server
├── requirements.txt       # Python dependencies
└── README.md
