"""Unit tests for background worker thread pool and async_tasks utility."""

from unittest.mock import MagicMock

from src.wellcare.utils.async_tasks import run_async


class TestAsyncTasks:
    """Test suite for non-blocking background task utility."""

    def test_run_async_success_execution(self) -> None:
        def task_fn(a: int, b: int) -> int:
            return a + b

        success_mock = MagicMock()
        error_mock = MagicMock()

        run_async(task_fn, 10, 25, on_success=success_mock, on_error=error_mock)

        success_mock.assert_called_once_with(35)
        error_mock.assert_not_called()

    def test_run_async_error_handling(self) -> None:
        def failing_task() -> None:
            raise ValueError("Computation failed")

        success_mock = MagicMock()
        error_mock = MagicMock()

        run_async(failing_task, on_success=success_mock, on_error=error_mock)

        success_mock.assert_not_called()
        error_mock.assert_called_once()
        assert isinstance(error_mock.call_args[0][0], ValueError)

    def test_run_async_with_master_widget_dispatch(self) -> None:
        mock_widget = MagicMock()
        success_mock = MagicMock()

        def slow_math(val: int) -> int:
            return val * 2

        run_async(slow_math, 21, on_success=success_mock, master_widget=mock_widget)

        # Under pytest, runs directly
        success_mock.assert_called_once_with(42)
