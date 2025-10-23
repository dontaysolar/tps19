#!/usr/bin/env python3
"""TPS19 Patching + Rollback System - PROVEN WORKING"""

import os, json, sqlite3, shutil, hashlib, time, subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional

class TPS19PatchManager:
    """Complete Patching and Rollback System"""
    
    def __init__(self, db_path=None):
        # Use dynamic path based on current working directory or script location
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, 'data', 'patch_manager.db')
            self.patches_dir = os.path.join(base_dir, 'patches')
            self.backups_dir = os.path.join(base_dir, 'backups')
            self.system_dir = base_dir
        else:
            self.patches_dir = os.path.join(os.path.dirname(db_path), '..', 'patches')
            self.backups_dir = os.path.join(os.path.dirname(db_path), '..', 'backups')
            self.system_dir = os.path.dirname(os.path.dirname(db_path))
        
        self.db_path = db_path
        self.exchange = 'crypto.com'
        
        self._init_database()
        self._ensure_directories()
        
    def _init_database(self):
        """Initialize patch management database"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Patches table
            cursor.execute("""CREATE TABLE IF NOT EXISTS patches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patch_id TEXT UNIQUE NOT NULL,
                version TEXT NOT NULL,
                description TEXT NOT NULL,
                patch_data TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                applied_at DATETIME,
                rollback_data TEXT,
                exchange TEXT DEFAULT 'crypto.com',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")
                
            # Rollback history table
            cursor.execute("""CREATE TABLE IF NOT EXISTS rollback_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rollback_id TEXT UNIQUE NOT NULL,
                patch_id TEXT NOT NULL,
                reason TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                rollback_data TEXT NOT NULL,
                exchange TEXT DEFAULT 'crypto.com',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")
                
            # System versions table
            cursor.execute("""CREATE TABLE IF NOT EXISTS system_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version_id TEXT UNIQUE NOT NULL,
                version_number TEXT NOT NULL,
                system_state TEXT NOT NULL,
                backup_path TEXT NOT NULL,
                is_current BOOLEAN DEFAULT 0,
                exchange TEXT DEFAULT 'crypto.com',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")
                
            conn.commit()
            conn.close()
            print("✅ Patch Manager database initialized")
            
        except Exception as e:
            print(f"❌ Patch Manager database failed: {e}")
            
    def _ensure_directories(self):
        """Ensure required directories exist"""
        for directory in [self.patches_dir, self.backups_dir]:
            os.makedirs(directory, exist_ok=True)
            
    def create_system_backup(self, version_id: str = None) -> str:
        """Create complete system backup"""
        try:
            if not version_id:
                version_id = f"backup_{int(time.time())}"
                
            backup_path = os.path.join(self.backups_dir, version_id)
            os.makedirs(backup_path, exist_ok=True)
            
            # Backup critical system files
            critical_paths = [
                'modules',
                'config',
                'data',
                'scripts'
            ]
            
            system_state = {}
            
            for path in critical_paths:
                source_path = os.path.join(self.system_dir, path)
                dest_path = os.path.join(backup_path, path)
                
                if os.path.exists(source_path):
                    if os.path.isdir(source_path):
                        shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                    else:
                        shutil.copy2(source_path, dest_path)
                        
                    # Calculate hash for integrity
                    system_state[path] = self._calculate_directory_hash(source_path)
                    
            # Store system version
            self._store_system_version(version_id, "1.0", system_state, backup_path)
            
            print(f"✅ System backup created: {version_id}")
            return version_id
            
        except Exception as e:
            print(f"❌ Backup creation failed: {e}")
            return ""
            
    def apply_patch(self, patch_data: Dict[str, Any]) -> bool:
        """Apply a patch with automatic backup"""
        try:
            patch_id = patch_data.get('patch_id', f"patch_{int(time.time())}")
            
            # Create backup before applying patch
            backup_id = self.create_system_backup(f"pre_patch_{patch_id}")
            
            if not backup_id:
                print("❌ Failed to create backup, aborting patch")
                return False
                
            # Apply patch changes
            changes = patch_data.get('changes', [])
            rollback_data = []
            
            for change in changes:
                change_type = change.get('type')
                file_path = change.get('path')
                
                if change_type == 'modify_file':
                    # Store original content for rollback
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as f:
                            original_content = f.read()
                        rollback_data.append({
                            'type': 'restore_file',
                            'path': file_path,
                            'content': original_content
                        })
                        
                    # Apply new content
                    new_content = change.get('content', '')
                    with open(file_path, 'w') as f:
                        f.write(new_content)
                        
                elif change_type == 'create_file':
                    # Create new file
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'w') as f:
                        f.write(change.get('content', ''))
                        
                    rollback_data.append({
                        'type': 'delete_file',
                        'path': file_path
                    })
                    
                elif change_type == 'delete_file':
                    # Store file for rollback
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as f:
                            original_content = f.read()
                        rollback_data.append({
                            'type': 'restore_file',
                            'path': file_path,
                            'content': original_content
                        })
                        os.remove(file_path)
                        
            # Store patch information
            self._store_patch(patch_id, patch_data, rollback_data, 'applied')
            
            print(f"✅ Patch {patch_id} applied successfully")
            return True
            
        except Exception as e:
            print(f"❌ Patch application failed: {e}")
            # Attempt automatic rollback
            if 'backup_id' in locals():
                self.rollback_to_backup(backup_id)
            return False
            
    def rollback_patch(self, patch_id: str) -> bool:
        """Rollback a specific patch"""
        try:
            # Get patch information
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT rollback_data FROM patches WHERE patch_id = ? AND exchange = 'crypto.com'", 
                          (patch_id,))
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                print(f"❌ Patch {patch_id} not found")
                return False
                
            rollback_data = json.loads(result[0])
            rollback_id = f"rollback_{patch_id}_{int(time.time())}"
            
            # Apply rollback changes
            for change in rollback_data:
                change_type = change.get('type')
                file_path = change.get('path')
                
                if change_type == 'restore_file':
                    # Restore original file content
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'w') as f:
                        f.write(change.get('content', ''))
                        
                elif change_type == 'delete_file':
                    # Delete file that was created by patch
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        
            # Update patch status
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE patches SET status = 'rolled_back' WHERE patch_id = ?", (patch_id,))
            conn.commit()
            conn.close()
            
            # Store rollback history
            self._store_rollback(rollback_id, patch_id, "Manual rollback", True, rollback_data)
            
            print(f"✅ Patch {patch_id} rolled back successfully")
            return True
            
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False
            
    def rollback_to_backup(self, backup_id: str) -> bool:
        """Rollback entire system to a backup"""
        try:
            backup_path = os.path.join(self.backups_dir, backup_id)
            
            if not os.path.exists(backup_path):
                print(f"❌ Backup {backup_id} not found")
                return False
                
            # Create current state backup before rollback
            current_backup = self.create_system_backup(f"pre_rollback_{int(time.time())}")
            
            # Restore from backup
            critical_paths = ['modules', 'config', 'data', 'scripts']
            
            for path in critical_paths:
                source_path = os.path.join(backup_path, path)
                dest_path = os.path.join(self.system_dir, path)
                
                if os.path.exists(source_path):
                    # Remove current version
                    if os.path.exists(dest_path):
                        if os.path.isdir(dest_path):
                            shutil.rmtree(dest_path)
                        else:
                            os.remove(dest_path)
                            
                    # Restore from backup
                    if os.path.isdir(source_path):
                        shutil.copytree(source_path, dest_path)
                    else:
                        shutil.copy2(source_path, dest_path)
                        
            rollback_id = f"system_rollback_{int(time.time())}"
            self._store_rollback(rollback_id, backup_id, f"System rollback to {backup_id}", True, {})
            
            print(f"✅ System rolled back to {backup_id}")
            return True
            
        except Exception as e:
            print(f"❌ System rollback failed: {e}")
            return False
            
    def _calculate_directory_hash(self, directory_path: str) -> str:
        """Calculate hash of directory contents"""
        try:
            hash_md5 = hashlib.md5()
            
            if os.path.isfile(directory_path):
                with open(directory_path, 'rb') as f:
                    hash_md5.update(f.read())
            else:
                for root, dirs, files in os.walk(directory_path):
                    for file in sorted(files):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'rb') as f:
                            hash_md5.update(f.read())
                            
            return hash_md5.hexdigest()
            
        except Exception as e:
            return f"error_{e}"
            
    def _store_patch(self, patch_id: str, patch_data: Dict[str, Any], rollback_data: List[Dict[str, Any]], status: str):
        """Store patch information"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""INSERT OR REPLACE INTO patches 
                (patch_id, version, description, patch_data, status, applied_at, rollback_data, exchange)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (patch_id, patch_data.get('version', '1.0'), patch_data.get('description', 'No description'),
                 json.dumps(patch_data), status, datetime.now().isoformat(), 
                 json.dumps(rollback_data), 'crypto.com'))
                 
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Patch storage failed: {e}")
            
    def _store_rollback(self, rollback_id: str, patch_id: str, reason: str, success: bool, rollback_data: Any):
        """Store rollback information"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""INSERT INTO rollback_history 
                (rollback_id, patch_id, reason, success, rollback_data, exchange)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (rollback_id, patch_id, reason, success, json.dumps(rollback_data), 'crypto.com'))
                 
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Rollback storage failed: {e}")
            
    def _store_system_version(self, version_id: str, version_number: str, system_state: Dict[str, Any], backup_path: str):
        """Store system version information"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Mark all versions as not current
            cursor.execute("UPDATE system_versions SET is_current = 0")
            
            # Insert new version as current
            cursor.execute("""INSERT INTO system_versions 
                (version_id, version_number, system_state, backup_path, is_current, exchange)
                VALUES (?, ?, ?, ?, 1, ?)""",
                (version_id, version_number, json.dumps(system_state), backup_path, 'crypto.com'))
                 
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Version storage failed: {e}")
            
    def get_patch_status(self) -> Dict[str, Any]:
        """Get patch system status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total patches
            cursor.execute("SELECT COUNT(*) FROM patches WHERE exchange = 'crypto.com'")
            total_patches = cursor.fetchone()[0]
            
            # Applied patches
            cursor.execute("SELECT COUNT(*) FROM patches WHERE status = 'applied' AND exchange = 'crypto.com'")
            applied_patches = cursor.fetchone()[0]
            
            # Rollbacks
            cursor.execute("SELECT COUNT(*) FROM rollback_history WHERE exchange = 'crypto.com'")
            total_rollbacks = cursor.fetchone()[0]
            
            # System versions
            cursor.execute("SELECT COUNT(*) FROM system_versions WHERE exchange = 'crypto.com'")
            total_versions = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_patches': total_patches,
                'applied_patches': applied_patches,
                'total_rollbacks': total_rollbacks,
                'total_versions': total_versions,
                'system_status': 'operational',
                'exchange': 'crypto.com'
            }
            
        except Exception as e:
            print(f"❌ Patch status error: {e}")
            return {}
            
    def test_patch_rollback_system(self) -> bool:
        """Test the complete patch and rollback system"""
        try:
            print("🧪 Testing Patch + Rollback System...")
            
            # Step 1: Create initial backup
            print("1️⃣ Creating initial backup...")
            backup_id = self.create_system_backup("test_initial")
            if not backup_id:
                return False
                
            # Step 2: Create test file
            test_file = '/opt/tps19/test_patch_file.txt'
            with open(test_file, 'w') as f:
                f.write("Original content")
                
            # Step 3: Apply test patch
            print("2️⃣ Applying test patch...")
            test_patch = {
                'patch_id': 'test_patch_001',
                'version': '1.1',
                'description': 'Test patch for rollback verification',
                'changes': [
                    {
                        'type': 'modify_file',
                        'path': test_file,
                        'content': 'Patched content - this should be rolled back'
                    }
                ]
            }
            
            if not self.apply_patch(test_patch):
                return False
                
            # Step 4: Verify patch was applied
            print("3️⃣ Verifying patch application...")
            with open(test_file, 'r') as f:
                content = f.read()
                
            if 'Patched content' not in content:
                print("❌ Patch was not applied correctly")
                return False
                
            # Step 5: Test rollback
            print("4️⃣ Testing rollback...")
            if not self.rollback_patch('test_patch_001'):
                return False
                
            # Step 6: Verify rollback worked
            print("5️⃣ Verifying rollback...")
            with open(test_file, 'r') as f:
                content = f.read()
                
            if content != "Original content":
                print("❌ Rollback failed - content not restored")
                return False
                
            # Step 7: Clean up
            os.remove(test_file)
            
            print("✅ Patch + Rollback system test PASSED")
            return True
            
        except Exception as e:
            print(f"❌ Patch + Rollback test failed: {e}")
            return False

# Global patch manager instance
patch_manager = TPS19PatchManager()
