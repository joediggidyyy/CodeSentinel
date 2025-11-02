#!/usr/bin/env python3
"""
Test GitHub integration page rendering with navigation fixes.
"""

import sys
sys.path.append('.')

from tools.codesentinel.gui_setup_wizard import GUISetupWizard

def test_github_page_rendering():
    """Test that GitHub integration page renders correctly."""
    print("🧪 Testing GitHub Integration Page Rendering")
    print("=" * 50)
    
    wizard = GUISetupWizard()
    
    # Test forward navigation to GitHub step
    print("1. Navigating forward to GitHub Integration (step 6)...")
    wizard.current_step = 6
    wizard.show_step(6)
    
    # Check if content was created
    content_widgets = wizard.content_frame.winfo_children()
    print(f"   - Content widgets created: {len(content_widgets)}")
    
    if len(content_widgets) > 0:
        # Look for the main frame
        main_frame = content_widgets[0]
        frame_widgets = main_frame.winfo_children() if hasattr(main_frame, 'winfo_children') else []
        print(f"   - Frame widgets created: {len(frame_widgets)}")
        
        # Check for the title label
        if len(frame_widgets) > 0:
            first_widget = frame_widgets[0]
            if hasattr(first_widget, 'cget'):
                try:
                    text = first_widget.cget('text')
                    if "GitHub Integration" in text:
                        print(f"   ✅ Title found: '{text}'")
                        page_rendered = True
                    else:
                        print(f"   ❌ Unexpected title: '{text}'")
                        page_rendered = False
                except:
                    print(f"   ❌ Could not get widget text")
                    page_rendered = False
            else:
                print(f"   ❌ First widget is not a label")
                page_rendered = False
        else:
            print(f"   ❌ No frame widgets found")
            page_rendered = False
    else:
        print(f"   ❌ No content widgets found")
        page_rendered = False
    
    # Test backward navigation and return
    print(f"\n2. Testing back navigation...")
    wizard.current_step = 5
    wizard.show_step(5)
    
    print(f"3. Returning to GitHub Integration...")
    wizard.current_step = 6
    wizard.show_step(6)
    
    # Check again after back navigation
    content_widgets_after = wizard.content_frame.winfo_children()
    print(f"   - Content widgets after back navigation: {len(content_widgets_after)}")
    
    if len(content_widgets_after) > 0:
        print(f"   ✅ Page renders correctly after back navigation")
        back_nav_works = True
    else:
        print(f"   ❌ Page does not render after back navigation")
        back_nav_works = False
    
    # Test result
    if page_rendered and back_nav_works:
        print(f"\n✅ SUCCESS: GitHub Integration page renders correctly in all scenarios")
        result = True
    else:
        print(f"\n❌ ISSUE: Page rendering problems detected")
        print(f"   Initial render: {'✅' if page_rendered else '❌'}")
        print(f"   Back navigation: {'✅' if back_nav_works else '❌'}")
        result = False
    
    wizard.root.destroy()
    return result

if __name__ == "__main__":
    success = test_github_page_rendering()
    exit(0 if success else 1)