#!/usr/bin/env python3
"""
Debug GitHub Integration page rendering issue.
"""

import sys
sys.path.append('.')

from tools.codesentinel.gui_setup_wizard import GUISetupWizard

def debug_github_rendering():
    """Debug why GitHub Integration page is not rendering."""
    print("🔧 Debugging GitHub Integration Page Rendering")
    print("=" * 55)
    
    wizard = GUISetupWizard()
    
    print(f"1. Initial setup...")
    print(f"   - Backend wizard is_git_repo: {wizard.backend_wizard.is_git_repo}")
    print(f"   - Content frame exists: {hasattr(wizard, 'content_frame')}")
    
    # Navigate to GitHub Integration step
    print(f"\n2. Navigating to GitHub Integration (step 6)...")
    wizard.current_step = 6
    
    try:
        # Try to call show_github_integration directly
        print(f"   - Calling show_github_integration()...")
        wizard.show_github_integration()
        
        # Check what was created
        if hasattr(wizard, 'content_frame'):
            children = wizard.content_frame.winfo_children()
            print(f"   - Content frame children: {len(children)}")
            
            if len(children) > 0:
                first_child = children[0]
                print(f"   - First child type: {type(first_child).__name__}")
                
                # Check if it's a frame with children
                if hasattr(first_child, 'winfo_children'):
                    frame_children = first_child.winfo_children()
                    print(f"   - Frame children: {len(frame_children)}")
                    
                    if len(frame_children) > 0:
                        # Check for the title label
                        for i, child in enumerate(frame_children[:3]):
                            try:
                                if hasattr(child, 'cget'):
                                    text = child.cget('text')
                                    print(f"   - Child {i} text: '{text}'")
                            except:
                                print(f"   - Child {i}: {type(child).__name__} (no text)")
                
                print(f"   ✅ Content appears to be created")
            else:
                print(f"   ❌ No content frame children found")
        else:
            print(f"   ❌ Content frame not found")
            
    except Exception as e:
        print(f"   ❌ Error in show_github_integration: {e}")
        import traceback
        traceback.print_exc()
    
    # Test with show_step method
    print(f"\n3. Testing with show_step method...")
    try:
        wizard.show_step(6)
        
        children_after = len(wizard.content_frame.winfo_children()) if hasattr(wizard, 'content_frame') else 0
        print(f"   - Content frame children after show_step: {children_after}")
        
        if children_after > 0:
            print(f"   ✅ show_step successfully rendered content")
        else:
            print(f"   ❌ show_step did not render content")
            
    except Exception as e:
        print(f"   ❌ Error in show_step: {e}")
        import traceback
        traceback.print_exc()
    
    wizard.root.destroy()

if __name__ == "__main__":
    debug_github_rendering()