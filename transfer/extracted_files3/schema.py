#!/usr/bin/env python3
"""
JIHUB Database Schema
=====================
DuckDB schema setup for JobIntel Hub.
Includes: companies, job_postings, field_observations, resume_versions, assessments

Usage:
    python schema.py --init        # Create fresh database
    python schema.py --reset       # Drop and recreate all tables
    python schema.py --export      # Export all tables to parquet
"""

import duckdb
import argparse
from pathlib import Path
from datetime import datetime
import json


class JIHUBDatabase:
    """Database manager for JobIntel Hub."""
    
    def __init__(self, db_path: str = "./jihub.duckdb"):
        self.db_path = Path(db_path)
        self.conn = None
    
    def connect(self):
        """Establish database connection."""
        self.conn = duckdb.connect(str(self.db_path))
        # Enable UUID extension
        self.conn.execute("INSTALL 'uuid'; LOAD 'uuid';")
        return self
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def __enter__(self):
        return self.connect()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def init_schema(self):
        """Create all tables with proper schema."""
        
        # Companies table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id UUID PRIMARY KEY DEFAULT uuid(),
                name TEXT NOT NULL,
                domain TEXT,
                claimed_size TEXT,
                claimed_funding NUMERIC,
                first_seen DATE DEFAULT CURRENT_DATE,
                last_verified DATE,
                address TEXT,
                ghost_score NUMERIC(5,2) DEFAULT 0.0,
                audit_priority INTEGER DEFAULT 0,
                metadata JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Indexes for companies
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_companies_ghost_score ON companies(ghost_score DESC)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_companies_audit_priority ON companies(audit_priority DESC)")
        
        # Job postings table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS job_postings (
                id UUID PRIMARY KEY DEFAULT uuid(),
                company_id UUID REFERENCES companies(id),
                title TEXT NOT NULL,
                location TEXT,
                posted_date DATE,
                scraped_date DATE DEFAULT CURRENT_DATE,
                description TEXT,
                salary_min NUMERIC,
                salary_max NUMERIC,
                application_count INTEGER,
                source TEXT NOT NULL,
                url TEXT UNIQUE,
                freshness_score NUMERIC(5,2) DEFAULT 0.0,
                is_active BOOLEAN DEFAULT TRUE,
                requirements TEXT,
                funding_mentions TEXT,
                company_size_claims TEXT,
                raw_data JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Indexes for job_postings
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_company ON job_postings(company_id)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_posted_date ON job_postings(posted_date DESC)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_freshness ON job_postings(freshness_score DESC)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_source ON job_postings(source)")
        
        # Field observations table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS field_observations (
                id UUID PRIMARY KEY DEFAULT uuid(),
                company_id UUID REFERENCES companies(id),
                observation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                observation_type TEXT NOT NULL CHECK (
                    observation_type IN ('photo', 'audio', 'video', 'interview', 'note', 'conversation')
                ),
                media_path TEXT,
                transcript TEXT,
                occupancy_estimate INTEGER,
                employee_count_observed INTEGER,
                activity_level TEXT CHECK (
                    activity_level IN ('none', 'low', 'medium', 'high', 'ghost')
                ),
                confidence_score NUMERIC(5,2),
                legal_release_obtained BOOLEAN DEFAULT FALSE,
                consent_form_path TEXT,
                metadata_scrubbed BOOLEAN DEFAULT FALSE,
                metadata JSON,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Indexes for field_observations
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_observations_company ON field_observations(company_id)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_observations_timestamp ON field_observations(observation_timestamp DESC)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_observations_type ON field_observations(observation_type)")
        
        # Resume versions table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS resume_versions (
                id UUID PRIMARY KEY DEFAULT uuid(),
                original_path TEXT,
                original_hash TEXT,
                transform_type TEXT NOT NULL CHECK (
                    transform_type IN ('content_swap', 'format_swap', 'style_swap', 'structure_swap', 'hybrid')
                ),
                transform_params JSON,
                output_path TEXT,
                content_hash TEXT,
                format_preservation_score NUMERIC(5,2),
                gemini_quality_score NUMERIC(5,2),
                applied_to_jobs UUID[],
                interview_invite_count INTEGER DEFAULT 0,
                interview_invite_rate NUMERIC(5,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Indexes for resume_versions
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_resumes_created ON resume_versions(created_at DESC)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_resumes_interview_rate ON resume_versions(interview_invite_rate DESC)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_resumes_transform_type ON resume_versions(transform_type)")
        
        # Assessments table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS assessments (
                id UUID PRIMARY KEY DEFAULT uuid(),
                company_id UUID REFERENCES companies(id),
                assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ghost_probability NUMERIC(5,2),
                online_vs_physical_discrepancy NUMERIC(5,2),
                funding_fraud_risk NUMERIC(5,2),
                legitimacy_score NUMERIC(5,2),
                audit_priority_ranking INTEGER,
                audit_recommendation TEXT,
                evidence_refs JSON,
                analysis_notes TEXT,
                exported BOOLEAN DEFAULT FALSE,
                export_path TEXT,
                export_format TEXT,
                verified_by_third_party BOOLEAN DEFAULT FALSE,
                verification_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Indexes for assessments
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_assessments_company ON assessments(company_id)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_assessments_ghost_prob ON assessments(ghost_probability DESC)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_assessments_date ON assessments(assessment_date DESC)")
        
        # Agent messages table (for SHL audit trail)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_messages (
                id UUID PRIMARY KEY DEFAULT uuid(),
                message_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                agent_from TEXT NOT NULL,
                agent_to TEXT NOT NULL,
                task_id TEXT,
                action TEXT NOT NULL CHECK (
                    action IN ('request', 'response', 'error', 'status_update', 'human_intervention')
                ),
                params JSON,
                priority TEXT DEFAULT 'normal',
                status TEXT,
                output_ref TEXT,
                processing_time_ms INTEGER,
                confidence_score NUMERIC(5,2),
                error_code TEXT,
                error_message TEXT,
                retry_count INTEGER DEFAULT 0,
                raw_shl_message TEXT
            )
        """)
        
        # Indexes for agent_messages
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON agent_messages(message_timestamp DESC)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_task ON agent_messages(task_id)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_agents ON agent_messages(agent_from, agent_to)")
        
        # API usage tracking table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS api_usage (
                id UUID PRIMARY KEY DEFAULT uuid(),
                usage_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                api_name TEXT NOT NULL,
                endpoint TEXT,
                tokens_input INTEGER,
                tokens_output INTEGER,
                cost_estimate NUMERIC(10,6),
                task_id TEXT,
                agent_name TEXT,
                response_time_ms INTEGER,
                success BOOLEAN,
                error_message TEXT
            )
        """)
        
        # Index for api_usage
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_api_usage_timestamp ON api_usage(usage_timestamp DESC)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_api_usage_api ON api_usage(api_name)")
        
        print("[+] Schema initialized successfully")
        return self
    
    def reset_schema(self):
        """Drop all tables and recreate."""
        tables = [
            'api_usage', 'agent_messages', 'assessments', 
            'resume_versions', 'field_observations', 'job_postings', 'companies'
        ]
        
        for table in tables:
            self.conn.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
            print(f"  [-] Dropped table: {table}")
        
        self.init_schema()
        print("[+] Schema reset complete")
        return self
    
    def export_to_parquet(self, output_dir: str = "./exports"):
        """Export all tables to parquet files."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        tables = [
            'companies', 'job_postings', 'field_observations',
            'resume_versions', 'assessments', 'agent_messages', 'api_usage'
        ]
        
        for table in tables:
            parquet_path = output_path / f"{table}_{timestamp}.parquet"
            self.conn.execute(f"""
                COPY {table} TO '{parquet_path}' (FORMAT PARQUET, COMPRESSION ZSTD)
            """)
            print(f"  [+] Exported: {parquet_path}")
        
        # Create manifest
        manifest = {
            "export_timestamp": timestamp,
            "tables": tables,
            "format": "parquet",
            "compression": "zstd",
            "jihub_version": "0.1"
        }
        
        manifest_path = output_path / f"manifest_{timestamp}.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"[+] Export complete: {output_path}")
        return self
    
    def get_stats(self):
        """Get table statistics."""
        stats = {}
        tables = [
            'companies', 'job_postings', 'field_observations',
            'resume_versions', 'assessments', 'agent_messages', 'api_usage'
        ]
        
        for table in tables:
            result = self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
            stats[table] = result[0]
        
        return stats
    
    def print_stats(self):
        """Print database statistics."""
        stats = self.get_stats()
        print("\n" + "=" * 40)
        print("  JIHUB Database Statistics")
        print("=" * 40)
        for table, count in stats.items():
            print(f"  {table}: {count} records")
        print("=" * 40)
        return self


# Utility functions for common operations
def get_db(db_path: str = "./jihub.duckdb") -> JIHUBDatabase:
    """Get database instance."""
    return JIHUBDatabase(db_path)


def quick_query(query: str, db_path: str = "./jihub.duckdb"):
    """Execute a quick query and return results."""
    with JIHUBDatabase(db_path) as db:
        return db.conn.execute(query).fetchall()


def main():
    parser = argparse.ArgumentParser(description="JIHUB Database Schema Manager")
    parser.add_argument('--init', action='store_true', help='Initialize database schema')
    parser.add_argument('--reset', action='store_true', help='Reset (drop and recreate) all tables')
    parser.add_argument('--export', action='store_true', help='Export all tables to parquet')
    parser.add_argument('--stats', action='store_true', help='Show database statistics')
    parser.add_argument('--db', type=str, default='./jihub.duckdb', help='Database file path')
    parser.add_argument('--export-dir', type=str, default='./exports', help='Export directory')
    
    args = parser.parse_args()
    
    with JIHUBDatabase(args.db) as db:
        if args.reset:
            confirm = input("This will DELETE all data. Type 'yes' to confirm: ")
            if confirm.lower() == 'yes':
                db.reset_schema()
            else:
                print("Reset cancelled.")
        elif args.init:
            db.init_schema()
        elif args.export:
            db.export_to_parquet(args.export_dir)
        elif args.stats:
            db.print_stats()
        else:
            # Default: init if needed, show stats
            db.init_schema()
            db.print_stats()


if __name__ == '__main__':
    main()
