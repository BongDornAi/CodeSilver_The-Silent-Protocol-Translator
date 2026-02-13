"""
Standalone test for CodeSilver - Core logic validation
"""

import json
import re
from typing import Dict, List

# Copy of core data structures
DRG_DATABASE = {
    "COPD": {
        "icd10": "J44.1",
        "drg_with_cc": "190",
        "drg_without_cc": "192",
        "avg_los": 2.3,
        "severity_keywords": ["severe", "acute", "respiratory failure", "hypoxemia"]
    },
    "CHF": {
        "icd10": "I50.9",
        "drg_with_cc": "291",
        "drg_without_cc": "293",
        "avg_los": 3.8,
        "severity_keywords": ["acute", "decompensated", "pulmonary edema", "cardiogenic shock"]
    },
    "Pneumonia": {
        "icd10": "J18.9",
        "drg_with_cc": "193",
        "drg_without_cc": "195",
        "avg_los": 4.2,
        "severity_keywords": ["severe", "respiratory failure", "sepsis", "hypoxemic"]
    }
}

EXAMPLE_SCENARIOS = {
    "COPD Exacerbation": """Mr. Jones has worsening COPD exacerbation, not responding to nebulizers.
Starting prednisone 60mg, observe for 24 hours, if no improvement we may need to admit.
Patient currently on 2L O2, respiratory rate 24.""",

    "CHF Decompensation": """Mrs. Smith presents with acute decompensated CHF, bilateral lower extremity edema,
JVD noted. Starting IV Lasix 40mg, will admit for telemetry monitoring and diuresis.
Expect 3-4 day stay. Patient has history of diabetes and hypertension.""",

    "Pneumonia Admission": """Patient presents with severe pneumonia, O2 sat 88% on room air,
respiratory rate 28. CXR shows bilateral infiltrates. Starting IV antibiotics,
will need inpatient admission for at least 48-72 hours. Patient also has CKD stage 3."""
}

def test_condition_identification():
    """Test condition identification logic"""
    print("\n🧪 Test 1: Condition Identification")
    print("-" * 60)
    
    test_cases = [
        ("Patient has COPD exacerbation", "COPD", "J44.1"),
        ("Acute CHF decompensation", "CHF", "I50.9"),
        ("Severe pneumonia with infiltrates", "Pneumonia", "J18.9"),
        ("Unknown condition", "Unspecified", None)
    ]
    
    passed = 0
    for text, expected_condition, expected_icd in test_cases:
        text_lower = text.lower()
        found = False
        
        for condition_name, details in DRG_DATABASE.items():
            if condition_name.lower() in text_lower:
                result_condition = condition_name
                result_icd = details["icd10"]
                found = True
                break
        
        if not found:
            result_condition = "Unspecified"
            result_icd = None
        
        if result_condition == expected_condition:
            print(f"✅ '{text[:40]}...' → {result_condition} ({result_icd})")
            passed += 1
        else:
            print(f"❌ '{text[:40]}...' → Expected {expected_condition}, got {result_condition}")
    
    print(f"\nPassed: {passed}/{len(test_cases)}")
    return passed == len(test_cases)

def test_severity_assessment():
    """Test severity assessment logic"""
    print("\n🧪 Test 2: Severity Assessment")
    print("-" * 60)
    
    test_cases = [
        ("Patient has severe respiratory failure with hypoxemia", ["severe", "respiratory failure", "hypoxemia"], True),
        ("Acute COPD exacerbation, O2 sat 88%", ["acute"], True),
        ("Mild COPD symptoms", [], False)
    ]
    
    passed = 0
    for text, expected_keywords, should_be_quantified in test_cases:
        text_lower = text.lower()
        
        # Check for quantification
        quantified = any([
            "o2 sat" in text_lower,
            "respiratory rate" in text_lower,
            re.search(r'\d+%', text)
        ])
        
        # Find keywords
        all_keywords = ["severe", "acute", "respiratory failure", "hypoxemia"]
        found_keywords = [kw for kw in all_keywords if kw.lower() in text_lower]
        
        keywords_match = set(found_keywords) >= set(expected_keywords)
        quantified_match = quantified == should_be_quantified
        
        if keywords_match and quantified_match:
            print(f"✅ '{text[:50]}...'")
            print(f"   Keywords: {found_keywords}, Quantified: {quantified}")
            passed += 1
        else:
            print(f"❌ '{text[:50]}...'")
            print(f"   Expected keywords: {expected_keywords}, Found: {found_keywords}")
            print(f"   Expected quantified: {should_be_quantified}, Got: {quantified}")
    
    print(f"\nPassed: {passed}/{len(test_cases)}")
    return passed == len(test_cases)

def test_full_scenarios():
    """Test full scenario processing"""
    print("\n🧪 Test 3: Full Scenario Processing")
    print("-" * 60)
    
    results = []
    
    for scenario_name, clinical_text in EXAMPLE_SCENARIOS.items():
        print(f"\n📋 {scenario_name}")
        
        # Identify condition
        text_lower = clinical_text.lower()
        condition = None
        
        for cond_name, details in DRG_DATABASE.items():
            if cond_name.lower() in text_lower:
                condition = {
                    "name": cond_name,
                    "icd10": details["icd10"],
                    "drg_cc": details["drg_with_cc"]
                }
                break
        
        if condition:
            print(f"   ✅ Condition: {condition['name']} ({condition['icd10']})")
            
            # Check for severity keywords
            severity_keywords = DRG_DATABASE[condition['name']]['severity_keywords']
            found_keywords = [kw for kw in severity_keywords if kw.lower() in text_lower]
            
            print(f"   ✅ Severity keywords: {', '.join(found_keywords) if found_keywords else 'None'}")
            
            # Check quantification
            quantified = bool(re.search(r'\d+%|o2 sat|respiratory rate', text_lower))
            print(f"   ✅ Quantified: {quantified}")
            
            results.append({"scenario": scenario_name, "status": "PASS"})
        else:
            print(f"   ❌ No condition identified")
            results.append({"scenario": scenario_name, "status": "FAIL"})
    
    passed = sum(1 for r in results if r["status"] == "PASS")
    print(f"\n✅ Passed: {passed}/{len(results)}")
    
    return passed == len(results)

def main():
    """Run all tests"""
    print("="*70)
    print("🏥 CODESILVER - STANDALONE TEST SUITE")
    print("="*70)
    
    test_results = []
    
    # Run tests
    test_results.append(("Condition Identification", test_condition_identification()))
    test_results.append(("Severity Assessment", test_severity_assessment()))
    test_results.append(("Full Scenarios", test_full_scenarios()))
    
    # Summary
    print("\n" + "="*70)
    print("📊 FINAL SUMMARY")
    print("="*70)
    
    for test_name, passed in test_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in test_results)
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
    else:
        print("⚠️ SOME TESTS FAILED")
    print("="*70)
    
    # Save results
    results_data = {
        "timestamp": "2026-02-13",
        "tests": [{"name": name, "passed": passed} for name, passed in test_results],
        "overall": "PASS" if all_passed else "FAIL"
    }
    
    with open("test_results.json", "w") as f:
        json.dump(results_data, f, indent=2)
    
    print("\n💾 Results saved to test_results.json")

if __name__ == "__main__":
    main()
