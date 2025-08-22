#!/bin/bash

# Actualizar pip
python -m pip install --upgrade pip

# Instalar dependencias
pip install -r backend/requirements.txt

# Crear directorio para la base de datos si no existe
mkdir -p backend/data

# Mostrar versiones instaladas
python --version
pip list
