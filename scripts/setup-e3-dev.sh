
#!/bin/bash
# Setup E3 development environment

set -e

echo "=== Setting up E3 development environment ==="

# Check Python version
PYTHON_CMD=""
if command -v python3.11 &amp;&gt; /dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3.12 &amp;&gt; /dev/null; then
    PYTHON_CMD="python3.12"
elif command -v python3 &amp;&gt; /dev/null; then
    PYTHON_CMD="python3"
else
    echo "Error: Python 3.11+ not found"
    exit 1
fi

echo "Using Python: $($PYTHON_CMD --version)"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
cd backend/e3
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# Copy env file if not exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

echo ""
echo "=== E3 development environment setup complete ==="
echo ""
echo "Next steps:"
echo "1. Edit backend/e3/.env with your configuration"
echo "2. Start PostgreSQL and Redis (e.g., using docker-compose)"
echo "3. Run the development server:"
echo "   cd backend/e3 &amp;&amp; uvicorn main:app --reload --port 8000"
echo ""

