#!/usr/bin/env python3
"""
Enhanced Issue Service - Day 6 Integration
Adds: DB persistence, session tracking, heuristics
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
import uuid

from app.preprocessing.text_cleaner import preprocess_text
from app.services.classification_service import get_classification_service
from app.services.embedding_service import get_embedding_service
from app.core.session import get_session_manager
from app.core.heuristics import HeuristicEngine
from app.db.session import get_db_context
from app.db.models.issue import IssueModel, IssueStatus
from app.db.models.complaint import ComplaintModel
from app.repositories.issue_repository import IssueRepository
from app.repositories.complaint_repository import ComplaintRepository
from app.issues.issue_id import generate_issue_id, generate_issue_key
from app.issues.urgency_rules import get_urgency_score
from app.utils.logger import get_logger

logger = get_logger(__name__)


class IssueServiceDay6:
    """
    Enhanced Issue Service with Day 6 features:
    - Database persistence
    - Session tracking
    - Heuristic evaluation
    """

    def __init__(self):
        self.classifier = get_classification_service()
        self.embedding_service = get_embedding_service()
        self.session_manager = get_session_manager()
        self.heuristic_engine = HeuristicEngine()
        
        logger.info("IssueServiceDay6 initialized with DB persistence")

    def process_complaint(
        self,
        text: str,
        hostel: str,
        complaint_id: Optional[str] = None,
        session_id: Optional[str] = None,
        session_metadata: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete pipeline with Day 6 enhancements:
        1. Session management
        2. Classification & embedding
        3. Issue aggregation (DB-backed)
        4. Heuristic evaluation
        5. Persistence
        """
        start_time = datetime.utcnow()
        
        try:
            # Generate complaint ID if not provided
            complaint_id = complaint_id or f"COMP-{uuid.uuid4().hex[:8]}"
            metadata = metadata or {}
            
            logger.info(f"Processing complaint: {complaint_id}")
            
            # ----------------------------------
            # 1️⃣ Session Management (Day 6.2)
            # ----------------------------------
            session = None
            if session_id:
                session = self.session_manager.get_session(session_id)
            
            if not session:
                session = self.session_manager.create_session(
                    metadata=session_metadata or {}
                )
            
            session_id = session.session_id
            
            # Check session complaint limit
            if not session.can_submit_complaint():
                return {
                    "success": False,
                    "error": "Session complaint limit exceeded",
                    "session_id": session_id,
                    "processing_time_seconds": (datetime.utcnow() - start_time).total_seconds()
                }
            
            # ----------------------------------
            # 2️⃣ Classification (Day 3 + Day 4)
            # ----------------------------------
            classification = self.classifier.classify_with_urgency(text, detailed=False)
            
            if "error" in classification:
                raise ValueError(f"Classification failed: {classification['error']}")
            
            category = classification["category"]
            urgency = classification["urgency"]
            response_time = classification.get("response_time_hours", 24)
            
            # ----------------------------------
            # 3️⃣ Embedding (Day 2)
            # ----------------------------------
            clean_text = preprocess_text(text, normalize_hinglish=False)
            embedding = self.embedding_service.generate_embedding(
                clean_text,
                normalize_hinglish=False
            )
            
            # ----------------------------------
            # 4️⃣ Issue Aggregation + DB Persistence
            # ----------------------------------
            with get_db_context() as db:
                issue_repo = IssueRepository(db)
                complaint_repo = ComplaintRepository(db)
                
                # Find or create issue
                issue_key = generate_issue_key(category, hostel)
                issue = issue_repo.get_by_hostel_category(hostel, category)
                
                if not issue:
                    # Create new issue
                    issue_id = generate_issue_id(category, hostel)
                    issue = issue_repo.create({
                        "id": issue_id,
                        "hostel": hostel,
                        "category": category,
                        "status": IssueStatus.OPEN,
                        "urgency_max": urgency,
                        "urgency_avg": get_urgency_score(urgency),
                        "complaint_count": 0,
                        "unique_complaint_count": 0,
                        "duplicate_count": 0
                    })
                    is_new_issue = True
                else:
                    is_new_issue = False
                
                # Detect duplicates
                is_duplicate, similarity_score = self._check_duplicate(
                    issue.id, embedding, complaint_repo
                )
                
                # Create complaint record
                complaint_data = {
                    "id": complaint_id,
                    "issue_id": issue.id,
                    "text": text,
                    "category": category,
                    "urgency": urgency,
                    "hostel": hostel,
                    "similarity_score": similarity_score,
                    "is_duplicate": is_duplicate,
                    "duplicate_of": None,  # Could enhance this
                    "session_id": session_id,
                    "extra_metadata": metadata  # Renamed field
                }
                
                complaint = complaint_repo.create(complaint_data)
                
                # Update issue statistics
                all_complaints = complaint_repo.get_by_issue(issue.id)
                urgency_scores = [get_urgency_score(c.urgency) for c in all_complaints]
                max_urgency_score = max(urgency_scores)
                avg_urgency_score = sum(urgency_scores) / len(urgency_scores)
                
                urgency_map = {1: "Low", 2: "Medium", 3: "High", 4: "Critical"}
                max_urgency_label = urgency_map.get(max_urgency_score, "Low")
                
                issue_repo.increment_counts(
                    issue,
                    is_duplicate,
                    max_urgency_label,
                    avg_urgency_score
                )
                
                # ----------------------------------
                # 5️⃣ Session Update (After Success)
                # ----------------------------------
                self.session_manager.register_complaint(
                    session_id=session_id,
                    complaint_id=complaint_id,
                    issue_id=issue.id,
                    category=category,
                    urgency=urgency,
                    similarity_score=similarity_score,
                    is_duplicate=is_duplicate
                )
                
                # ----------------------------------
                # 6️⃣ Heuristic Evaluation (Day 6.3)
                # ----------------------------------
                try:
                    heuristics = self.heuristic_engine.evaluate(
                        session=session,
                        current_issue_id=issue.id,
                        current_urgency=urgency,
                        is_duplicate=is_duplicate,
                        similarity_score=similarity_score,
                        timestamp=start_time
                    )
                except Exception as e:
                    logger.error(f"Heuristic evaluation failed: {str(e)}")
                    heuristics = {
                        "is_follow_up": False,
                        "is_escalation": False,
                        "possible_noise": False,
                        "details": {},
                        "error": str(e)
                    }
                
                # ----------------------------------
                # 7️⃣ Build Response
                # ----------------------------------
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                
                response = {
                    "success": True,
                    "processing_time_seconds": round(processing_time, 3),
                    "complaint_id": complaint_id,
                    "text_preview": text[:100] + "..." if len(text) > 100 else text,
                    "classification": {
                        "category": category,
                        "category_confidence": classification.get("category_confidence", 0.0),
                        "urgency": urgency,
                        "urgency_confidence": classification.get("urgency_confidence", 0.0),
                        "response_time_hours": response_time
                    },
                    "issue_aggregation": {
                        "status": "new_issue_created" if is_new_issue else "added_to_existing",
                        "issue_id": issue.id,
                        "is_new_complaint": not is_duplicate,
                        "is_duplicate": is_duplicate,
                        "similarity_score": round(similarity_score, 4) if similarity_score else None,
                        "complaint_count": issue.complaint_count,
                        "unique_complaint_count": issue.unique_complaint_count,
                        "urgency_max": issue.urgency_max,
                        "urgency_avg": round(issue.urgency_avg, 2)
                    },
                    "session": {
                        "session_id": session_id,
                        "complaints_in_session": len(session.entries)
                    },
                    "heuristics": heuristics,
                    "metadata": {
                        "text_length": len(text),
                        "hostel": hostel,
                        "timestamp": start_time.isoformat(),
                        "db_persisted": True,
                        **metadata
                    }
                }
                
                logger.info(
                    f"Complaint processed: {complaint_id} → "
                    f"Issue: {issue.id}, Duplicate: {is_duplicate}, "
                    f"Follow-up: {heuristics.get('is_follow_up', False)}"
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
    
    def _check_duplicate(
        self,
        issue_id: str,
        embedding: List[float],
        complaint_repo: ComplaintRepository,
        threshold: float = 0.88
    ) -> tuple:
        """Check if complaint is duplicate within issue"""
        from app.issues.similarity import cosine_similarity
        
        # Get existing complaints for this issue
        existing_complaints = complaint_repo.get_by_issue(issue_id)
        
        if not existing_complaints:
            return False, 0.0
        
        # For now, we don't have embeddings stored
        # In production, you'd store and compare embeddings
        # This is a simplified version
        
        # Return not duplicate for now
        return False, 0.0
    
    def get_issue(self, issue_id: str) -> Optional[Dict]:
        """Get issue by ID"""
        with get_db_context() as db:
            issue_repo = IssueRepository(db)
            issue = issue_repo.get_by_id(issue_id)
            
            if not issue:
                return None
            
            return issue.to_dict(include_complaints=True)
    
    def get_issues(
        self,
        status: Optional[str] = None,
        hostel: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 50
    ) -> Dict:
        """Get issues with filters"""
        with get_db_context() as db:
            issue_repo = IssueRepository(db)
            
            status_enum = None
            if status:
                try:
                    status_enum = IssueStatus[status.upper()]
                except KeyError:
                    pass
            
            issues = issue_repo.get_all(
                status=status_enum,
                hostel=hostel,
                category=category,
                limit=limit
            )
            
            return {
                "issues": [issue.to_dict(summary=True) for issue in issues],
                "count": len(issues)
            }
    
    def update_issue_status(
        self,
        issue_id: str,
        status: str
    ) -> Optional[Dict]:
        """Update issue status (admin action)"""
        with get_db_context() as db:
            issue_repo = IssueRepository(db)
            
            try:
                status_enum = IssueStatus[status.upper()]
            except KeyError:
                raise ValueError(f"Invalid status: {status}")
            
            issue = issue_repo.update_status(issue_id, status_enum)
            
            if not issue:
                return None
            
            logger.info(f"Issue {issue_id} status updated to {status}")
            return issue.to_dict(summary=True)
    
    def get_system_stats(self) -> Dict:
        """Get comprehensive system statistics"""
        with get_db_context() as db:
            issue_repo = IssueRepository(db)
            complaint_repo = ComplaintRepository(db)
            
            issue_stats = issue_repo.get_statistics()
            complaint_stats = complaint_repo.get_statistics()
            session_stats = self.session_manager.get_stats()
            
            return {
                "issue_system": issue_stats,
                "complaint_system": complaint_stats,
                "session_system": session_stats,
                "classification_system": self.classifier.get_classification_stats(),
                "embedding_system": self.embedding_service.get_embedding_info(),
                "day_6_complete": True,
                "timestamp": datetime.utcnow().isoformat()
            }


# Singleton instance
_issue_service_day6_instance = None


def get_issue_service_day6() -> IssueServiceDay6:
    """Get singleton IssueServiceDay6 instance"""
    global _issue_service_day6_instance
    if _issue_service_day6_instance is None:
        _issue_service_day6_instance = IssueServiceDay6()
    return _issue_service_day6_instance