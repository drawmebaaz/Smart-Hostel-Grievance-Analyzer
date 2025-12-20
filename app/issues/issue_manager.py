#!/usr/bin/env python3
"""
Issue Manager - Core of Day 5
Responsible for grouping complaints into issues
"""

from typing import Dict, Optional, List, Tuple
from datetime import datetime
import uuid

from app.issues.issue import Issue
from app.issues.complaint import Complaint
from app.issues.issue_id import generate_issue_id, generate_issue_key
from app.issues.urgency_rules import get_urgency_score
from app.issues.validators import (
    validate_category, 
    validate_hostel, 
    validate_complaint_id,
    validate_embedding
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


class IssueManager:
    """
    Manages issue lifecycle and complaint grouping.
    """
    
    def __init__(self, duplicate_threshold: float = 0.88):  # Changed from 0.82 to 0.75
        self.issues: Dict[str, Issue] = {}  # issue_id -> Issue
        self.issue_key_index: Dict[str, str] = {}  # issue_key -> issue_id
        self.duplicate_threshold = duplicate_threshold
        
        # Statistics
        self.total_complaints = 0
        self.total_issues = 0
        
        logger.info(f"IssueManager initialized (threshold: {duplicate_threshold})")
    
    def process_complaint(
        self,
        complaint_id: str,
        text: str,
        category: str,
        urgency: str,
        hostel: str,
        embedding: List[float],
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, any]:
        """
        Process a complaint and assign to appropriate issue.
        Returns comprehensive result dictionary.
        """
        try:
            # Validate inputs
            validate_complaint_id(complaint_id)
            validate_category(category)
            validate_hostel(hostel)
            validate_embedding(embedding)
            
            timestamp = timestamp or datetime.utcnow()
            metadata = metadata or {}
            
            # Create complaint object
            complaint = Complaint(
                id=complaint_id,
                text=text,
                category=category,
                urgency=urgency,
                hostel=hostel,
                timestamp=timestamp,
                embedding=embedding,
                metadata=metadata
            )
            
            # Generate issue key (category + hostel) - ENFORCES BOTH
            issue_key = generate_issue_key(category, hostel)
            
            # Check if issue exists
            if issue_key in self.issue_key_index:
                # Add to existing issue
                issue_id = self.issue_key_index[issue_key]
                issue = self.issues[issue_id]
                
                # VERIFICATION: Issue must match complaint hostel and category
                if issue.hostel != hostel or issue.category != category:
                    # This should never happen due to issue_key logic
                    logger.error(f"Issue mismatch! Issue: {issue.hostel}/{issue.category}, Complaint: {hostel}/{category}")
                    raise ValueError("Issue-hostel-category mismatch")
                
                # Modified: get similarity score always
                is_new, duplicate_of, similarity_score = issue.add_complaint(complaint)
                
                logger.info(
                    f"Complaint {complaint_id} → Issue {issue_id} "
                    f"(hostel: {hostel}, category: {category}, "
                    f"duplicate: {duplicate_of is not None}, similarity: {similarity_score:.3f})"
                )
                
                result = {
                    "status": "added_to_existing",
                    "complaint_id": complaint_id,
                    "issue_id": issue_id,
                    "is_new_complaint": is_new,
                    "is_duplicate": duplicate_of is not None,
                    "duplicate_of": duplicate_of.id if duplicate_of else None,
                    "similarity_score": round(similarity_score, 4) if similarity_score is not None else None,
                    "complaint_count": issue.complaint_count,
                    "unique_complaint_count": issue.unique_complaint_count,
                    "urgency_max": issue.urgency_max,
                    "urgency_avg": round(issue.urgency_avg, 2)
                }
                
            else:
                # Create new issue
                issue_id = generate_issue_id(category, hostel)
                
                issue = Issue(
                    issue_id=issue_id,
                    category=category,
                    hostel=hostel,
                    duplicate_threshold=self.duplicate_threshold
                )
                
                # Add first complaint (always unique)
                is_new, duplicate_of, similarity_score = issue.add_complaint(complaint)
                
                # Register issue
                self.issues[issue_id] = issue
                self.issue_key_index[issue_key] = issue_id
                self.total_issues += 1
                
                logger.info(f"New issue created: {issue_id} (hostel: {hostel}, category: {category})")
                
                result = {
                    "status": "new_issue_created",
                    "complaint_id": complaint_id,
                    "issue_id": issue_id,
                    "is_new_complaint": True,
                    "is_duplicate": False,
                    "duplicate_of": None,
                    "similarity_score": round(similarity_score, 4) if similarity_score is not None else None,
                    "complaint_count": 1,
                    "unique_complaint_count": 1,
                    "urgency_max": urgency,
                    "urgency_avg": get_urgency_score(urgency)
                }
            
            self.total_complaints += 1
            
            # Add issue summary
            result["issue_summary"] = self.get_issue(issue_id).to_dict(summary=True)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to process complaint {complaint_id}: {str(e)}")
            raise
        
    def get_issue(self, issue_id: str) -> Optional[Issue]:
        """Get issue by ID"""
        return self.issues.get(issue_id)
    
    def get_issues(self, include_complaints: bool = False) -> List[Dict]:
        """Get all issues"""
        return [
            issue.to_dict(include_complaints=include_complaints, summary=not include_complaints)
            for issue in self.issues.values()
        ]
    
    def get_active_issues(self, limit: int = 50) -> List[Dict]:
        """Get active issues sorted by last updated"""
        sorted_issues = sorted(
            self.issues.values(),
            key=lambda x: x.last_updated,
            reverse=True
        )
        
        return [
            issue.to_dict(summary=True)
            for issue in sorted_issues[:limit]
        ]
    
    def get_issues_by_category(self, category: str) -> List[Dict]:
        """Get issues filtered by category"""
        filtered = [
            issue for issue in self.issues.values()
            if issue.category.lower() == category.lower()
        ]
        
        return [issue.to_dict(summary=True) for issue in filtered]
    
    def get_issues_by_hostel(self, hostel: str) -> List[Dict]:
        """Get issues filtered by hostel"""
        filtered = [
            issue for issue in self.issues.values()
            if issue.hostel.lower() == hostel.lower()
        ]
        
        return [issue.to_dict(summary=True) for issue in filtered]
    
    def get_issues_by_urgency(self, min_urgency: str = "MEDIUM") -> List[Dict]:
        """Get issues filtered by minimum urgency"""
        from app.issues.urgency_rules import get_urgency_score
        
        min_score = get_urgency_score(min_urgency)
        filtered = [
            issue for issue in self.issues.values()
            if get_urgency_score(issue.urgency_max) >= min_score
        ]
        
        return [issue.to_dict(summary=True) for issue in filtered]
    
    def get_duplicate_statistics(self) -> Dict:
        """Get detailed duplicate statistics"""
        duplicate_pairs = []
        similarity_scores = []
        
        for issue in self.issues.values():
            for complaint in issue.complaints:
                if complaint.is_duplicate and complaint.similarity_score:
                    duplicate_pairs.append({
                        "complaint_id": complaint.id,
                        "original_id": complaint.duplicate_of,
                        "similarity": complaint.similarity_score,
                        "issue_id": issue.issue_id
                    })
                    similarity_scores.append(complaint.similarity_score)
        
        return {
            "total_duplicate_pairs": len(duplicate_pairs),
            "average_similarity": round(sum(similarity_scores) / len(similarity_scores), 4) if similarity_scores else 0,
            "min_similarity": round(min(similarity_scores), 4) if similarity_scores else 0,
            "max_similarity": round(max(similarity_scores), 4) if similarity_scores else 0,
            "duplicate_pairs": duplicate_pairs[:20]  # Limit for response size
        }
    
    def get_statistics(self) -> Dict:
        """Get manager statistics"""
        categories = {}
        hostels = {}
        urgency_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        
        # Track potential issues
        cross_hostel_attempts = 0
        cross_category_attempts = 0
        
        for issue in self.issues.values():
            # Category stats
            cat = issue.category
            categories[cat] = categories.get(cat, 0) + issue.complaint_count
            
            # Hostel stats
            hostel = issue.hostel
            hostels[hostel] = hostels.get(hostel, 0) + issue.complaint_count
            
            # Urgency stats
            from app.issues.urgency_rules import get_urgency_label
            urgency_label = issue.urgency_max.upper()
            if urgency_label in urgency_counts:
                urgency_counts[urgency_label] += 1
            
            # Check for consistency
            for complaint in issue.complaints:
                if complaint.hostel != issue.hostel:
                    cross_hostel_attempts += 1
                    logger.warning(f"Cross-hostel complaint: {complaint.id} in issue {issue.issue_id}")
                if complaint.category != issue.category:
                    cross_category_attempts += 1
                    logger.warning(f"Cross-category complaint: {complaint.id} in issue {issue.issue_id}")
        
        unique_complaints = sum(issue.unique_complaint_count for issue in self.issues.values())
        duplicate_count = self.total_complaints - unique_complaints
        
        # Calculate average complaints per issue
        avg_complaints_per_issue = self.total_complaints / max(1, self.total_issues)
        
        return {
            "total_issues": self.total_issues,
            "total_complaints": self.total_complaints,
            "unique_complaints": unique_complaints,
            "duplicate_complaints": duplicate_count,
            "duplicate_rate": round(duplicate_count / max(1, self.total_complaints), 4),
            "avg_complaints_per_issue": round(avg_complaints_per_issue, 2),
            "categories": categories,
            "hostels": hostels,
            "urgency_distribution": urgency_counts,
            "issue_key_count": len(self.issue_key_index),
            "duplicate_threshold": self.duplicate_threshold,
            "consistency_checks": {
                "cross_hostel_attempts": cross_hostel_attempts,
                "cross_category_attempts": cross_category_attempts,
                "consistent": cross_hostel_attempts == 0 and cross_category_attempts == 0
            }
        }
    
    def get_complaint_timeline(self, hours: int = 24) -> List[Dict]:
        """Get complaints within last N hours"""
        cutoff = datetime.utcnow().timestamp() - (hours * 3600)
        
        timeline = []
        for issue in self.issues.values():
            for complaint in issue.complaints:
                if complaint.timestamp.timestamp() >= cutoff:
                    timeline.append({
                        "complaint_id": complaint.id,
                        "issue_id": issue.issue_id,
                        "category": issue.category,
                        "hostel": issue.hostel,
                        "urgency": complaint.urgency,
                        "timestamp": complaint.timestamp.isoformat(),
                        "is_duplicate": complaint.is_duplicate,
                        "similarity_score": complaint.similarity_score
                    })
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x["timestamp"], reverse=True)
        return timeline
    
    def find_similar_issues(self, issue_id: str, similarity_threshold: float = 0.7) -> List[Dict]:
        """Find issues similar to given issue (by category/urgency patterns)"""
        target_issue = self.get_issue(issue_id)
        if not target_issue:
            return []
        
        similar_issues = []
        for issue in self.issues.values():
            if issue.issue_id == issue_id:
                continue
            
            # Calculate similarity based on multiple factors
            similarity = 0.0
            
            # Category match
            if issue.category == target_issue.category:
                similarity += 0.3
            
            # Urgency similarity
            from app.issues.urgency_rules import get_urgency_score
            urgency_diff = abs(get_urgency_score(issue.urgency_max) - get_urgency_score(target_issue.urgency_max))
            similarity += max(0, 0.3 - (urgency_diff * 0.1))
            
            # Hostel similarity (same hostel block?)
            if issue.hostel.split('-')[0] == target_issue.hostel.split('-')[0]:
                similarity += 0.2
            
            # Time proximity (issues created around same time)
            time_diff = abs((issue.created_at - target_issue.created_at).total_seconds() / 3600)
            if time_diff < 24:  # Within 24 hours
                similarity += max(0, 0.2 - (time_diff / 120))
            
            if similarity >= similarity_threshold:
                similar_issues.append({
                    "issue_id": issue.issue_id,
                    "category": issue.category,
                    "hostel": issue.hostel,
                    "similarity_score": round(similarity, 3),
                    "urgency_max": issue.urgency_max,
                    "complaint_count": issue.complaint_count
                })
        
        # Sort by similarity
        similar_issues.sort(key=lambda x: x["similarity_score"], reverse=True)
        return similar_issues
    
    def reset(self) -> None:
        """Reset all issues (for testing)"""
        self.issues.clear()
        self.issue_key_index.clear()
        self.total_complaints = 0
        self.total_issues = 0
        logger.info("IssueManager reset")
    
    def export_issues(self, include_embeddings: bool = False) -> List[Dict]:
        """Export all issues for backup/analysis"""
        exported = []
        for issue in self.issues.values():
            issue_data = issue.to_dict(include_complaints=True)
            
            if not include_embeddings:
                # Remove embeddings to reduce size
                for complaint in issue_data.get("complaints", []):
                    if "embedding" in complaint:
                        del complaint["embedding"]
                    if "embedding_length" in complaint:
                        complaint["embedding_length"] = 512  # Keep length info
            
            exported.append(issue_data)
        
        return exported


# Singleton instance
_issue_manager_instance = None

def get_issue_manager() -> IssueManager:
    """Get singleton IssueManager instance"""
    global _issue_manager_instance
    if _issue_manager_instance is None:
        _issue_manager_instance = IssueManager()
    return _issue_manager_instance