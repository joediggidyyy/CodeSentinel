#!/usr/bin/env python3
"""
Test the scroll region canvas fix for GitHub Integration.
"""

import sys
import time
sys.path.append('.')

from tools.codesentinel.gui_setup_wizard import GUISetupWizard

def test_canvas_scroll_fix():
    """Test that canvas scroll region updates correctly."""
    print("🧪 Testing Canvas Scroll Region Fix")
    print("=" * 40)
    
    wizard = GUISetupWizard()
    
    print("1. Navigating to GitHub Integration...")
    wizard.current_step = 6
    wizard.show_step(6)
    
    # Allow time for the delayed canvas update
    wizard.root.update()
    time.sleep(0.02)
    wizard.root.update()
    
    # Check canvas state
    scroll_region = wizard.canvas.cget('scrollregion')
    print(f"   - Canvas scroll region: {scroll_region}")
    
    # Check if content exists
    content_children = len(wizard.content_frame.winfo_children())
    print(f"   - Content frame children: {content_children}")
    
    # Check canvas bbox
    bbox = wizard.canvas.bbox("all")
    print(f"   - Canvas bbox: {bbox}")
    
    if content_children > 0 and bbox and scroll_region != "0 0 0 0":
        print(f"   ✅ Canvas properly configured with content")
        success = True
    else:
        print(f"   ❌ Canvas not properly configured")
        success = False
    
    # Test canvas position
    yview = wizard.canvas.yview()
    print(f"   - Canvas y-view: {yview}")
    
    if yview[0] == 0.0:
        print(f"   ✅ Canvas positioned at top")
    else:
        print(f"   ⚠️  Canvas not at top position")
    
    print(f"\n{'✅ SUCCESS' if success else '❌ ISSUE'}: Canvas scroll fix {'working' if success else 'needs adjustment'}")
    
    wizard.root.destroy()
    return success

if __name__ == "__main__":
    success = test_canvas_scroll_fix()
    exit(0 if success else 1)