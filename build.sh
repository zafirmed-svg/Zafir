#!/bin/bash
set -o errexit  # Exit on error

echo "Starting build process..."

# Navigate to backend directory
cd backend

# Update pip
echo "Updating pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create database directory if it doesn't exist
echo "Setting up database directory..."
mkdir -p data

# Create or update the start script
echo "Creating start script..."
cat > start.sh << 'EOF'
#!/bin/bash
export PYTHONPATH=/opt/render/project/src/backend:$PYTHONPATH
exec gunicorn main:app -k uvicorn.workers.UvicornWorker -w 4 --bind 0.0.0.0:$PORT
EOF

# Make start script executable
chmod +x start.sh

# Show installed versions
echo "Installed versions:"
python --version
pip list

echo "Build completed successfully!"
