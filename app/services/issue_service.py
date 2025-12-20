#!/usr/bin/env python3
"""
Issue Service - Thin orchestration layer
Day 5.4
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
import uuid

from app.preprocessing.text_cleaner import preprocess_text  # ADDED
from app.services.classification_service import get_classification_service
from app.services.embedding_service import get_embedding_service
from app.issues.issue_manager import get_issue_manager
from app.utils.logger import get_logger

logger = get_logger(__name__)


class IssueService:
    """
    Orchestrates the complete complaint processing pipeline.
    Thin layer - no business logic here.
    """
    
    def __init__(self):
        self.classifier = get_classification_service()
        self.embedding_service = get_embedding_service()
        self.issue_manager = get_issue_manager()
        
        logger.info("IssueService initialized")
    
    def process_complaint(
        self,
        text: str,
        hostel: str,
        complaint_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete pipeline: Classify → Embed → Group → Return result
        """
        start_time = datetime.utcnow()
        
        try:
            # Generate complaint ID if not provided
            complaint_id = complaint_id or f"COMP-{uuid.uuid4().hex[:8]}"
            metadata = metadata or {}
            
            logger.info(f"Processing complaint: {complaint_id[:20]}...")
            
            # 1️⃣ Classification (Day 3 + Day 4) - Use ORIGINAL text
            classification = self.classifier.classify_with_urgency(text, detailed=False)
            
            if "error" in classification:
                raise ValueError(f"Classification failed: {classification['error']}")
            
            category = classification["category"]
            urgency = classification["urgency"]
            response_time = classification.get("response_time_hours", 24)
            confidence = classification.get("category_confidence", 0.0)
            
            # 2️⃣ Embedding (Day 2) - Use PREPROCESSED text
            clean_text = preprocess_text(text, normalize_hinglish=True)
            
            # Generate embedding with preprocessing already applied
            embedding = self.embedding_service.generate_embedding(
                clean_text,
                normalize_hinglish=False  # Already normalized
            )
            
            # 3️⃣ Issue Management (Day 5)
            issue_result = self.issue_manager.process_complaint(
                complaint_id=complaint_id,
                text=text,  # Keep original text for display
                category=category,
                urgency=urgency,
                hostel=hostel,
                embedding=embedding,
                timestamp=start_time,
                metadata=metadata
            )
            
            # 4️⃣ Assemble final response
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            response = {
                "success": True,
                "processing_time_seconds": round(processing_time, 3),
                "complaint_id": complaint_id,
                "text_preview": text[:100] + "..." if len(text) > 100 else text,
                "classification": {
                    "category": category,
                    "category_confidence": round(confidence, 4),
                    "urgency": urgency,
                    "urgency_confidence": classification.get("urgency_confidence", 0.0),
                    "response_time_hours": response_time
                },
                "issue_aggregation": issue_result,
                "metadata": {
                    "text_length": len(text),
                    "hostel": hostel,
                    "timestamp": start_time.isoformat(),
                    **metadata
                }
            }
            
            logger.info(
                f"Complaint processed: {complaint_id} → "
                f"Category: {category}, Urgency: {urgency}, "
                f"Issue: {issue_result.get('issue_id', 'N/A')}, "
                f"Duplicate: {issue_result.get('is_duplicate', False)}"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to process complaint: {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "complaint_id": complaint_id,
                "text_preview": text[:100] + "..." if len(text) > 100 else text,
                "processing_time_seconds": round((datetime.utcnow() - start_time).total_seconds(), 3)
            }
    
    def batch_process_complaints(
        self,
        complaints: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Process multiple complaints.
        """
        results = []
        
        for complaint in complaints:
            result = self.process_complaint(
                text=complaint.get("text", ""),
                hostel=complaint.get("hostel", "UNKNOWN"),
                complaint_id=complaint.get("complaint_id"),
                metadata=complaint.get("metadata", {})
            )
            results.append(result)
        
        return results
    
    def get_issues(self, include_complaints: bool = False) -> Dict[str, Any]:
        """Get all issues with optional complaint details"""
        issues = self.issue_manager.get_issues(include_complaints=include_complaints)
        stats = self.issue_manager.get_statistics()
        
        return {
            "issues": issues,
            "statistics": stats,
            "count": len(issues)
        }
    
    def get_issue_details(self, issue_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific issue"""
        issue = self.issue_manager.get_issue(issue_id)
        
        if not issue:
            return None
        
        return issue.to_dict(include_complaints=True)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        issue_stats = self.issue_manager.get_statistics()
        
        return {
            "issue_system": issue_stats,
            "classification_system": self.classifier.get_classification_stats(),
            "embedding_system": self.embedding_service.get_embedding_info(),
            "day_5_complete": True,
            "timestamp": datetime.utcnow().isoformat()
        }


# Singleton instance
_issue_service_instance = None

def get_issue_service() -> IssueService:
    """Get singleton IssueService instance"""
    global _issue_service_instance
    if _issue_service_instance is None:
        _issue_service_instance = IssueService()
    return _issue_service_instance