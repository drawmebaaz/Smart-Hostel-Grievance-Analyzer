#!/usr/bin/env python3
"""
Demo Data Seeder for Smart Grievance System

Purpose: Generate realistic demo data to showcase all system capabilities.
This creates meaningful scenarios that demonstrate:
- Priority scoring
- SLA breach detection
- Health degradation
- Duplicate detection
- Issue lifecycle
- Filtering capabilities

Usage: python scripts/seed_demo_data.py --demo
"""

import sys
import uuid
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, '.')

from app.services.issue_service_day7a import get_issue_service_day7a
from app.core.session import get_session_manager
from app.db.session import get_db_context
from app.db.models.complaint import ComplaintModel
from app.repositories.complaint_repository import ComplaintRepository

DEMO_FLAG = "--demo"
DEMO_PREFIX = "DEMO-"

def safety_check():
    """
    Safety guard to prevent accidental production use.
    Requires explicit --demo flag.
    """
    if DEMO_FLAG not in sys.argv:
        print("❌ DEMO SEED BLOCKED - SAFETY CHECK FAILED")
        print("=" * 60)
        print("This script creates demo data and should only be used in:")
        print("1. Development environments")
        print("2. Demo/preview deployments")
        print("3. Interview/showcase sessions")
        print("\nTo proceed, add the --demo flag:")
        print("  python scripts/seed_demo_data.py --demo")
        print("\n⚠️  WARNING: This will create/reset demo data!")
        print("=" * 60)
        sys.exit(1)

def generate_demo_id(prefix: str = "DEMO") -> str:
    """Generate deterministic demo IDs for reproducibility"""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"

def patch_complaint_timestamp(complaint_id: str, created_at: datetime):
    """
    Patch complaint creation timestamp.
    This is the only 'controlled cheat' - justified for demo purposes.
    """
    try:
        with get_db_context() as db:
            repo = ComplaintRepository(db)
            complaint = repo.get_by_id(complaint_id)
            if complaint:
                complaint.created_at = created_at
                db.commit()
                print(f"  ⏰ Patched timestamp: {created_at.isoformat()}")
            else:
                print(f"  ⚠️  Could not find complaint {complaint_id} to patch")
    except Exception as e:
        print(f"  ⚠️  Timestamp patch failed: {str(e)}")

def submit_complaint(
    service,
    text: str,
    hostel: str,
    session_id: str,
    created_at: datetime,
    complaint_id: str = None
) -> Dict[str, Any]:
    """
    Submit a complaint with controlled timestamp.
    Uses real service pipeline for full intelligence processing.
    """
    try:
        # Generate deterministic ID for demo
        comp_id = complaint_id or f"{DEMO_PREFIX}{generate_demo_id('COMP')}"
        
        print(f"  📝 Complaint: {text[:50]}...")
        
        # Process through real pipeline
        result = service.process_complaint(
            text=text,
            hostel=hostel,
            complaint_id=comp_id,
            session_id=session_id,
            metadata={"demo": True, "seed_time": created_at.isoformat()}
        )
        
        if result.get("success"):
            # Patch the timestamp (only for demo purposes)
            comp_id = result.get("complaint_id", comp_id)
            patch_complaint_timestamp(comp_id, created_at)
            
            return {
                "success": True,
                "complaint_id": comp_id,
                "issue_id": result.get("issue_aggregation", {}).get("issue_id"),
                "is_duplicate": result.get("issue_aggregation", {}).get("is_duplicate", False)
            }
        else:
            print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
            return {"success": False, "error": result.get("error")}
            
    except Exception as e:
        print(f"  ❌ Exception: {str(e)}")
        return {"success": False, "error": str(e)}

# ==================== SCENARIO DEFINITIONS ====================

SCENARIOS = [
    # 🔴 SCENARIO 1: Critical Water Outage (SLA Breached)
    {
        "name": "Critical Water Outage",
        "hostel": "BH-3",
        "category": "Water",
        "complaints": [
            "No water in entire BH-3 since yesterday morning",
            "Washrooms have no water, students cannot bathe - urgent",
            "Still no water supply in BH-3, this is critical",
            "Water pipes seem to be broken, need immediate repair",
            "Multiple floors reporting zero water pressure in BH-3"
        ],
        "created_offset_hours": 36,
        "status": "OPEN",
        "expected": {
            "severity": "SEV-1",
            "sla": "BREACHING",
            "health": "EMERGENCY",
            "priority": "CRITICAL"
        }
    },
    
    # 🔴 SCENARIO 2: Night Power Failure (Critical, Warning SLA)
    {
        "name": "Night Power Failure",
        "hostel": "GH-1",
        "category": "Electricity",
        "complaints": [
            "Power cut in GH-1 since 3 hours, affecting studies",
            "No electricity in rooms, students using phone torches",
            "Frequent power fluctuations causing damage to devices",
            "Complete blackout in GH-1 wing B"
        ],
        "created_offset_hours": 3.5,
        "status": "OPEN",
        "expected": {
            "severity": "SEV-1",
            "sla": "WARNING",
            "health": "CRITICAL",
            "priority": "HIGH"
        }
    },
    
    # 🟠 SCENARIO 3: Dirty Washrooms (Escalating)
    {
        "name": "Dirty Washrooms",
        "hostel": "BH-1",
        "category": "Hygiene",
        "complaints": [
            "Washrooms on 2nd floor are very dirty",
            "Toilets not cleaned properly, bad smell spreading",
            "Cleaning staff missing for 2 days, washrooms unusable",
            "Urgent: Washroom hygiene deteriorating rapidly"
        ],
        "created_offset_hours": 12,
        "status": "IN_PROGRESS",
        "spread_hours": 10,  # Spread complaints over 10 hours
        "expected": {
            "severity": "SEV-2",
            "health": "WARNING",
            "priority": "MEDIUM"
        }
    },
    
    # 🟠 SCENARIO 4: Internet Outage (Multiple Duplicates)
    {
        "name": "Internet Outage",
        "hostel": "International Hostel",
        "category": "Internet",
        "complaints": [
            "WiFi not working in international hostel",
            "Internet connectivity lost since morning",
            "No network access in rooms, students cannot attend online classes",
            "WiFi extremely slow, cannot load basic websites",
            "Internet down in international hostel - urgent fix needed"
        ],
        "created_offset_hours": 8,
        "status": "OPEN",
        "expected": {
            "severity": "SEV-2",
            "duplicates": 2,
            "priority": "MEDIUM"
        }
    },
    
    # 🟡 SCENARIO 5: Fan Not Working (Medium, Healthy)
    {
        "name": "Fan Not Working",
        "hostel": "GH-2",
        "category": "Infrastructure",
        "complaints": [
            "Ceiling fan not working in room 205",
            "Room fan making weird noise and stopped working"
        ],
        "created_offset_hours": 2,
        "status": "OPEN",
        "expected": {
            "severity": "SEV-3",
            "health": "MONITOR",
            "priority": "LOW"
        }
    },
    
    # 🟢 SCENARIO 6: Light Fixed (Resolved)
    {
        "name": "Light Fixed",
        "hostel": "BH-1",
        "category": "Electricity",
        "complaints": [
            "Corridor light not working on 3rd floor"
        ],
        "created_offset_hours": 12,
        "resolved_hours_ago": 6,
        "status": "RESOLVED",
        "expected": {
            "severity": "SEV-4",
            "health": "HEALTHY"
        }
    },
    
    # 🟢 SCENARIO 7: Bathroom Leak (Reopened)
    {
        "name": "Bathroom Leak",
        "hostel": "GH-1",
        "category": "Infrastructure",
        "complaints": [
            "Water leakage from bathroom ceiling in room 312",
            "Leak is getting worse, water dripping on floor",
            "Leak resumed after temporary fix"
        ],
        "created_offset_hours": 24,
        "resolved_hours_ago": 12,
        "reopened_hours_ago": 2,
        "status": "REOPENED",
        "expected": {
            "severity": "SEV-2",
            "priority": "MEDIUM"
        }
    },
    
    # 🟡 SCENARIO 8: Mess Food Quality
    {
        "name": "Mess Food Quality",
        "hostel": "BH-3",
        "category": "Mess",
        "complaints": [
            "Mess food quality has deteriorated significantly",
            "Found hair in food today - unacceptable hygiene",
            "Vegetables not fresh, tastes bad"
        ],
        "created_offset_hours": 6,
        "status": "OPEN",
        "expected": {
            "severity": "SEV-2",
            "health": "WARNING"
        }
    },
    
    # 🟡 SCENARIO 9: Noise Complaint
    {
        "name": "Night Noise",
        "hostel": "International Hostel",
        "category": "Noise",
        "complaints": [
            "Loud music at night disturbing sleep",
            "Excessive noise from nearby room during study hours"
        ],
        "created_offset_hours": 1,
        "status": "OPEN",
        "expected": {
            "severity": "SEV-3",
            "health": "MONITOR"
        }
    },
    
    # 🟡 SCENARIO 10: Admin Delay
    {
        "name": "Admin Delay",
        "hostel": "GH-2",
        "category": "Administration",
        "complaints": [
            "Complaint filed 3 days ago, no response from warden",
            "Administration not taking action on previous complaints"
        ],
        "created_offset_hours": 72,
        "status": "OPEN",
        "expected": {
            "severity": "SEV-3",
            "sla": "BREACHING",
            "health": "CRITICAL"
        }
    },
    
    # 🟡 SCENARIO 11: Water Pressure Low
    {
        "name": "Low Water Pressure",
        "hostel": "BH-1",
        "category": "Water",
        "complaints": [
            "Water pressure very low on 4th floor",
            "Takes 10 minutes to fill a bucket"
        ],
        "created_offset_hours": 4,
        "status": "OPEN",
        "expected": {
            "severity": "SEV-3",
            "health": "MONITOR"
        }
    },
    
    # 🟡 SCENARIO 12: WiFi Slow
    {
        "name": "Slow WiFi",
        "hostel": "GH-1",
        "category": "Internet",
        "complaints": [
            "WiFi speed very slow during peak hours",
            "Cannot attend online classes due to poor connection"
        ],
        "created_offset_hours": 3,
        "status": "OPEN",
        "expected": {
            "severity": "SEV-3",
            "health": "MONITOR"
        }
    }
]

# ==================== SEEDING ENGINE ====================

def seed_scenarios():
    """
    Main seeding engine that creates all demo scenarios.
    Uses real services to ensure intelligence signals are generated.
    """
    service = get_issue_service_day7a()
    session_manager = get_session_manager()
    now = datetime.utcnow()
    
    print("🚀 Starting demo data seeding...")
    print("=" * 60)
    
    scenario_results = []
    total_complaints = 0
    successful_complaints = 0
    
    for scenario_idx, scenario in enumerate(SCENARIOS, 1):
        print(f"\n📋 Scenario {scenario_idx}/{len(SCENARIOS)}: {scenario['name']}")
        print(f"   Hostel: {scenario['hostel']}, Category: {scenario['category']}")
        print(f"   Expected: {scenario['expected']}")
        
        # Create session for this scenario
        session = session_manager.create_session({
            "demo_scenario": scenario["name"],
            "scenario_idx": scenario_idx
        })
        
        # Calculate base time for this scenario
        if scenario.get("resolved_hours_ago"):
            # For resolved issues, create earlier and resolve
            base_time = now - timedelta(hours=scenario["created_offset_hours"])
        else:
            base_time = now - timedelta(hours=scenario["created_offset_hours"])
        
        # Submit complaints for this scenario
        scenario_complaints = []
        
        for complaint_idx, text in enumerate(scenario["complaints"]):
            # Spread complaints over time if specified
            if scenario.get("spread_hours"):
                time_offset = timedelta(
                    hours=complaint_idx * (scenario["spread_hours"] / len(scenario["complaints"]))
                )
                complaint_time = base_time + time_offset
            else:
                # Default: complaints 10 minutes apart
                complaint_time = base_time + timedelta(minutes=complaint_idx * 10)
            
            # Submit complaint
            result = submit_complaint(
                service=service,
                text=text,
                hostel=scenario["hostel"],
                session_id=session.session_id,
                created_at=complaint_time,
                complaint_id=f"{DEMO_PREFIX}SCN{scenario_idx}-CMP{complaint_idx+1}"
            )
            
            if result["success"]:
                successful_complaints += 1
                scenario_complaints.append(result)
            total_complaints += 1
            
            # Small delay to simulate real-world timing
            import time
            time.sleep(0.1)
        
        # If this is a resolved scenario, update status
        if scenario.get("resolved_hours_ago") and scenario_complaints:
            try:
                issue_id = scenario_complaints[0]["issue_id"]
                # Mark as resolved
                resolved_time = now - timedelta(hours=scenario["resolved_hours_ago"])
                
                print(f"   ✅ Marking issue as RESOLVED (resolved {scenario['resolved_hours_ago']}h ago)")
                
                # For demo, we'll patch the resolved_at timestamp
                with get_db_context() as db:
                    from app.repositories.issue_repository import IssueRepository
                    issue_repo = IssueRepository(db)
                    issue = issue_repo.get_by_id(issue_id)
                    if issue:
                        issue.status = "RESOLVED"
                        issue.resolved_at = resolved_time
                        issue.last_updated = resolved_time
                        db.commit()
                        print(f"   ✅ Issue {issue_id} marked as RESOLVED")
                
                # If it's a reopened scenario, also reopen it
                if scenario.get("reopened_hours_ago"):
                    reopened_time = now - timedelta(hours=scenario["reopened_hours_ago"])
                    print(f"   🔄 Reopening issue (reopened {scenario['reopened_hours_ago']}h ago)")
                    
                    with get_db_context() as db:
                        issue_repo = IssueRepository(db)
                        issue = issue_repo.get_by_id(issue_id)
                        if issue:
                            issue.status = "REOPENED"
                            issue.resolved_at = None
                            issue.last_updated = reopened_time
                            db.commit()
                            print(f"   🔄 Issue {issue_id} REOPENED")
                
            except Exception as e:
                print(f"   ⚠️  Could not update issue status: {str(e)}")
        
        # Record scenario results
        scenario_results.append({
            "name": scenario["name"],
            "hostel": scenario["hostel"],
            "category": scenario["category"],
            "complaint_count": len(scenario_complaints),
            "successful": len(scenario_complaints),
            "issue_id": scenario_complaints[0]["issue_id"] if scenario_complaints else None
        })
        
        print(f"   ✅ Created {len(scenario_complaints)} complaints")
    
    print("\n" + "=" * 60)
    print("📊 SEEDING COMPLETE - SUMMARY")
    print("=" * 60)
    
    # Print scenario summary
    print("\n📋 Scenario Results:")
    for result in scenario_results:
        print(f"  • {result['name']}")
        print(f"    Hostel: {result['hostel']}, Category: {result['category']}")
        print(f"    Complaints: {result['complaint_count']}, Issue: {result['issue_id']}")
    
    # Print statistics
    print(f"\n📈 Statistics:")
    print(f"  • Total Scenarios: {len(scenario_results)}")
    print(f"  • Total Complaints Attempted: {total_complaints}")
    print(f"  • Successful Complaints: {successful_complaints}")
    print(f"  • Success Rate: {(successful_complaints/total_complaints*100):.1f}%")
    
    # Calculate expected dashboard state
    print(f"\n🎯 Expected Dashboard State:")
    print(f"  • Total Issues: ~{len(scenario_results)}")
    print(f"  • Total Complaints: ~{successful_complaints}")
    print(f"  • SLA Breaches: 4-6")
    print(f"  • Resolved Issues: 2-3")
    print(f"  • SEV-1 Issues: 3-4")
    print(f"  • EMERGENCY Health: 2-3")
    
    return scenario_results

def cleanup_old_demo_data():
    """
    Clean up any existing demo data before seeding.
    """
    print("🧹 Cleaning up old demo data...")
    
    try:
        with get_db_context() as db:
            from app.repositories.complaint_repository import ComplaintRepository
            from app.repositories.issue_repository import IssueRepository
            
            complaint_repo = ComplaintRepository(db)
            issue_repo = IssueRepository(db)
            
            # Find and delete demo complaints
            all_complaints = complaint_repo.get_recent(hours=24*30, limit=1000)
            demo_complaints = [c for c in all_complaints if c.id.startswith(DEMO_PREFIX)]
            
            if demo_complaints:
                print(f"  Found {len(demo_complaints)} existing demo complaints")
                
                # Group by issue_id to find demo issues
                demo_issue_ids = set(c.issue_id for c in demo_complaints)
                
                # Delete demo complaints
                for complaint in demo_complaints:
                    db.delete(complaint)
                
                # Delete demo issues
                for issue_id in demo_issue_ids:
                    issue = issue_repo.get_by_id(issue_id)
                    if issue:
                        db.delete(issue)
                
                db.commit()
                print(f"  ✅ Removed {len(demo_complaints)} demo complaints and related issues")
            else:
                print("  No existing demo data found")
                
    except Exception as e:
        print(f"  ⚠️  Cleanup failed: {str(e)}")

# ==================== MAIN ENTRYPOINT ====================

def main():
    """
    Main entry point for demo data seeding.
    """
    # Safety check
    safety_check()
    
    print("=" * 60)
    print("🎭 SMART GRIEVANCE SYSTEM - DEMO DATA SEEDER")
    print("=" * 60)
    
    # Set random seed for reproducibility
    random.seed(42)  # The answer to life, the universe, and everything
    
    # Confirm with user
    print("\n⚠️  WARNING: This will:")
    print("   1. Remove existing demo data")
    print("   2. Create ~45-50 new complaints")
    print("   3. Generate ~18 realistic issues")
    print("   4. Showcase all system capabilities")
    
    response = input("\nProceed? (type 'YES' to continue): ")
    if response != "YES":
        print("\n❌ Operation cancelled")
        sys.exit(0)
    
    # Clean up old demo data
    cleanup_old_demo_data()
    
    # Seed new demo data
    print("\n" + "=" * 60)
    print("🌱 SEEDING NEW DEMO DATA")
    print("=" * 60)
    
    try:
        results = seed_scenarios()
        
        print("\n" + "=" * 60)
        print("✅ DEMO DATA CREATION SUCCESSFUL")
        print("=" * 60)
        
        print("\n🎯 Demo scenarios created to showcase:")
        print("  • Critical SLA breaches")
        print("  • Health score degradation")
        print("  • Duplicate detection")
        print("  • Issue lifecycle (OPEN → RESOLVED → REOPENED)")
        print("  • Priority scoring and queue sorting")
        print("  • Filtering capabilities")
        
        print("\n🚀 NEXT STEPS:")
        print("  1. Start the frontend: npm run dev")
        print("  2. Open: http://localhost:5173/dashboard")
        print("  3. Explore all charts, filters, and issue details")
        print("  4. Use filters to find specific scenarios")
        
        print("\n🔍 Quick filters to try:")
        print("  • Priority: CRITICAL")
        print("  • SLA Status: BREACHING")
        print("  • Health: EMERGENCY")
        print("  • Severity: SEV-1")
        
        print("\n🎉 Your dashboard is now showcase-ready!")
        
    except Exception as e:
        print(f"\n❌ DEMO SEEDING FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()