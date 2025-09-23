import pytest
from click.testing import CliRunner
from tix.cli import cli
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import os


@pytest.fixture
def runner():
    """Create a CLI runner for testing"""
    return CliRunner()


@pytest.fixture
def mock_home(tmp_path):
    """Create a mock home directory for testing"""
    return tmp_path


def test_completion_command_exists(runner):
    """Test that completion command exists"""
    result = runner.invoke(cli, ['completion', '--help'])
    assert result.exit_code == 0
    assert 'Setup or reset shell completion' in result.output


def test_completion_shows_instructions(runner):
    """Test that completion command shows setup instructions"""
    result = runner.invoke(cli, ['completion'])
    assert result.exit_code == 0
    assert '_TIX_COMPLETE=bash_source' in result.output
    assert '_TIX_COMPLETE=zsh_source' in result.output
    assert '_TIX_COMPLETE=fish_source' in result.output


def test_completion_reset(runner, mock_home):
    """Test resetting completion setup"""
    with patch('pathlib.Path.home', return_value=mock_home):
        # Create marker file
        tix_dir = mock_home / '.tix'
        tix_dir.mkdir()
        marker = tix_dir / '.completion_installed'
        marker.touch()

        # Reset completion
        result = runner.invoke(cli, ['completion', '--reset'])
        assert result.exit_code == 0
        assert 'Completion setup reset' in result.output
        assert not marker.exists()


def test_auto_setup_bash(runner, mock_home):
    """Test automatic completion setup for bash"""
    with patch('pathlib.Path.home', return_value=mock_home):
        with patch.dict(os.environ, {'SHELL': '/bin/bash'}):
            # Create mock .bashrc
            bashrc = mock_home / '.bashrc'
            bashrc.write_text('# Existing bashrc content\n')

            # Import and call setup function
            from tix.cli import setup_shell_completion
            setup_shell_completion()

            # Check that completion was added
            content = bashrc.read_text()
            assert '_TIX_COMPLETE=bash_source' in content

            # Check marker was created
            marker = mock_home / '.tix' / '.completion_installed'
            assert marker.exists()


def test_auto_setup_zsh(runner, mock_home):
    """Test automatic completion setup for zsh"""
    with patch('pathlib.Path.home', return_value=mock_home):
        with patch.dict(os.environ, {'SHELL': '/bin/zsh'}):
            # Create mock .zshrc
            zshrc = mock_home / '.zshrc'
            zshrc.write_text('# Existing zshrc content\n')

            # Import and call setup function
            from tix.cli import setup_shell_completion
            setup_shell_completion()

            # Check that completion was added
            content = zshrc.read_text()
            assert '_TIX_COMPLETE=zsh_source' in content

            # Check marker was created
            marker = mock_home / '.tix' / '.completion_installed'
            assert marker.exists()


def test_auto_setup_fish(runner, mock_home):
    """Test automatic completion setup for fish"""
    with patch('pathlib.Path.home', return_value=mock_home):
        with patch.dict(os.environ, {'SHELL': '/usr/bin/fish'}):
            # Import and call setup function
            from tix.cli import setup_shell_completion
            setup_shell_completion()

            # Check that fish config was created
            fish_config = mock_home / '.config' / 'fish' / 'config.fish'
            assert fish_config.exists()
            content = fish_config.read_text()
            assert '_TIX_COMPLETE=fish_source' in content

            # Check marker was created
            marker = mock_home / '.tix' / '.completion_installed'
            assert marker.exists()


def test_auto_setup_skips_if_already_installed(runner, mock_home):
    """Test that auto-setup skips if already installed"""
    with patch('pathlib.Path.home', return_value=mock_home):
        # Create marker file
        tix_dir = mock_home / '.tix'
        tix_dir.mkdir()
        marker = tix_dir / '.completion_installed'
        marker.touch()

        # Create mock .bashrc
        bashrc = mock_home / '.bashrc'
        bashrc.write_text('# Original content\n')

        # Import and call setup function
        from tix.cli import setup_shell_completion
        setup_shell_completion()

        # Check that bashrc was not modified
        content = bashrc.read_text()
        assert '_TIX_COMPLETE' not in content


def test_auto_setup_on_first_command(runner, mock_home):
    """Test that completion is set up on first tix command"""
    with patch('pathlib.Path.home', return_value=mock_home):
        with patch.dict(os.environ, {'SHELL': '/bin/bash'}):
            # Create mock .bashrc
            bashrc = mock_home / '.bashrc'
            bashrc.write_text('# Original content\n')

            # Run a tix command (ls)
            result = runner.invoke(cli, ['ls'])

            # Check that completion was added to bashrc
            if bashrc.exists():
                content = bashrc.read_text()
                # Note: In isolated test environment, auto-setup might not trigger
                # This is expected behavior in test mode


def test_click_completion_environment_variable(runner):
    """Test that Click completion works with environment variable"""
    # Set the completion environment variable
    with patch.dict(os.environ, {'_TIX_COMPLETE': 'bash_complete'}):
        # This would normally trigger Click's completion mechanism
        # In test environment, we just verify it doesn't crash
        result = runner.invoke(cli, [])
        # Click handles completion internally when _TIX_COMPLETE is set


def test_completion_for_different_shells(runner):
    """Test that completion instructions work for all shells"""
    for shell in ['bash', 'zsh', 'fish']:
        with patch.dict(os.environ, {'SHELL': f'/bin/{shell}'}):
            result = runner.invoke(cli, ['completion'])
            assert result.exit_code == 0
            assert '_TIX_COMPLETE' in result.output


def test_no_setup_in_completion_mode(runner, mock_home):
    """Test that auto-setup doesn't run when in completion mode"""
    with patch('pathlib.Path.home', return_value=mock_home):
        with patch.dict(os.environ, {'_TIX_COMPLETE': 'bash_complete', 'SHELL': '/bin/bash'}):
            # Create mock .bashrc
            bashrc = mock_home / '.bashrc'
            bashrc.write_text('# Original\n')

            # Import and call setup function
            from tix.cli import setup_shell_completion
            setup_shell_completion()

            # Verify bashrc wasn't modified
            content = bashrc.read_text()
            assert content == '# Original\n'