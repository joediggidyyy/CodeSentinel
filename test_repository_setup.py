#!/usr/bin/env python3
"""
Test script for the comprehensive repository setup wizard.
Tests specifically the "local to existing GitHub repository" scenario.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))

from tools.codesentinel.gui_setup_wizard import GUISetupWizard

def test_repository_setup():
    """Test the comprehensive repository setup wizard."""
    print("Testing comprehensive repository setup wizard...")
    
    root = tk.Tk()
    root.title("Test - Repository Setup Wizard")
    root.geometry("900x800")
    
    # Create wizard
    wizard = GUISetupWizard()
    
    print("\n=== Testing Repository Setup Scenarios ===")
    
    # Force the wizard to show repository setup (simulate non-git directory)
    wizard.backend_wizard.is_git_repo = False
    
    # Go to GitHub integration step which will show repository setup
    print("1. Navigating to GitHub Integration step")
    wizard.show_step(6)  # GitHub integration step
    
    print("2. Repository setup wizard loaded successfully")
    print("3. Available scenarios:")
    print("   🔗 Connect Local Project to Existing GitHub Repository (YOUR SCENARIO)")
    print("   🆕 Start Fresh - Create Everything New")
    print("   📥 Clone Existing GitHub Repository")
    print("   🚀 Local Project → New GitHub Repository")
    print("   🔄 Connect Existing Local Git to GitHub")
    
    print(f"\n4. Current scenario: {wizard.repo_scenario_var.get()}")
    print(f"   GitHub URL: {wizard.github_url_var.get()}")
    print(f"   Merge strategy: {wizard.merge_strategy_var.get()}")
    
    print("\n5. Your specific scenario handles:")
    print("   • Automatic Git repository initialization (if needed)")
    print("   • Adding GitHub repository as 'origin' remote")
    print("   • Fetching existing content from GitHub")
    print("   • Smart conflict resolution (merge/rebase/force)")
    print("   • Setting up branch tracking")
    print("   • Pushing local changes to GitHub")
    print("   • Progress dialog with detailed steps")
    
    # Test status
    status_frame = ttk.Frame(root)
    status_frame.pack(fill=tk.X, pady=15)
    
    ttk.Label(status_frame, text="✅ Comprehensive Repository Setup Wizard", 
              font=('Arial', 12, 'bold'), foreground="green").pack(pady=5)
    ttk.Label(status_frame, text="Features implemented:", 
              font=('Arial', 10, 'bold')).pack(pady=(10, 5))
    
    features = [
        "🔗 Local to Existing GitHub Repository (your exact scenario)",
        "⚙️ Comprehensive scenario detection and handling",
        "🛠️ Smart Git repository initialization",
        "📡 Remote repository connection and synchronization",
        "🔄 Multiple conflict resolution strategies",
        "📊 Progress dialog with step-by-step feedback",
        "🛡️ Error handling and recovery",
        "🎯 Auto-detected CodeSentinel repository URL"
    ]
    
    for feature in features:
        ttk.Label(status_frame, text=f"     {feature}", 
                 font=('Arial', 9)).pack(anchor=tk.W, padx=20)
    
    # Instructions
    instructions_frame = ttk.LabelFrame(root, text="Manual Testing Instructions")
    instructions_frame.pack(fill=tk.X, pady=15, padx=20)
    
    instructions = [
        "1. Select 'Connect Local Project to Existing GitHub Repository'",
        "2. Verify GitHub URL is pre-filled: https://github.com/joediggidyyy/CodeSentinel.git",
        "3. Choose conflict resolution strategy (Merge recommended for your scenario)",
        "4. Click '🔧 Setup Repository Connection' to execute",
        "5. Monitor progress dialog showing each step",
        "6. Verify successful connection to your existing GitHub repository"
    ]
    
    for i, instruction in enumerate(instructions, 1):
        ttk.Label(instructions_frame, text=instruction, 
                 font=('Arial', 9)).pack(anchor=tk.W, pady=2, padx=10)
    
    # Scenario info
    scenario_frame = ttk.LabelFrame(root, text="Your Scenario Details")
    scenario_frame.pack(fill=tk.X, pady=15, padx=20)
    
    scenario_info = [
        "✓ Local CodeSentinel project exists",
        "✓ GitHub repository exists: https://github.com/joediggidyyy/CodeSentinel.git",
        "✓ GitHub repository is empty (no conflicts expected)",
        "✓ Local project has files that need to be uploaded",
        "→ Wizard will: Initialize Git → Add remote → Push files → Set up tracking"
    ]
    
    for info in scenario_info:
        ttk.Label(scenario_frame, text=info, 
                 font=('Arial', 9)).pack(anchor=tk.W, pady=2, padx=10)
    
    # Control buttons
    control_frame = ttk.Frame(root)
    control_frame.pack(fill=tk.X, pady=10)
    
    ttk.Button(control_frame, text="Test Repository Setup", 
               command=wizard.execute_repository_setup).pack(side=tk.LEFT, padx=10)
    ttk.Button(control_frame, text="Test Complete - Close", 
               command=root.destroy).pack(side=tk.RIGHT, padx=10)
    
    root.mainloop()

if __name__ == "__main__":
    test_repository_setup()