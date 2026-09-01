import asyncio
from abc import ABC, abstractmethod
from typing import Callable, Any, Coroutine


class JobQueue(ABC):
    @abstractmethod
    def enqueue(self, task_func: Callable[..., Coroutine[Any, Any, None]], *args: Any, **kwargs: Any) -> None:
        """Enqueues an asynchronous background job."""
        pass


class LocalBackgroundQueue(JobQueue):
    """
    In-process asynchronous job queue using asyncio.create_task.
    Enables background execution in development and test environments without Redis.
    """
    def enqueue(self, task_func: Callable[..., Coroutine[Any, Any, None]], *args: Any, **kwargs: Any) -> None:
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(task_func(*args, **kwargs))
        except RuntimeError:
            # If no running loop, create and run in thread or new loop
            asyncio.run(task_func(*args, **kwargs))


class CeleryQueue(JobQueue):
    """
    Celery queue adapter for production Redis/RabbitMQ deployment.
    """
    def enqueue(self, task_func: Callable[..., Coroutine[Any, Any, None]], *args: Any, **kwargs: Any) -> None:
        # Placeholder for Celery task invocation
        # E.g. run_verification_celery.delay(*args, **kwargs)
        LocalBackgroundQueue().enqueue(task_func, *args, **kwargs)


def get_job_queue(queue_mode: str = "local") -> JobQueue:
    if queue_mode.lower() == "celery":
        return CeleryQueue()
    return LocalBackgroundQueue()
