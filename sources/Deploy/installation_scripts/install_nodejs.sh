#!/bin/bash
# Salir inmediatamente si un comando falla.
set -e

echo "--- Actualizando la lista de paquetes ---"
apt-get update -y

echo "--- Instalando Node.js y npm ---"
apt-get install -y nodejs npm

echo "--- Verificando las versiones instaladas ---"
node -v
npm -v
npx -v

echo "--- La instalación de Node.js a nivel de sistema se ha completado ---"