#!/usr/bin/env python3
"""
Test script for validation lock functionality
Tests the logic without running the full GUI
"""

class MockValidationLogic:
    """Mock implementation of validation lock logic for testing"""
    
    def __init__(self):
        self.validations = {
            'email': True,
            'slack': True,
            'github': True
        }
        self.email_enabled = False
        self.slack_enabled = False
        self.github_enabled = False
    
    def on_email_toggle(self, enabled):
        """Simulate email checkbox toggle"""
        self.email_enabled = enabled
        if enabled:
            self.validations['email'] = False
            return "⚠️ Not validated"
        else:
            self.validations['email'] = True
            return ""
    
    def on_slack_toggle(self, enabled):
        """Simulate Slack checkbox toggle"""
        self.slack_enabled = enabled
        if enabled:
            self.validations['slack'] = False
            return "⚠️ Not validated"
        else:
            self.validations['slack'] = True
            return ""
    
    def on_github_toggle(self, enabled):
        """Simulate GitHub checkbox toggle"""
        self.github_enabled = enabled
        if enabled:
            self.validations['github'] = False
            return "⚠️ Not validated"
        else:
            self.validations['github'] = True
            return ""
    
    def check_nav_lock(self, current_step):
        """Check if navigation is locked for current step"""
        if current_step == 2:  # Alerts step
            if self.email_enabled and not self.validations['email']:
                return False, "Email validation required"
            if self.slack_enabled and not self.validations['slack']:
                return False, "Slack validation required"
        elif current_step == 3:  # GitHub step
            if self.github_enabled and not self.validations['github']:
                return False, "GitHub validation required"
        return True, None
    
    def validate_service(self, service, success):
        """Simulate validation attempt"""
        self.validations[service] = success
        return "✓ Valid" if success else "❌ Error"


def test_email_validation():
    """Test email validation logic"""
    print("Testing Email Validation...")
    logic = MockValidationLogic()
    
    # Initial state - not enabled, can navigate
    can_nav, msg = logic.check_nav_lock(2)
    assert can_nav, "Should allow navigation when email disabled"
    
    # Enable email - should require validation
    status = logic.on_email_toggle(True)
    assert status == "⚠️ Not validated", "Should show not validated warning"
    can_nav, msg = logic.check_nav_lock(2)
    assert not can_nav, "Should lock navigation when email enabled but not validated"
    assert "Email" in msg, "Error message should mention email"
    
    # Validate successfully - should unlock
    logic.validate_service('email', True)
    can_nav, msg = logic.check_nav_lock(2)
    assert can_nav, "Should allow navigation after successful validation"
    
    # Disable email - should unlock
    logic.on_email_toggle(False)
    can_nav, msg = logic.check_nav_lock(2)
    assert can_nav, "Should allow navigation when email disabled"
    
    print("✓ Email validation tests passed")


def test_slack_validation():
    """Test Slack validation logic"""
    print("Testing Slack Validation...")
    logic = MockValidationLogic()
    
    # Enable Slack - should require validation
    logic.on_slack_toggle(True)
    can_nav, msg = logic.check_nav_lock(2)
    assert not can_nav, "Should lock navigation when Slack enabled but not validated"
    
    # Validation fails - should remain locked
    logic.validate_service('slack', False)
    can_nav, msg = logic.check_nav_lock(2)
    assert not can_nav, "Should remain locked after failed validation"
    
    # Retry validation successfully - should unlock
    logic.validate_service('slack', True)
    can_nav, msg = logic.check_nav_lock(2)
    assert can_nav, "Should unlock after successful validation"
    
    print("✓ Slack validation tests passed")


def test_github_validation():
    """Test GitHub validation logic"""
    print("Testing GitHub Validation...")
    logic = MockValidationLogic()
    
    # Enable GitHub - should require validation
    logic.on_github_toggle(True)
    can_nav, msg = logic.check_nav_lock(3)
    assert not can_nav, "Should lock navigation when GitHub enabled but not validated"
    assert "GitHub" in msg, "Error message should mention GitHub"
    
    # Validate successfully - should unlock
    logic.validate_service('github', True)
    can_nav, msg = logic.check_nav_lock(3)
    assert can_nav, "Should allow navigation after successful validation"
    
    print("✓ GitHub validation tests passed")


def test_multiple_services():
    """Test multiple services enabled at once"""
    print("Testing Multiple Services...")
    logic = MockValidationLogic()
    
    # Enable both email and Slack
    logic.on_email_toggle(True)
    logic.on_slack_toggle(True)
    
    # Both should block navigation
    can_nav, msg = logic.check_nav_lock(2)
    assert not can_nav, "Should lock when multiple services need validation"
    
    # Validate email only
    logic.validate_service('email', True)
    can_nav, msg = logic.check_nav_lock(2)
    assert not can_nav, "Should remain locked while Slack needs validation"
    
    # Validate Slack too
    logic.validate_service('slack', True)
    can_nav, msg = logic.check_nav_lock(2)
    assert can_nav, "Should unlock when all services validated"
    
    print("✓ Multiple services tests passed")


def test_rapid_toggling():
    """Test rapid checkbox toggling"""
    print("Testing Rapid Toggling...")
    logic = MockValidationLogic()
    
    # Toggle email multiple times
    for i in range(5):
        logic.on_email_toggle(True)
        logic.on_email_toggle(False)
    
    # Should end in disabled state
    can_nav, msg = logic.check_nav_lock(2)
    assert can_nav, "Should allow navigation after even number of toggles"
    
    # Toggle once more
    logic.on_email_toggle(True)
    can_nav, msg = logic.check_nav_lock(2)
    assert not can_nav, "Should lock after odd number of toggles"
    
    print("✓ Rapid toggling tests passed")


def test_state_persistence():
    """Test state persistence through navigation"""
    print("Testing State Persistence...")
    logic = MockValidationLogic()
    
    # Enable and validate email on step 2
    logic.on_email_toggle(True)
    logic.validate_service('email', True)
    
    # Navigate to step 3
    can_nav, msg = logic.check_nav_lock(2)
    assert can_nav, "Should allow navigation from step 2"
    
    # Enable GitHub on step 3
    logic.on_github_toggle(True)
    can_nav, msg = logic.check_nav_lock(3)
    assert not can_nav, "Should lock navigation on step 3"
    
    # Navigate back to step 2 (simulated)
    # Email should still be validated
    can_nav, msg = logic.check_nav_lock(2)
    assert can_nav, "Email validation should persist when navigating back"
    
    # Navigate forward to step 3 again
    # GitHub should still need validation
    can_nav, msg = logic.check_nav_lock(3)
    assert not can_nav, "GitHub validation state should persist"
    
    print("✓ State persistence tests passed")


def run_all_tests():
    """Run all validation lock tests"""
    print("=" * 60)
    print("Validation Lock Logic Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_email_validation,
        test_slack_validation,
        test_github_validation,
        test_multiple_services,
        test_rapid_toggling,
        test_state_persistence
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Test error: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
