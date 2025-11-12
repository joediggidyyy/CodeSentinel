"""
Agent Query Index for CodeSentinel Archive
==========================================

This file provides a structured query reference for agents to efficiently
search and reference historical content in quarantine_legacy_archive/

Format: Each query includes the intent, file pattern, and example usage
"""

ARCHIVE_QUERIES = {
    # Code Archaeology Queries
    "code_archaeology": {
        "find_all_python_scripts": {
            "pattern": "**/*.py",
            "files": [
                "diagnosis.py",
                "fix_syntax.py", 
                "remove_duplicates.py",
                "repository_bloat_audit.py",
                "root_cause_analysis.py"
            ],
            "purpose": "Locate all Python source files for utility analysis",
            "agent_use": "Search for specific function implementations or patterns"
        },
        
        "find_diagnostic_scripts": {
            "pattern": "**/*diagnosis*.py",
            "files": ["diagnosis.py"],
            "purpose": "Find system diagnostic utilities",
            "agent_use": "Analyze diagnostic patterns and health check implementations"
        },
        
        "find_fix_utilities": {
            "pattern": "**/*fix*.py",
            "files": ["fix_syntax.py"],
            "purpose": "Locate code fix and correction utilities",
            "agent_use": "Reference for syntax fixing patterns and error handling"
        },
        
        "find_cleanup_scripts": {
            "pattern": "**/*remove*.py|**/*duplicat*.py",
            "files": ["remove_duplicates.py"],
            "purpose": "Find cleanup and duplication removal utilities",
            "agent_use": "Reference for duplicate detection and removal algorithms"
        },
        
        "find_analysis_scripts": {
            "pattern": "**/*audit*.py|**/*analysis*.py",
            "files": ["repository_bloat_audit.py", "root_cause_analysis.py"],
            "purpose": "Locate analysis and audit utilities",
            "agent_use": "Reference for analysis methodologies and reporting"
        }
    },
    
    # Compliance & Policy Queries
    "compliance": {
        "find_policy_docs": {
            "pattern": "**/*POLICY*.md|**/*VIOLATION*.md",
            "files": ["POLICY_VIOLATION_PREVENTION.md"],
            "purpose": "Policy violation prevention guidelines",
            "agent_use": "Verify compliance requirements and enforcement rules"
        },
        
        "find_assessment_docs": {
            "pattern": "**/*ASSESSMENT*.md|**/*ROOT*.md",
            "files": ["ROOT_DIRECTORY_ASSESSMENT.md"],
            "purpose": "Assessment and evaluation reports",
            "agent_use": "Understand compliance violations and remediation"
        },
        
        "find_organizational_docs": {
            "pattern": "**/*ORGANIZATION*.md|**/*ARCHIVE*.md",
            "files": ["ARCHIVE_ORGANIZATION_POLICY.md"],
            "purpose": "Archive organization and structure guidelines",
            "agent_use": "Reference for content categorization and organization"
        },
        
        "find_all_documentation": {
            "pattern": "**/*.md",
            "count": 13,
            "purpose": "All policy and documentation files",
            "agent_use": "Comprehensive compliance research"
        }
    },
    
    # Configuration & State Queries
    "configuration": {
        "find_requirements": {
            "pattern": "**/*requirements*.txt",
            "files": ["requirements-dev.txt"],
            "purpose": "Find Python dependency specifications",
            "agent_use": "Compare environment configurations and dependency versions"
        },
        
        "find_backups": {
            "pattern": "**/*.bak",
            "count": 8,
            "purpose": "Find backup files from maintenance operations",
            "agent_use": "Compare pre/post-modification states"
        },
        
        "find_config_snapshots": {
            "pattern": "**/*.json|**/*.yaml|**/*.toml",
            "count": 1,
            "purpose": "Find configuration snapshot files",
            "agent_use": "Understand system state at archival time"
        },
        
        "find_temp_files": {
            "pattern": "**/temp_*.txt|**/README_*.md",
            "purpose": "Find temporary backup files",
            "agent_use": "Recover temporary state information"
        }
    },
    
    # Python Module History Queries
    "module_history": {
        "find_all_bytecode": {
            "pattern": "**/*.pyc",
            "count": 3869,
            "purpose": "All compiled Python modules",
            "agent_use": "Trace import history and dependency archaeology"
        },
        
        "find_bytecode_by_module": {
            "pattern": "**/{module_name}*.pyc",
            "example": "find quarantine_legacy_archive -name 'scheduler*.pyc'",
            "purpose": "Find all versions of a specific module",
            "agent_use": "Track module evolution and versions"
        },
        
        "find_recent_bytecode": {
            "pattern": "**/*20251111*.pyc",
            "timestamp_format": "YYYYMMDD_HHMMSS",
            "purpose": "Recent bytecode from latest compilation",
            "agent_use": "Analyze current module import state"
        },
        
        "list_unique_modules": {
            "command": "find quarantine_legacy_archive -name '*.pyc' | sed 's/.*\\///' | sed 's/\\.cpython.*//' | sort -u",
            "purpose": "Extract unique module names",
            "agent_use": "Build inventory of archived modules"
        }
    },
    
    # Quick Reference Queries
    "quick_reference": {
        "list_all_python_files": {
            "command": "find quarantine_legacy_archive -type f -name '*.py' | sort",
            "count_var": "34",
            "use_case": "Get complete inventory of source code"
        },
        
        "list_all_docs": {
            "command": "find quarantine_legacy_archive -type f -name '*.md' | sort",
            "count_var": "13",
            "use_case": "Review all policy and documentation files"
        },
        
        "list_all_configs": {
            "command": "find quarantine_legacy_archive -type f \\( -name '*.txt' -o -name '*.json' -o -name '*.bak' \\) | sort",
            "count_var": "19+",
            "use_case": "Find all configuration and backup files"
        },
        
        "summarize_archive": {
            "command": "echo 'Total files:' && find quarantine_legacy_archive -type f | wc -l && echo 'File types:' && find quarantine_legacy_archive -type f | sed 's/.*\\.//' | sort | uniq -c | sort -rn",
            "use_case": "Get archive overview statistics"
        }
    },
    
    # Complex Analysis Queries
    "analysis": {
        "track_module_versions": {
            "description": "Track different versions of compiled modules",
            "query": "find quarantine_legacy_archive -name '{module}*.pyc' | sed 's/.*\\///' | sort",
            "example": "find quarantine_legacy_archive -name 'scheduler*.pyc' | sed 's/.*\\///' | sort",
            "use": "Identify all archived versions of a specific module"
        },
        
        "extract_import_graph": {
            "description": "Build import dependency graph from bytecode filenames",
            "query": "find quarantine_legacy_archive -name '*.pyc' | sed 's/.*\\///' | sed 's/\\.cpython.*//' | sed 's/_/-/g' | sort | uniq",
            "use": "Understand module dependencies and import chains"
        },
        
        "find_breaking_changes": {
            "description": "Compare old vs new module versions",
            "query": "find quarantine_legacy_archive -name '{old_version}' && find {current_location} -name '{same_module}' && diff",
            "use": "Identify changes between archived and current versions"
        },
        
        "audit_configuration_drift": {
            "description": "Compare archived vs current configuration",
            "query": "diff quarantine_legacy_archive/requirements-dev.txt requirements-dev.txt",
            "use": "Identify environmental changes and dependency updates"
        }
    },
    
    # Recovery Queries
    "recovery": {
        "recover_bytecode_to_source": {
            "description": "Decompile .pyc back to Python source",
            "tool": "uncompyle6 or pycdc",
            "query": "uncompyle6 {file}.pyc > {file}_recovered.py",
            "example": "uncompyle6 quarantine_legacy_archive/scheduler.cpython-314.pyc > scheduler_recovered.py",
            "use": "Recover source code from compiled bytecode"
        },
        
        "recover_configuration": {
            "description": "Restore archived configuration",
            "query": "cat quarantine_legacy_archive/{config_file}.txt",
            "example": "cat quarantine_legacy_archive/requirements-dev.txt",
            "use": "Reconstruct system state from configuration backups"
        },
        
        "recover_policy_rationale": {
            "description": "Find policy documentation explaining compliance decisions",
            "query": "cat quarantine_legacy_archive/{policy_file}.md | grep -i '{keyword}'",
            "example": "cat quarantine_legacy_archive/POLICY_VIOLATION_PREVENTION.md | grep -i 'archive'",
            "use": "Understand the rationale behind current policies"
        }
    }
}

# Metadata for agent reference
ARCHIVE_METADATA = {
    "index_version": "1.0",
    "created_date": "2025-11-11T00:00:00Z",
    "total_queries": len(ARCHIVE_QUERIES),
    "archive_location": "quarantine_legacy_archive/",
    "total_files": 3943,
    "file_breakdown": {
        "bytecode": 3869,
        "python_source": 34,
        "documentation": 13,
        "configuration": 19,
        "other": 8
    }
}

# Agent-friendly query builder
def build_query(query_type, **kwargs):
    """
    Helper function for agents to build archive queries
    
    Example:
        build_query("code_archaeology", category="find_python_scripts")
        build_query("module_history", module_name="scheduler")
    """
    pass

# Query execution guide for agents
EXECUTION_GUIDE = {
    "step_1_identify": "Determine what you're looking for (code, policy, config, modules)",
    "step_2_select_category": "Choose appropriate query category from ARCHIVE_QUERIES",
    "step_3_build_query": "Use query pattern to construct filesystem search",
    "step_4_execute": "Run find/grep command or use build_query() helper",
    "step_5_analyze": "Examine results and reference-correlate with documentation",
    "step_6_recover": "If needed, use recovery queries for decompilation or restoration"
}
