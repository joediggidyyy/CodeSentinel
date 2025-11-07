# Documentation Operations Agent Instructions

**Classification**: T4b - Infrastructure & Procedural Agent Documentation  
**Scope**: Documentation creation, modification, archival, and classification in docs/ directory  
**Target Users**: Agents creating and managing CodeSentinel documentation  
**Last Updated**: November 7, 2025  
**Version**: 1.0

---

## Quick Authority Reference

**Who can create, modify, delete documentation?**

| Operation | Authority | Requires Approval |
|-----------|-----------|-------------------|
| Create Tier 2 doc | Agent | No |
| Create Tier 1 doc | Agent | Yes (user verification) |
| Modify Tier 2 doc | Agent | No (minor), Yes (major) |
| Modify Tier 1 doc | Agent | Yes (major only) |
| Delete Tier 2 doc | Agent | Yes (user approval) |
| Delete Tier 1 doc | Agent | Yes (explicit user instruction) |
| Archive document | Agent | Yes (verification) |
| Update README | Agent | No (minor), Yes (major) |
| Create guide/tutorial | Agent | No |
| Update CHANGELOG | Agent | No |

**Reference**: See `docs/architecture/DOCUMENT_CLASSIFICATION.md` - Authority matrices by tier

---

## Domain Overview

The `docs/` directory contains CodeSentinel documentation including:

- **Architecture Docs** (`docs/architecture/`) - Policy, classification, strategy
- **Feature Docs** (`docs/features/`) - Feature descriptions and specifications
- **Reports** (`docs/reports/`) - Audit reports and compliance documents
- **Guides** (`docs/guides/`) - User guides and tutorials
- **API Documentation** - Generated and manual API docs
- **README Files** - High-level project information

**Key Principles for This Domain**:

- Clear and professional writing
- Non-destructive archival before deletion
- Proper tier classification for all documents
- Metadata tracking for all archived docs
- UTF-8 encoding, no corrupted characters
- Version tracking for critical documents

---

## Common Procedures

### Procedure 1: Create New Informative Document (Tier 2)

**When**: User needs guidance, tutorial, or informational content

**Steps**:

1. **Verify Scope**: Clarify what the document will cover ✅

2. **Choose Location**:
   - Guides: `docs/guides/[topic]/`
   - Features: `docs/features/[feature_name].md`
   - API: `docs/api/[module_name].md`
   - Procedures: `docs/procedures/[procedure_name].md`
   - Other: Root `docs/` with clear naming

3. **Plan Structure**:
   - Title and purpose (first section)
   - Quick reference (if applicable)
   - Main content (body sections)
   - Examples or use cases
   - Related documentation links
   - References section

4. **Write Document**:
   - Clear and professional language
   - Code examples with syntax highlighting
   - Consistent heading hierarchy
   - Proper markdown formatting
   - Links to related documentation
   - No hardcoded paths or credentials

5. **Apply Professional Standards**:
   - UTF-8 encoding (no BOM)
   - Consistent emoji usage (only when clarifying)
   - Professional branding (subtle, not overwhelming)
   - Consistent formatting with existing docs
   - No commented-out sections

6. **Add Metadata** (if Tier 1):
   - Metadata already applied for archival
   - Not needed for new Tier 2 docs

7. **Validation**:
   - Document is clear and complete ✅
   - Links to related docs work ✅
   - Code examples are correct ✅
   - No formatting issues ✅
   - Professional standards met ✅

8. **Commit**:
   - Message: `docs: add [document name] guide/documentation`
   - Include the new document
   - Include any related updates (index, README)

---

### Procedure 2: Create Infrastructure/Policy Document (Tier 1)

**When**: New policy, procedure, or critical infrastructure document needed

**Steps**:

1. **Verify Authority**: Get user approval before creating Tier 1 docs ✅

2. **Choose Location**:
   - Policies: `docs/architecture/POLICY.md` or new policy file
   - Infrastructure: `docs/architecture/[system].md`
   - Reports: `docs/reports/[report_name]_[DATE].md`
   - Critical: Usually in `docs/architecture/`

3. **Plan Document**:
   - Clear title and purpose
   - Version number
   - Effective date
   - Classification (should be T1)
   - Authority statement
   - Table of contents for long docs

4. **Write Document**:
   - Comprehensive and authoritative
   - Clear decision frameworks
   - Authority matrices if applicable
   - Implementation procedures
   - Compliance requirements
   - Examples and case studies

5. **Create Metadata**:
   - File: `docs/architecture/metadata.json` (if not existing)
   - Include document metadata:
     - Title, version, date
     - Classification tier
     - Authority and approval
     - Related documents
     - Retention policy

6. **Archive Setup**:
   - New Tier 1 docs should have archival plan
   - Version tracking folder structure planned
   - Metadata file created
   - Backup location configured

7. **Validation**:
   - Document is complete and authoritative ✅
   - Classification tier is correct (T1) ✅
   - Metadata is accurate ✅
   - Links to related docs verified ✅
   - Authority statement clear ✅

8. **Commit**:
   - Message: `docs(T1): add [document name] - [purpose]`
   - Include document and metadata
   - Include any related updates
   - Note version 1.0 in message

---

### Procedure 3: Update Existing Documentation

**When**: Docs need correction, clarification, or minor updates

**Steps**:

1. **Determine Update Type**:
   - Correction (fix typo/error)? → Minor update
   - Clarification (better explanation)? → Minor/medium update
   - New section (new information)? → Medium update
   - Structural change (reorganize)? → Major update
   - Policy change (affects behavior)? → Major update (Tier 1 needs approval)

2. **For Minor Updates**:
   - Fix the content directly
   - Keep document classification same
   - Update "Last Updated" date
   - Test any code examples
   - Commit with descriptive message

3. **For Medium Updates**:
   - Plan changes carefully
   - Update structure if needed
   - Add new sections with clear heading hierarchy
   - Verify all links still work
   - Update table of contents if present
   - Update "Last Updated" date
   - Commit with detailed message

4. **For Major Updates** (Tier 1 docs):
   - Get user verification for major changes ✅
   - Consider if this warrants new version
   - Create v2 directory in archive if new version
   - Update version number
   - Document what changed in "Version History"
   - Add old version to archive
   - Update "Last Updated" date

5. **Validation**:
   - All links verified ✅
   - Code examples tested ✅
   - No formatting broken ✅
   - Professional standards maintained ✅
   - If Tier 1: Change documented in history ✅

6. **Commit**:
   - Message: `docs: [update description]`
   - Include clear description of changes
   - For Tier 1: Include version change notes

---

### Procedure 4: Archive and Delete Old Documentation

**When**: Document no longer needed or replaced by newer version

**Steps**:

1. **Verify Deletion Authority**: Check if user approval needed ✅
   - Tier 1 docs: YES (explicit instruction required)
   - Tier 2 docs: YES (user approval)
   - Tier 3 docs: NO (agent discretion)

2. **Check Dependencies**:
   - What other docs link to this?
   - What code depends on this?
   - Are there references to this doc?
   - Update references before deleting

3. **Prepare for Archival**:
   - Create archive location: `archive/active/[tier]/[doc_type]/[doc_name]/v1/`
   - Copy document to archive
   - Create metadata.json with archival info
   - Include timestamp and reason for archival

4. **Create Archive Metadata**:

   ```json
   {
     "classification_tier": 2,
     "original_path": "docs/old_guide.md",
     "archived_date": "2025-11-07T14:30:00Z",
     "archived_reason": "Replaced by new guide",
     "related_documents": ["docs/guides/new_guide.md"],
     "retention_policy": "indefinite",
     "last_accessed": "2025-11-05"
   }
   ```

5. **Delete Original**:
   - Remove from main docs/ directory
   - Update any indices or navigation
   - Update README if document was listed
   - Update any cross-references

6. **Update Documentation**:
   - Note where old document was moved to
   - Add pointer to replacement if applicable
   - Update related documents lists
   - Add note to CHANGELOG.md if relevant

7. **Validation**:
   - Archive copy complete ✅
   - Metadata accurate ✅
   - Original removed from main location ✅
   - All references updated ✅
   - Replacement document (if any) available ✅

8. **Commit**:
   - Message: `docs: archive [document name]`
   - Include deletion and archive creation
   - Note reason for archival

---

## Quick Document Classification Decision Tree

**Is this a policy, compliance, or infrastructure document?**

- If YES → Tier 1 (Critical Infrastructure)
- If NO → Continue

**Is this a user guide, tutorial, or informational content?**

- If YES → Tier 2 (Informative Documentation)
- If NO → Continue

**Is this a temporary report or audit output?**

- If YES → Tier 3 (Temporary & Job Reports)
- If NO → Continue

**Is this guidance for agent operations?**

- If YES → Tier 4 (Agent Documentation)
- If NO → This shouldn't be in docs/

**Tier 1 Characteristics** (if unsure):

- Permanent storage needed? YES
- Multiple versions tracked? YES
- User approval required for changes? YES
- Never deleted without explicit instruction? YES

**Tier 2 Characteristics**:

- Permanent storage needed? YES
- Multiple versions tracked? NO (usually)
- User approval required for major changes? YES
- Agent can create freely? YES

---

## Quick Reference: Before Creating Any Document

**Checklist**:

- [ ] **Tier Determined**: Know if Tier 1, 2, 3, or 4
- [ ] **Location Planned**: Know where document will live
- [ ] **Approval Needed**: Confirmed authority (Tier 1 docs need approval)
- [ ] **Structure Clear**: Have outline/plan before writing
- [ ] **Professional Standards**: Will follow formatting and emoji guidelines
- [ ] **UTF-8 Encoding**: Save as UTF-8 (no BOM)
- [ ] **Links Verified**: All documentation links will work
- [ ] **Code Examples**: Any examples will be tested/correct
- [ ] **Metadata Ready**: For Tier 1, metadata will be created
- [ ] **Archive Plan**: For Tier 1, understand archival strategy

---

## Validation Checklist (Before Commit)

**Content Quality**:

- [ ] Document has clear title and purpose
- [ ] Heading hierarchy is logical (H1 → H2 → H3, etc.)
- [ ] Sections are well-organized
- [ ] Code examples are correct and tested
- [ ] Links to other docs work
- [ ] No hardcoded paths or credentials
- [ ] Professional language throughout

**Formatting**:

- [ ] UTF-8 encoding (verified)
- [ ] Consistent bullet formatting
- [ ] Code blocks have language specified
- [ ] No trailing spaces or extra blank lines
- [ ] Markdown is clean and valid
- [ ] Tables (if any) are properly formatted

**Standards Compliance**:

- [ ] Professional branding applied (if Tier 1/2)
- [ ] Emoji usage follows policy (only when clarifying)
- [ ] Consistent with existing documentation style
- [ ] Character encoding clean (no corrupted text)
- [ ] No excessive decoration

**Classification & Metadata**:

- [ ] Tier classification is correct
- [ ] Metadata.json created (if Tier 1)
- [ ] Version number assigned (if Tier 1)
- [ ] Date field added (if Tier 1)
- [ ] Authority statement clear (if Tier 1)

**References & Links**:

- [ ] Links to related documentation included
- [ ] References section complete (if applicable)
- [ ] Cross-references accurate
- [ ] No broken internal links

**Compliance**:

- [ ] Document preserves existing features
- [ ] Non-destructive approach maintained
- [ ] Archive procedures followed (if deleting)
- [ ] Metadata properly tracked
- [ ] Audit trail noted

---

## Common Documentation Questions

### Q: What's the difference between a guide and a procedure?

**A**:

- **Guide**: Educational content explaining concepts, with examples. Tier 2.
- **Procedure**: Step-by-step instructions for how to do something. Can be Tier 1 (infrastructure) or Tier 2 (user procedure).

### Q: Should I update the main README or create a separate guide?

**A**:

- Update README for major, commonly-needed information
- Create separate guide for detailed, specialized content
- Link from README to guides for discoverability

### Q: How do I handle documentation that depends on code?

**A**:

- Code examples must match current code
- Document code as it is, not as it should be
- If code changes, update documentation
- Consider creating automated tests for code examples

### Q: Can I delete documentation that's "outdated"?

**A**: No. Follow archival procedure:

1. Archive to inactive location with metadata
2. Keep all historical versions
3. Only delete with explicit user approval
4. Document why it was archived

### Q: How do I handle version history in documentation?

**A**: Add section to document:

```markdown
## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.1 | Nov 15 | Agent | Added new section |
| 1.0 | Nov 7 | Agent | Initial version |
```

---

## File Organization Reference

```
docs/
├── architecture/          # Tier 1: Policies, classification, strategy
│   ├── POLICY.md
│   ├── DOCUMENT_CLASSIFICATION.md
│   └── AGENT_INSTRUCTION_STRATEGY.md
│
├── guides/               # Tier 2: User guides and tutorials
│   ├── getting_started.md
│   ├── installation.md
│   └── [topic]/
│
├── api/                  # Tier 2: API documentation
│   ├── cli.md
│   ├── core.md
│   └── utils.md
│
├── features/             # Tier 2: Feature descriptions
│   └── [feature_name].md
│
├── procedures/           # Tier 1: Infrastructure procedures
│   ├── deployment.md
│   └── maintenance.md
│
├── reports/              # Tier 1: Audit and compliance reports
│   └── [audit_name]_[DATE].md
│
└── README.md            # High-level overview (Tier 2)
```

---

## References & Links

**Core Documentation**:

- Global Policy: `docs/architecture/POLICY.md`
- Classification Framework: `docs/architecture/DOCUMENT_CLASSIFICATION.md`
- General Strategy: `docs/architecture/AGENT_INSTRUCTION_STRATEGY.md`

**Documentation Standards**:

- Professional Standards: In `docs/architecture/POLICY.md`
- Emoji Policy: In `docs/architecture/POLICY.md`
- Archive Strategy: In `docs/architecture/DOCUMENT_CLASSIFICATION.md`

**Related Documents**:

- Satellite Archive Instructions: `archive/AGENT_INSTRUCTIONS.md`
- Testing Instructions: `tests/AGENT_INSTRUCTIONS.md`
- Core Package Instructions: `codesentinel/AGENT_INSTRUCTIONS.md`

---

**Classification**: T4b - Infrastructure & Procedural Agent Documentation  
**Authority**: Guidelines for agents creating and managing documentation  
**Update Frequency**: When documentation procedures or policies change  
**Last Updated**: November 7, 2025  
**Next Review**: December 7, 2025 (quarterly satellite audit)
