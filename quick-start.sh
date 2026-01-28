#!/bin/bash
# quick-start.sh: Get the pipeline running locally in minutes

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "=== econ-llm: Quick Start ==="
echo ""

# Step 1: Create venv
if [ ! -d "venv" ]; then
    echo "1️⃣  Creating Python virtual environment..."
    python3 -m venv venv
else
    echo "✓ Virtual environment exists"
fi

# Step 2: Activate venv
echo "2️⃣  Activating virtual environment..."
source venv/bin/activate

# Step 3: Install dependencies
echo "3️⃣  Installing dependencies..."
pip install -q -r requirements.txt

# Step 4: Test imports
echo "4️⃣  Testing Python imports..."
python3 -c "import yaml; import openai; print('✓ Dependencies OK')"

# Step 5: Show structure
echo ""
echo "5️⃣  Repository structure:"
echo ""
find . -type d -name "venv" -prune -o -type f \( -name "*.py" -o -name "*.yaml" -o -name "*.txt" -o -name "*.md" \) -print | head -30 | sed 's|^\./||'

echo ""
echo "=== Ready! ==="
echo ""
echo "Next steps:"
echo "  1. Create .env with your OpenAI API key:"
echo "     echo 'OPENAI_API_KEY=sk-...' > .env"
echo ""
echo "  2. Run pipeline manually:"
echo "     python pipeline/main.py"
echo ""
echo "  3. Check outputs:"
echo "     ls -la data/archive/"
echo ""
echo "  For full docs, see PIPELINE.md"
echo ""
