import threading
import uuid
import time
import logging

class JobManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(JobManager, cls).__new__(cls)
                cls._instance.jobs = {}
        return cls._instance

    def submit_job(self, task_func, *args, **kwargs):
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {
            "status": "running",
            "progress": 0.0,
            "message": "Initializing...",
            "result": None,
            "error": None,
            "start_time": time.time(),
            "updated_at": time.time()
        }

        def worker():
            try:
                def updater(progress, message=""):
                    self.update_job(job_id, progress=progress, message=message)
                
                # Pass updater to the task function so it can report progress
                result = task_func(updater, *args, **kwargs)
                
                with self._lock:
                    self.jobs[job_id]["status"] = "completed"
                    self.jobs[job_id]["progress"] = 1.0
                    self.jobs[job_id]["message"] = "Job completed successfully."
                    self.jobs[job_id]["result"] = result
                    self.jobs[job_id]["updated_at"] = time.time()
            except Exception as e:
                logging.exception(f"Job {job_id} failed.")
                with self._lock:
                    self.jobs[job_id]["status"] = "error"
                    self.jobs[job_id]["error"] = str(e)
                    self.jobs[job_id]["message"] = f"Error: {str(e)}"
                    self.jobs[job_id]["updated_at"] = time.time()

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        return job_id

    def update_job(self, job_id, progress=None, message=None):
        with self._lock:
            if job_id in self.jobs:
                if progress is not None:
                    self.jobs[job_id]["progress"] = progress
                if message is not None:
                    self.jobs[job_id]["message"] = message
                self.jobs[job_id]["updated_at"] = time.time()

    def get_job(self, job_id):
        with self._lock:
            return self.jobs.get(job_id, None)

    def cancel_job(self, job_id):
        # Cancellation isn't strictly implemented for threads safely in Python
        # without custom events, but we can set status to cancelled and let 
        # the task check it if we implemented it.
        with self._lock:
            if job_id in self.jobs and self.jobs[job_id]["status"] == "running":
                self.jobs[job_id]["status"] = "error"
                self.jobs[job_id]["error"] = "Job cancelled by user."
                self.jobs[job_id]["message"] = "Cancelled"

# Singleton instance
manager = JobManager()
