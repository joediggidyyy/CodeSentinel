# Archive Management Agent Instructions

**Classification**: T4b - Infrastructure & Procedural Agent Documentation  
**Scope**: Archive operations, document archival, version management, and backup procedures  
**Target Users**: Agents managing archived documents and versions  
**Last Updated**: November 7, 2025  
**Version**: 1.0

---

## Quick Authority Reference

**Who can create, modify, delete in archive operations?**

| Operation | Authority | Requires Approval |
|-----------|-----------|-------------------|
| Archive document | Agent | Yes (verification) |
| Create archive directory | Agent | No |
| Archive Tier 1 doc | Agent | Yes (user verification) |
| Archive Tier 2 doc | Agent | Yes (user approval) |
| Archive Tier 3 doc | Agent | No |
| Create version directory | Agent | No |
| Move doc to inactive | Agent | Yes (verification) |
| Delete from archive | Agent | Yes (explicit user instruction) |
| Update metadata.json | Agent | No (minor), Yes (major) |
| Backup archive | Agent | No |

**Reference**: See `docs/architecture/DOCUMENT_CLASSIFICATION.md` - Archive strategy and Tier-specific authority

---

## Domain Overview

The archive system manages CodeSentinel's document lifecycle including:

- **Active Archive** - Current versions of documents being preserved
- **Inactive Archive** - Old versions and superseded documents
- **Metadata Tracking** - JSON files tracking document history
- **Backup Location** - Copies in parent directory for disaster recovery
- **Version Management** - Multiple versions of same document tracked

**Key Principles for This Domain**:

- Non-destructive operations (no permanent deletion without archive)
- Complete audit trail (all archival actions tracked)
- Version history preservation (all versions retained)
- Metadata completeness (every document has metadata)
- Backup redundancy (copies in safe location)
- Tier-based procedures (different tiers archive differently)

---

## Common Procedures

### Procedure 1: Archive an Active Document (Move to Inactive)

**When**: Document no longer needed or replaced by newer version

**Steps**:

1. **Verify Authority**: Check if user approval needed ✅
   - Tier 1 docs: YES (explicit instruction required)
   - Tier 2 docs: YES (user approval)
   - Tier 3 docs: NO (agent discretion)

2. **Check Dependencies**:
   - What other docs link to this?
   - What code references this?
   - Update all references before archiving
   - Document dependencies in metadata

3. **Create Archive Path**:
   - Path: `archive/inactive/[tier]/[doc_type]/[doc_name]/`
   - Create directory structure if not exists
   - Ensure parent directories exist
   - Verify permissions are correct

4. **Copy Document to Archive**:
   - Copy from current location to archive path
   - Preserve filename and content exactly
   - Verify copy is complete and correct
   - Do NOT delete original yet

5. **Create/Update Metadata**:

   ```json
   {
     "classification_tier": 2,
     "document_name": "Example Document",
     "original_path": "docs/example.md",
     "archived_date": "2025-11-07T14:30:00Z",
     "archived_reason": "Replaced by new version",
     "archived_by": "agent",
     "related_documents": ["docs/new_example.md"],
     "retention_policy": "indefinite",
     "last_accessed": "2025-11-05",
     "versions": ["v1"]
   }
   ```

6. **Delete Original** (if appropriate):
   - Only delete after archive verified complete
   - Update any indices or navigation
   - Update cross-references if needed
   - Add note to CHANGELOG.md

7. **Verification**:
   - Archive copy exists and is correct ✅
   - Metadata file created ✅
   - Original location updated ✅
   - All references updated ✅
   - Backup location includes archive ✅

8. **Commit**:
   - Message: `archive: move [document name] to inactive`
   - Include metadata creation
   - Note reason for archival

---

### Procedure 2: Create New Version of Document

**When**: Document updated significantly and old version should be preserved

**Steps**:

1. **Verify Current Archive Status**:
   - Is document already archived? Check archive/active/
   - Does version directory exist? Look for v1/, v2/, etc.
   - Get current version number

2. **Determine New Version Number**:
   - Increment version: v1 → v2, v2 → v3, etc.
   - Alternative: Use dates if tracking by date
   - Document versioning strategy chosen
   - Update metadata to reflect versioning scheme

3. **Archive Current Version**:
   - Path: `archive/active/[tier]/[doc_type]/[doc_name]/v[old_number]/`
   - Copy current document to old version directory
   - Create metadata for old version if not exists
   - Preserve exact copy of previous version

4. **Create New Version Directory**:
   - Path: `archive/active/[tier]/[doc_type]/[doc_name]/v[new_number]/`
   - Create directory structure
   - Place new document in new version directory
   - Update main repo with new version

5. **Update Metadata**:

   ```json
   {
     "classification_tier": 1,
     "document_name": "Example Policy",
     "current_version": "v2",
     "versions_tracked": true,
     "archive_location": "archive/active/tier1_critical/policy/",
     "version_history": [
       {
         "version": "v1",
         "date": "2025-11-07T00:00:00Z",
         "description": "Initial version"
       },
       {
         "version": "v2",
         "date": "2025-11-15T10:00:00Z",
         "description": "Updated procedures"
       }
     ],
     "retention_policy": "permanent"
   }
   ```

6. **Update Documentation**:
   - Note version change in document header
   - Add to "Version History" section
   - Update related documents if needed
   - Note what changed from v1 to v2

7. **Verification**:
   - Old version archived correctly ✅
   - New version directory created ✅
   - Metadata tracks both versions ✅
   - Main repo updated to new version ✅
   - Version history documented ✅

8. **Commit**:
   - Message: `archive: version [doc_name] from v1 to v2`
   - Include both archive and main repo changes
   - Document what changed

---

### Procedure 3: Backup Archive Directory

**When**: Regularly (daily or weekly) to ensure disaster recovery capability

**Steps**:

1. **Identify Backup Location**:
   - Path: `{repository_parent_directory}/archive_backup/`
   - Ensure location exists and is accessible
   - Verify permissions allow backup

2. **Backup Strategy**:
   - Full backup: Copy entire archive/ directory
   - Incremental: Only copy changed files
   - Frequency: Daily or per policy
   - Retention: Keep recent backups

3. **Perform Backup**:
   - Copy: `cp -r archive/ ../archive_backup/`
   - Verify all files copied correctly
   - Check file counts match
   - Verify backup is readable

4. **Create Backup Manifest**:

   ```json
   {
     "backup_date": "2025-11-07T20:00:00Z",
     "backup_location": "../archive_backup/",
     "source": "archive/",
     "file_count": 245,
     "total_size_mb": 125,
     "backup_type": "full",
     "verification": "ok",
     "next_backup": "2025-11-08T20:00:00Z"
   }
   ```

5. **Verification**:
   - File count matches ✅
   - Archive is readable ✅
   - Manifest created ✅
   - Backup location is safe ✅
   - Recent backup exists ✅

6. **Update Backup Index**:
   - Update `archive/metadata/backup_manifest.json`
   - Log backup completion
   - Document any issues
   - Schedule next backup

7. **Testing** (Periodic):
   - Test restore from backup quarterly
   - Verify backup integrity
   - Document restore procedure
   - Ensure backup is usable

---

### Procedure 4: Restore Document from Archive

**When**: Need to recover previous version or accidentally deleted document

**Steps**:

1. **Locate Document in Archive**:
   - Search `archive/active/` for current versions
   - Search `archive/inactive/` for old versions
   - Check metadata.json for location info
   - Use `archive_index.json` for quick lookup

2. **Verify Archive Completeness**:
   - Document exists in archive? ✅
   - Metadata accurate? ✅
   - File not corrupted? ✅
   - Correct version? ✅

3. **Copy Document from Archive**:
   - Copy from archive location to restore destination
   - Preserve filename and content
   - Verify copy is complete
   - Do NOT modify restored document yet

4. **Update Metadata**:
   - Add "restored_date" field
   - Add "restored_by" field
   - Note "restored_reason"
   - Track recovery event

5. **Verify Restored Document**:
   - Document content correct ✅
   - File format intact ✅
   - All references still valid ✅
   - Restored to correct location ✅

6. **Documentation**:
   - Log restoration event
   - Document why restoration was needed
   - Update related documentation
   - Note any manual fixes needed

7. **Testing** (if restored to production):
   - Verify restored content works
   - Update references if needed
   - Test any dependent code/docs
   - Confirm restoration successful

---

## Quick Archive Decision Tree

**What are you doing with a document?**

- Replacing with newer version? → Use "Create New Version" procedure
- Marking as obsolete? → Use "Archive Document" procedure
- Recovering from backup? → Use "Restore Document" procedure
- Regular maintenance backup? → Use "Backup Archive" procedure
- Checking archive status? → Check `archive_index.json` or metadata.json

**What tier is the document?**

- Tier 1 (Critical)? → Archive all versions, track permanently
- Tier 2 (Informative)? → Archive when obsolete, track history
- Tier 3 (Temporary)? → May delete after archiving (optional)
- Tier 4 (Agent)? → 4a/4b archive permanently, 4c delete when done

**Is user approval needed?**

- Archiving Tier 1? → YES (explicit instruction)
- Archiving Tier 2? → YES (user approval)
- Archiving Tier 3? → NO (agent discretion)
- Archiving Tier 4a/b? → YES (verification)
- Archiving Tier 4c? → NO (agent discretion)

---

## Archive Structure Reference

```
archive/
├── active/
│   ├── tier1_critical/
│   │   ├── policy/
│   │   │   └── POLICY/
│   │   │       ├── v1/
│   │   │       ├── v2/
│   │   │       └── metadata.json
│   │   ├── reports/
│   │   └── compliance/
│   │
│   ├── tier2_informative/
│   │   ├── guides/
│   │   ├── api/
│   │   └── features/
│   │
│   ├── tier3_temporary/
│   │   └── job_reports/
│   │
│   └── tier4_agent/
│       ├── 4a_core/
│       ├── 4b_infrastructure/
│       └── 4c_temporary/
│
├── inactive/
│   ├── tier1_critical/
│   ├── tier2_informative/
│   ├── tier3_temporary/
│   └── tier4_agent/
│
└── metadata/
    ├── archive_index.json
    ├── classification_audit.log
    └── backup_manifest.json
```

---

## Validation Checklist (Before Archive Operations)

**Authority & Approval**:

- [ ] Approval verified (if needed for tier)
- [ ] User instruction documented (if Tier 1)
- [ ] Authority matrix checked
- [ ] Compliance confirmed

**Archive Preparation**:

- [ ] Archive location exists or will be created
- [ ] Metadata template ready
- [ ] Current version documented
- [ ] Dependencies identified

**Document Integrity**:

- [ ] Document complete and uncorrupted
- [ ] Filename and path correct
- [ ] Content verified as accurate
- [ ] Links and references checked

**Metadata Quality**:

- [ ] All required fields populated
- [ ] Dates and times accurate
- [ ] Reason for archival clear
- [ ] Related documents linked

**Backup Verification**:

- [ ] Archive will be backed up
- [ ] Backup location accessible
- [ ] Backup schedule maintained
- [ ] Disaster recovery possible

**Documentation**:

- [ ] CHANGELOG updated (if applicable)
- [ ] References updated
- [ ] Metadata tracked
- [ ] Audit trail recorded

---

## Common Archive Questions

### Q: How long do archived documents stay in archive/?

**A**: Per tier:

- Tier 1: Permanent (never deleted)
- Tier 2: Indefinite (years)
- Tier 3: As-useful (may be deleted after 6-12 months)
- Tier 4a/b: Permanent (never deleted)
- Tier 4c: Optional (delete when no longer needed)

### Q: Can I restore a document from archive?

**A**: Yes:

1. Locate in archive/ (active or inactive)
2. Verify metadata for completeness
3. Copy to restore destination
4. Update metadata with restore info
5. Document why restoration was needed
6. Update any affected code/docs

### Q: What if archive gets corrupted?

**A**: Recovery procedure:

1. Check backup location (`../archive_backup/`)
2. Restore from most recent backup
3. Document corruption and recovery
4. Verify all files after restore
5. Report incident
6. Consider additional backups

### Q: Should I version every change?

**A**: No:

- Minor updates: Update in place (no new version)
- Major changes: Create new version
- Tier 1 docs: Usually version (major changes)
- Tier 2 docs: Version if major restructure
- Tier 3 docs: Usually don't version (temporary)

### Q: How do I find old versions?

**A**: Three ways:

1. Check `archive_index.json` for document locations
2. Look in `archive/active/[tier]/[type]/[name]/vX/`
3. Check metadata.json for version history

---

## References & Links

**Core Documentation**:

- Global Policy: `docs/architecture/POLICY.md`
- Classification Framework: `docs/architecture/DOCUMENT_CLASSIFICATION.md`
- Archive Strategy: In DOCUMENT_CLASSIFICATION.md - Archive Organization Structure
- General Strategy: `docs/architecture/AGENT_INSTRUCTION_STRATEGY.md`

**Related Satellites**:

- Documentation Operations: `docs/AGENT_INSTRUCTIONS.md`
- Core Package Operations: `codesentinel/AGENT_INSTRUCTIONS.md`

**Archive Locations**:

- Active Archive: `archive/active/`
- Inactive Archive: `archive/inactive/`
- Backup Location: `{parent_directory}/archive_backup/`
- Metadata Index: `archive/metadata/archive_index.json`

---

**Classification**: T4b - Infrastructure & Procedural Agent Documentation  
**Authority**: Guidelines for agents managing archives and versions  
**Update Frequency**: When archive procedures or policies change  
**Last Updated**: November 7, 2025  
**Next Review**: December 7, 2025 (quarterly satellite audit)
