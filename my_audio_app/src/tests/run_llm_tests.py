#!/usr/bin/env python3
"""
מריץ בדיקות יחידה עבור מודלי וסירותי LLM
"""

import sys
import os
import unittest

# הוספת נתיב הפרויקט ל-PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def run_llm_tests():
    """מריץ את כל בדיקות ה-LLM"""
    
    # יצירת test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # הוספת בדיקות מודלים
    try:
        from tests.models.test_llm_models import (
            TestLLMProvider, TestLLMModel, TestUsageRecord, TestLLMParameters
        )
        
        suite.addTests(loader.loadTestsFromTestCase(TestLLMProvider))
        suite.addTests(loader.loadTestsFromTestCase(TestLLMModel))
        suite.addTests(loader.loadTestsFromTestCase(TestUsageRecord))
        suite.addTests(loader.loadTestsFromTestCase(TestLLMParameters))
        
        print("✅ נטענו בדיקות מודלי LLM")
        
    except ImportError as e:
        print(f"❌ שגיאה בטעינת בדיקות מודלי LLM: {e}")
        return False
    
    # הוספת בדיקות שירותים
    try:
        from tests.services.test_llm_service import TestLLMService
        from tests.services.test_settings_service import TestSettingsService
        from tests.services.test_usage_service import TestUsageService
        
        suite.addTests(loader.loadTestsFromTestCase(TestLLMService))
        suite.addTests(loader.loadTestsFromTestCase(TestSettingsService))
        suite.addTests(loader.loadTestsFromTestCase(TestUsageService))
        
        print("✅ נטענו בדיקות שירותי LLM")
        
    except ImportError as e:
        print(f"❌ שגיאה בטעינת בדיקות שירותי LLM: {e}")
        return False
    
    # הרצת הבדיקות
    print("\n" + "="*60)
    print("🧪 מתחיל בדיקות LLM")
    print("="*60)
    
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    result = runner.run(suite)
    
    # סיכום תוצאות
    print("\n" + "="*60)
    print("📊 סיכום תוצאות")
    print("="*60)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    successful = total_tests - failures - errors - skipped
    
    print(f"📈 סה\"כ בדיקות: {total_tests}")
    print(f"✅ הצליחו: {successful}")
    print(f"❌ נכשלו: {failures}")
    print(f"💥 שגיאות: {errors}")
    print(f"⏭️ דולגו: {skipped}")
    
    success_rate = (successful / total_tests * 100) if total_tests > 0 else 0
    print(f"📊 אחוז הצלחה: {success_rate:.1f}%")
    
    # הדפסת פרטי כישלונות ושגיאות
    if failures:
        print("\n" + "="*40)
        print("❌ כישלונות:")
        print("="*40)
        for test, traceback in result.failures:
            print(f"\n🔴 {test}")
            print("-" * 40)
            print(traceback)
    
    if errors:
        print("\n" + "="*40)
        print("💥 שגיאות:")
        print("="*40)
        for test, traceback in result.errors:
            print(f"\n🔴 {test}")
            print("-" * 40)
            print(traceback)
    
    # החזרת תוצאה
    success = failures == 0 and errors == 0
    
    if success:
        print(f"\n🎉 כל הבדיקות עברו בהצלחה!")
        return True
    else:
        print(f"\n💔 יש בדיקות שנכשלו או שגיאות")
        return False


def run_specific_test_class(test_class_name):
    """
    מריץ בדיקות עבור מחלקה מסוימת
    
    Args:
        test_class_name (str): שם מחלקת הבדיקה
    """
    
    # מיפוי שמות מחלקות לבדיקות
    test_classes = {
        'LLMProvider': 'tests.models.test_llm_models.TestLLMProvider',
        'LLMModel': 'tests.models.test_llm_models.TestLLMModel',
        'UsageRecord': 'tests.models.test_llm_models.TestUsageRecord',
        'LLMParameters': 'tests.models.test_llm_models.TestLLMParameters',
        'LLMService': 'tests.services.test_llm_service.TestLLMService',
        'SettingsService': 'tests.services.test_settings_service.TestSettingsService',
        'UsageService': 'tests.services.test_usage_service.TestUsageService'
    }
    
    if test_class_name not in test_classes:
        print(f"❌ מחלקת בדיקה לא ידועה: {test_class_name}")
        print(f"מחלקות זמינות: {', '.join(test_classes.keys())}")
        return False
    
    try:
        # טעינת מחלקת הבדיקה
        module_path, class_name = test_classes[test_class_name].rsplit('.', 1)
        module = __import__(module_path, fromlist=[class_name])
        test_class = getattr(module, class_name)
        
        # יצירת test suite
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(test_class)
        
        # הרצת הבדיקות
        print(f"\n🧪 מריץ בדיקות עבור {test_class_name}")
        print("="*50)
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()
        
    except Exception as e:
        print(f"❌ שגיאה בהרצת בדיקות עבור {test_class_name}: {e}")
        return False


if __name__ == "__main__":
    # בדיקת ארגומנטים
    if len(sys.argv) > 1:
        # הרצת בדיקה מסוימת
        test_class = sys.argv[1]
        success = run_specific_test_class(test_class)
    else:
        # הרצת כל הבדיקות
        success = run_llm_tests()
    
    # יציאה עם קוד מתאים
    sys.exit(0 if success else 1)
