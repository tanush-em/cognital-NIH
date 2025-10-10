#!/bin/bash
# Start the React frontend

echo "🚀 Starting AI-First Customer Support Frontend..."
echo ""

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📥 Installing dependencies..."
    npm install
fi

# Start the development server
echo "✅ Starting Vite dev server on http://localhost:3000"
echo ""
npm run dev

