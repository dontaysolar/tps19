#!/bin/bash
################################################################################
# TPS19 - RUN ALL TESTS
# Comprehensive testing suite
################################################################################

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                              ║"
echo "║                    🧪 TPS19 - COMPLETE TEST SUITE 🧪                         ║"
echo "║                                                                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run test
run_test() {
    TEST_NAME=$1
    TEST_COMMAND=$2
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🧪 Running: $TEST_NAME"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if eval "$TEST_COMMAND"; then
        echo ""
        echo "✅ $TEST_NAME PASSED"
        echo ""
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo ""
        echo "❌ $TEST_NAME FAILED"
        echo ""
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# Run all tests
echo "Starting comprehensive test suite..."
echo ""

run_test "Startup Validation" "python3 validate_startup.py"
run_test "Unit Tests (Core Layers)" "python3 test_suite.py"
run_test "Integration Tests" "python3 test_integration.py"
run_test "End-to-End Tests" "python3 test_end_to_end.py"

# Summary
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                              ║"
echo "║                         📊 FINAL TEST RESULTS                                ║"
echo "║                                                                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Total Test Suites:  $TOTAL_TESTS"
echo "✅ Passed:          $PASSED_TESTS"
echo "❌ Failed:          $FAILED_TESTS"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo "✅ ALL TESTS PASSED - SYSTEM READY FOR USE"
    echo ""
    echo "Next steps:"
    echo "  1. python3 tps19_integrated.py paper  ← Start paper trading"
    echo "  2. ./quick_start_integrated.sh        ← Full stack with web UI"
    echo ""
    exit 0
else
    echo "❌ SOME TESTS FAILED - FIX ISSUES BEFORE USING"
    echo ""
    echo "Check the errors above and:"
    echo "  1. Install missing dependencies"
    echo "  2. Fix configuration issues"
    echo "  3. Run tests again"
    echo ""
    exit 1
fi
