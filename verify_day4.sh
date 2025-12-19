#!/bin/bash
echo "🔍 Verifying Day 4 Implementation..."
echo ""

# Check if server is running
echo -n "Checking API server: "
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Running"
else
    echo "❌ Not running"
    echo "   Start with: python -m app.main"
    exit 1
fi

# Test critical case
echo -n "Testing critical urgency: "
RESULT=$(curl -s -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "Electric spark coming from switch"}' \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('urgency', 'ERROR'))")

if [ "$RESULT" = "Critical" ]; then
    echo "✅ Correct (Critical)"
else
    echo "❌ Failed (got: $RESULT)"
fi

# Test low urgency
echo -n "Testing low urgency: "
RESULT=$(curl -s -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "Tap is leaking slightly in washroom"}' \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('urgency', 'ERROR'))")

if [ "$RESULT" = "Low" ]; then
    echo "✅ Correct (Low)"
else
    echo "❌ Failed (got: $RESULT)"
fi

# Test API structure
echo -n "Testing API response format: "
RESULT=$(curl -s -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "test"}' \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
required = ['category', 'category_confidence', 'urgency', 'urgency_confidence']
missing = [f for f in required if f not in data]
if missing:
    print('MISSING: ' + ', '.join(missing))
else:
    print('✅ Complete')
")

echo "$RESULT"

echo ""
echo "📊 Quick Verification Complete!"
echo "   Run detailed tests: python scripts/validate_day4_fixed.py"
echo "   API Docs: http://localhost:8000/docs"
