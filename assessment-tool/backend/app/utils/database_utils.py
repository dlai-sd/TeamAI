"""
Database utilities for backup, export, and maintenance
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import csv


class DatabaseUtils:
    """Utilities for database operations"""
    
    def __init__(self, db_path: str = "assessment.db"):
        self.db_path = db_path
    
    def backup_database(self, backup_dir: str = "backups") -> str:
        """
        Create a backup of the SQLite database
        Returns: Path to backup file
        """
        backup_path = Path(backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_path / f"assessment_backup_{timestamp}.db"
        
        # Copy database file
        source = sqlite3.connect(self.db_path)
        dest = sqlite3.connect(str(backup_file))
        
        source.backup(dest)
        
        dest.close()
        source.close()
        
        print(f"✅ Database backed up to: {backup_file}")
        return str(backup_file)
    
    def export_to_json(self, output_file: str = None) -> str:
        """
        Export all assessments to JSON
        Returns: Path to JSON file
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"assessments_export_{timestamp}.json"
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all assessments
        cursor.execute("SELECT * FROM assessments")
        rows = cursor.fetchall()
        
        # Convert to dictionaries
        assessments = [dict(row) for row in rows]
        
        # Write to JSON
        with open(output_file, 'w') as f:
            json.dump(assessments, f, indent=2, default=str)
        
        conn.close()
        
        print(f"✅ Exported {len(assessments)} assessments to: {output_file}")
        return output_file
    
    def export_to_csv(self, output_file: str = None) -> str:
        """
        Export all assessments to CSV
        Returns: Path to CSV file
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"assessments_export_{timestamp}.csv"
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all assessments
        cursor.execute("SELECT * FROM assessments")
        rows = cursor.fetchall()
        
        if not rows:
            print("No assessments to export")
            return None
        
        # Write to CSV
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            
            for row in rows:
                writer.writerow(dict(row))
        
        conn.close()
        
        print(f"✅ Exported {len(rows)} assessments to: {output_file}")
        return output_file
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total assessments
        cursor.execute("SELECT COUNT(*) FROM assessments")
        stats["total_assessments"] = cursor.fetchone()[0]
        
        # By status
        cursor.execute(
            "SELECT status, COUNT(*) as count FROM assessments GROUP BY status"
        )
        stats["by_status"] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # By industry
        cursor.execute(
            "SELECT industry, COUNT(*) as count FROM assessments GROUP BY industry"
        )
        stats["by_industry"] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Recent assessments (last 7 days)
        cursor.execute(
            """
            SELECT COUNT(*) FROM assessments 
            WHERE created_at >= datetime('now', '-7 days')
            """
        )
        stats["last_7_days"] = cursor.fetchone()[0]
        
        conn.close()
        
        return stats
    
    def cleanup_old_assessments(self, days: int = 90) -> int:
        """
        Delete assessments older than specified days
        Returns: Number of deleted records
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            DELETE FROM assessments 
            WHERE created_at < datetime('now', ? || ' days')
            """,
            (f"-{days}",)
        )
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"✅ Deleted {deleted} assessments older than {days} days")
        return deleted
    
    def vacuum_database(self):
        """Optimize database file size"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("VACUUM")
        conn.close()
        print("✅ Database vacuumed (optimized)")


def main():
    """CLI tool for database utilities"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python database_utils.py [backup|export-json|export-csv|stats|cleanup|vacuum]")
        return
    
    utils = DatabaseUtils()
    command = sys.argv[1]
    
    if command == "backup":
        utils.backup_database()
    elif command == "export-json":
        utils.export_to_json()
    elif command == "export-csv":
        utils.export_to_csv()
    elif command == "stats":
        stats = utils.get_statistics()
        print(json.dumps(stats, indent=2))
    elif command == "cleanup":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 90
        utils.cleanup_old_assessments(days)
    elif command == "vacuum":
        utils.vacuum_database()
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
