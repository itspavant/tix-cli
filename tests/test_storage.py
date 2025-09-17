import pytest
import tempfile
from pathlib import Path
from tix.storage.json_storage import TaskStorage


@pytest.fixture
def temp_storage():
    """Create temporary storage for tests"""
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        storage_path = Path(f.name)
    storage = TaskStorage(storage_path)
    yield storage
    storage_path.unlink()  # Clean up


def test_add_task(temp_storage):
    """Test adding a task"""
    task = temp_storage.add_task("Test task", "high", ["work"])
    assert task.id == 1
    assert task.text == "Test task"
    assert task.priority == "high"
    assert "work" in task.tags


def test_get_task(temp_storage):
    """Test retrieving a task"""
    task = temp_storage.add_task("Test")
    retrieved = temp_storage.get_task(task.id)
    assert retrieved.id == task.id
    assert retrieved.text == "Test"


def test_delete_task(temp_storage):
    """Test deleting a task"""
    task = temp_storage.add_task("To delete")
    assert temp_storage.delete_task(task.id) == True
    assert temp_storage.get_task(task.id) is None


def test_update_task(temp_storage):
    """Test updating a task"""
    task = temp_storage.add_task("Original")
    task.text = "Updated"
    temp_storage.update_task(task)

    retrieved = temp_storage.get_task(task.id)
    assert retrieved.text == "Updated"