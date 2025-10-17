#!/bin/bash
# AEGIS FULL VALIDATION PROTOCOL
# Executes comprehensive testing with compliance receipts

echo "============================================================"
echo "🔍 AEGIS FULL VALIDATION PROTOCOL - STARTING"
echo "============================================================"
echo ""

cd ~/tps19

# Run comprehensive test suite
echo "📋 Executing comprehensive test suite..."
python3 comprehensive_test_suite.py 2>&1 | tee validation_output.txt

EXIT_CODE=$?

echo ""
echo "============================================================"
echo "📊 VALIDATION COMPLETE"
echo "============================================================"
echo ""

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ ALL TESTS PASSED - SYSTEM READY FOR DEPLOYMENT"
    echo ""
    echo "🚀 To start trading bot:"
    echo "   python3 tps19_main.py"
    echo ""
    echo "📱 To run in background (keeps running):"
    echo "   sudo apt install -y tmux"
    echo "   tmux new -s tps19"
    echo "   python3 tps19_main.py"
    echo "   # Press Ctrl+B then D to detach"
else
    echo "❌ TESTS FAILED - REVIEW ERRORS ABOVE"
    echo ""
    echo "📄 Full report saved to:"
    echo "   ~/tps19/COMPREHENSIVE_VALIDATION_RECEIPT.txt"
    echo "   ~/tps19/validation_report.json"
    echo "   ~/tps19/validation_output.txt"
fi

echo ""
echo "============================================================"

exit $EXIT_CODE
