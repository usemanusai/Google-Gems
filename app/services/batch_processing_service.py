"""
Batch Processing Service

Handles large-scale knowledge source processing with progress tracking,
queue management, and parallel processing capabilities.
"""

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from loguru import logger

from models.knowledge_source import KnowledgeSource, SourceStatus
from services.rag_service import RAGService


class BatchJobStatus(str, Enum):
    """Status of batch processing jobs."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BatchJob:
    """Represents a batch processing job."""
    id: str
    source: KnowledgeSource
    status: BatchJobStatus = BatchJobStatus.PENDING
    progress: float = 0.0
    error_message: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None


class BatchProcessingWorker(QThread):
    """Worker thread for batch processing."""
    
    # Signals
    job_started = pyqtSignal(str)  # job_id
    job_progress = pyqtSignal(str, float)  # job_id, progress
    job_completed = pyqtSignal(str, bool)  # job_id, success
    batch_progress = pyqtSignal(int, int)  # completed, total
    
    def __init__(self, rag_service: RAGService, max_workers: int = 3):
        super().__init__()
        self.rag_service = rag_service
        self.max_workers = max_workers
        self.jobs: List[BatchJob] = []
        self.is_running = False
        self.should_stop = False
    
    def add_job(self, job: BatchJob):
        """Add a job to the processing queue."""
        self.jobs.append(job)
        logger.info(f"Added batch job: {job.id}")
    
    def add_jobs(self, jobs: List[BatchJob]):
        """Add multiple jobs to the processing queue."""
        self.jobs.extend(jobs)
        logger.info(f"Added {len(jobs)} batch jobs")
    
    def stop_processing(self):
        """Stop the batch processing."""
        self.should_stop = True
        logger.info("Batch processing stop requested")
    
    def run(self):
        """Run the batch processing."""
        if not self.jobs:
            logger.warning("No jobs to process")
            return
        
        self.is_running = True
        self.should_stop = False
        
        logger.info(f"Starting batch processing of {len(self.jobs)} jobs with {self.max_workers} workers")
        
        try:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all jobs
                future_to_job = {
                    executor.submit(self._process_job, job): job 
                    for job in self.jobs
                }
                
                completed_count = 0
                total_count = len(self.jobs)
                
                # Process completed jobs
                for future in as_completed(future_to_job):
                    if self.should_stop:
                        # Cancel remaining jobs
                        for f in future_to_job:
                            f.cancel()
                        break
                    
                    job = future_to_job[future]
                    
                    try:
                        success = future.result()
                        job.status = BatchJobStatus.COMPLETED if success else BatchJobStatus.FAILED
                        self.job_completed.emit(job.id, success)
                        
                    except Exception as e:
                        job.status = BatchJobStatus.FAILED
                        job.error_message = str(e)
                        self.job_completed.emit(job.id, False)
                        logger.error(f"Job {job.id} failed: {e}")
                    
                    completed_count += 1
                    self.batch_progress.emit(completed_count, total_count)
                
                if self.should_stop:
                    logger.info("Batch processing stopped by user")
                else:
                    logger.info(f"Batch processing completed: {completed_count}/{total_count} jobs")
        
        except Exception as e:
            logger.error(f"Batch processing error: {e}")
        
        finally:
            self.is_running = False
    
    def _process_job(self, job: BatchJob) -> bool:
        """Process a single job."""
        try:
            import time
            
            job.status = BatchJobStatus.RUNNING
            job.start_time = time.time()
            
            self.job_started.emit(job.id)
            logger.info(f"Processing job: {job.id} ({job.source.get_display_name()})")
            
            # Simulate progress updates
            for progress in [0.1, 0.3, 0.5, 0.7, 0.9]:
                if self.should_stop:
                    job.status = BatchJobStatus.CANCELLED
                    return False
                
                job.progress = progress
                self.job_progress.emit(job.id, progress)
                time.sleep(0.1)  # Small delay for progress visualization
            
            # Process the knowledge source
            success = self.rag_service.process_knowledge_source(job.source)
            
            job.progress = 1.0
            job.end_time = time.time()
            
            self.job_progress.emit(job.id, 1.0)
            
            if success:
                logger.info(f"Job completed successfully: {job.id}")
            else:
                logger.error(f"Job failed: {job.id}")
                job.error_message = "Processing failed"
            
            return success
            
        except Exception as e:
            job.status = BatchJobStatus.FAILED
            job.error_message = str(e)
            job.end_time = time.time()
            logger.error(f"Job {job.id} failed with exception: {e}")
            return False


class BatchProcessingService(QObject):
    """Service for managing batch processing operations."""
    
    # Signals
    batch_started = pyqtSignal(int)  # total_jobs
    batch_completed = pyqtSignal(int, int)  # successful, total
    job_status_changed = pyqtSignal(str, str)  # job_id, status
    
    def __init__(self, rag_service: RAGService):
        super().__init__()
        self.rag_service = rag_service
        self.worker = None
        self.current_jobs: Dict[str, BatchJob] = {}
        self.max_workers = 3
    
    def set_max_workers(self, max_workers: int):
        """Set the maximum number of worker threads."""
        self.max_workers = max_workers
        logger.info(f"Set max workers to: {max_workers}")
    
    def process_sources_batch(self, sources: List[KnowledgeSource]) -> bool:
        """Process multiple knowledge sources in batch."""
        if self.is_processing():
            logger.warning("Batch processing already in progress")
            return False
        
        if not sources:
            logger.warning("No sources to process")
            return False
        
        try:
            # Create jobs
            jobs = []
            for i, source in enumerate(sources):
                job = BatchJob(
                    id=f"batch_job_{i}_{source.id}",
                    source=source
                )
                jobs.append(job)
                self.current_jobs[job.id] = job
            
            # Create and start worker
            self.worker = BatchProcessingWorker(self.rag_service, self.max_workers)
            
            # Connect signals
            self.worker.job_started.connect(self._on_job_started)
            self.worker.job_progress.connect(self._on_job_progress)
            self.worker.job_completed.connect(self._on_job_completed)
            self.worker.batch_progress.connect(self._on_batch_progress)
            self.worker.finished.connect(self._on_batch_finished)
            
            # Add jobs and start
            self.worker.add_jobs(jobs)
            self.worker.start()
            
            self.batch_started.emit(len(jobs))
            logger.info(f"Started batch processing of {len(jobs)} sources")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start batch processing: {e}")
            return False
    
    def stop_batch_processing(self):
        """Stop the current batch processing."""
        if self.worker and self.worker.is_running:
            self.worker.stop_processing()
            logger.info("Stopping batch processing...")
    
    def is_processing(self) -> bool:
        """Check if batch processing is currently running."""
        return self.worker is not None and self.worker.is_running
    
    def get_job_status(self, job_id: str) -> Optional[BatchJob]:
        """Get the status of a specific job."""
        return self.current_jobs.get(job_id)
    
    def get_all_jobs(self) -> List[BatchJob]:
        """Get all current jobs."""
        return list(self.current_jobs.values())
    
    def clear_completed_jobs(self):
        """Clear completed jobs from memory."""
        completed_jobs = [
            job_id for job_id, job in self.current_jobs.items()
            if job.status in [BatchJobStatus.COMPLETED, BatchJobStatus.FAILED, BatchJobStatus.CANCELLED]
        ]
        
        for job_id in completed_jobs:
            del self.current_jobs[job_id]
        
        logger.info(f"Cleared {len(completed_jobs)} completed jobs")
    
    def _on_job_started(self, job_id: str):
        """Handle job started signal."""
        if job_id in self.current_jobs:
            self.current_jobs[job_id].status = BatchJobStatus.RUNNING
            self.job_status_changed.emit(job_id, BatchJobStatus.RUNNING.value)
    
    def _on_job_progress(self, job_id: str, progress: float):
        """Handle job progress signal."""
        if job_id in self.current_jobs:
            self.current_jobs[job_id].progress = progress
    
    def _on_job_completed(self, job_id: str, success: bool):
        """Handle job completed signal."""
        if job_id in self.current_jobs:
            status = BatchJobStatus.COMPLETED if success else BatchJobStatus.FAILED
            self.current_jobs[job_id].status = status
            self.job_status_changed.emit(job_id, status.value)
    
    def _on_batch_progress(self, completed: int, total: int):
        """Handle batch progress signal."""
        logger.debug(f"Batch progress: {completed}/{total}")
    
    def _on_batch_finished(self):
        """Handle batch processing finished."""
        successful = sum(1 for job in self.current_jobs.values() if job.status == BatchJobStatus.COMPLETED)
        total = len(self.current_jobs)
        
        self.batch_completed.emit(successful, total)
        logger.info(f"Batch processing finished: {successful}/{total} successful")
        
        # Clean up worker
        if self.worker:
            self.worker.deleteLater()
            self.worker = None
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get statistics about current processing."""
        if not self.current_jobs:
            return {"total": 0, "status_counts": {}}
        
        status_counts = {}
        for job in self.current_jobs.values():
            status = job.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total": len(self.current_jobs),
            "status_counts": status_counts,
            "is_processing": self.is_processing()
        }
