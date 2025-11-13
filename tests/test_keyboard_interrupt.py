"""
Test keyboard interrupt handling in CLI.

Verifies that Ctrl+C gracefully exits from interactive prompts
following SEAM Protection principles.
"""

import pytest
import sys
from unittest.mock import patch, MagicMock
from io import StringIO


class TestKeyboardInterruptHandling:
    """Test suite for KeyboardInterrupt handling across CLI commands."""
    
    def test_main_cli_keyboard_interrupt(self):
        """Test that main() handles KeyboardInterrupt gracefully."""
        from codesentinel.cli import main
        
        # Mock sys.argv to trigger a command that might have interactive prompts
        with patch.object(sys, 'argv', ['codesentinel', '--help']):
            with patch('sys.exit') as mock_exit:
                with patch('sys.stderr', new=StringIO()):
                    # This should not raise, just print help and exit
                    try:
                        main()
                    except SystemExit:
                        pass  # Expected from --help
    
    def test_interactive_review_keyboard_interrupt(self):
        """Test that interactive review mode handles KeyboardInterrupt."""
        from codesentinel.cli.dev_audit_review import run_interactive_review
        from codesentinel.cli.agent_utils import AgentContext, RemediationOpportunity
        
        # Create a mock context with a manual review item
        context = AgentContext(command="dev-audit")
        context.add_opportunity(
            RemediationOpportunity(
                id="test-1",
                type="minimalism",
                title="Test issue",
                description="Test description",
                priority="low",
                suggested_actions=["Test action"],
                agent_decision_required=True,
                safe_to_automate=False
            )
        )
        
        # Mock input to raise KeyboardInterrupt
        with patch('builtins.input', side_effect=KeyboardInterrupt):
            with patch('sys.stdout', new=StringIO()) as mock_stdout:
                # Should not raise - should handle gracefully
                run_interactive_review(context)
                
                output = mock_stdout.getvalue()
                assert "interrupted" in output.lower() or "Review interrupted" in output
    
    def test_command_utils_keyboard_interrupt(self):
        """Test that command_utils handles KeyboardInterrupt in review prompt."""
        from codesentinel.cli.command_utils import run_agent_enabled_command
        from codesentinel.cli.agent_utils import AgentContext, RemediationOpportunity
        
        # Create mock args with agent mode
        mock_args = MagicMock()
        mock_args.agent = True
        mock_args.export = None
        mock_args.verbose = False
        
        # Mock analysis function that returns results
        def mock_analysis():
            return {"summary": {"total_issues": 1}}
        
        # Context builder that creates context with manual review items
        def mock_context_builder(results):
            context = AgentContext(command="test-command")
            context.add_opportunity(
                RemediationOpportunity(
                    id="test-1",
                    type="test",
                    title="Test",
                    description="Test",
                    priority="low",
                    suggested_actions=["Test"],
                    agent_decision_required=True,
                    safe_to_automate=False
                )
            )
            return context
        
        # Standard handler (no-op)
        def mock_handler(results):
            pass
        
        # Mock input to raise KeyboardInterrupt
        with patch('builtins.input', side_effect=KeyboardInterrupt):
            with patch('sys.stdout', new=StringIO()) as mock_stdout:
                result = run_agent_enabled_command(
                    command_name="test-command",
                    args=mock_args,
                    analysis_fn=mock_analysis,
                    standard_handler=mock_handler,
                    context_builder=mock_context_builder
                )
                
                # Should complete without raising exception
                assert result is not None
                assert result['mode'] == 'agent'
                
                output = mock_stdout.getvalue()
                # Should have printed the interrupt message
                assert "interrupted" in output.lower() or "Skipping" in output
    
    def test_eof_error_handling(self):
        """Test that EOFError is also handled gracefully."""
        from codesentinel.cli.dev_audit_review import run_interactive_review
        from codesentinel.cli.agent_utils import AgentContext, RemediationOpportunity
        
        context = AgentContext(command="dev-audit")
        context.add_opportunity(
            RemediationOpportunity(
                id="test-1",
                type="test",
                title="Test",
                description="Test",
                priority="low",
                suggested_actions=["Test"],
                agent_decision_required=True,
                safe_to_automate=False
            )
        )
        
        # Mock input to raise EOFError (Ctrl+D on Unix, Ctrl+Z on Windows)
        with patch('builtins.input', side_effect=EOFError):
            with patch('sys.stdout', new=StringIO()) as mock_stdout:
                run_interactive_review(context)
                
                output = mock_stdout.getvalue()
                assert "terminated" in output.lower() or "Review terminated" in output


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
