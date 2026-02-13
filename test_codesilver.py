"""
Test script for CodeSilver translator - validates core logic without UI
"""

import json
import re
from typing import Dict, List
from datetime import datetime

# Import data structures from main file
from codesilver_the_silent_real_time_translator import (
    DRG_DATABASE,
    ADMISSION_RULES,
    PRIOR_AUTH_DATABASE,
    EXAMPLE_SCENARIOS,
    CodeSilverTranslator,
    calculate_denial_risk
)

def run_tests():
    """Run validation tests on all scenarios"""
    
    print("="*70)
    print("🧪 CODESILVER VALIDATION TEST SUITE")
    print("="*70)
    print()
    
    translator = CodeSilverTranslator()
    test_results = []
    
    for scenario_name, clinical_text in EXAMPLE_SCENARIOS.items():
        print(f"\n📋 Testing: {scenario_name}")
        print("-" * 70)
        
        try:
            # Run translation
            analysis = translator.analyze_clinical_text(clinical_text)
            
            # Calculate metrics
            risk_score = calculate_denial_risk(analysis)
            
            # Display results
            print(f"✅ Condition: {analysis['condition']['name']} ({analysis['condition']['icd10']})")
            print(f"✅ Severity: {analysis['severity']['level']}")
            print(f"   - Quantified: {analysis['severity']['quantified']}")
            print(f"   - Keywords: {', '.join(analysis['severity']['keywords_found']) if analysis['severity']['keywords_found'] else 'None'}")
            print(f"✅ Status: {analysis['admission_status']['current_status']}")
            print(f"   - Expected LOS: {analysis['admission_status']['expected_los_days']} days")
            print(f"   - 2-Midnight Rule: {'✓ Compliant' if analysis['admission_status']['two_midnight_rule'] else '✗ Not met'}")
            print(f"✅ Interventions: {', '.join(analysis['interventions']) if analysis['interventions'] else 'None identified'}")
            print(f"✅ Prior Auth Required: {len(analysis['prior_auth'])} interventions")
            for auth in analysis['prior_auth']:
                print(f"   - {auth['intervention']}: {auth['commercial']}")
            print(f"✅ Documentation Gaps: {len(analysis['documentation_gaps'])}")
            for gap in analysis['documentation_gaps']:
                print(f"   - {gap[:80]}...")
            print(f"✅ Denial Risk Score: {risk_score}/10")
            
            # Format full output
            formatted_output = translator.format_output(analysis)
            
            test_results.append({
                "scenario": scenario_name,
                "status": "PASS",
                "condition": analysis['condition']['name'],
                "risk_score": risk_score,
                "gaps": len(analysis['documentation_gaps'])
            })
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            test_results.append({
                "scenario": scenario_name,
                "status": "FAIL",
                "error": str(e)
            })
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for r in test_results if r["status"] == "PASS")
    failed = sum(1 for r in test_results if r["status"] == "FAIL")
    
    print(f"\nTotal Scenarios: {len(test_results)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/len(test_results)*100):.1f}%")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY!" if failed == 0 else "⚠️ SOME TESTS FAILED")
    print("="*70)
    
    return test_results

if __name__ == "__main__":
    results = run_tests()
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n💾 Test results saved to test_results.json")
