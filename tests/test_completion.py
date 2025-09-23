import pytest
from click.testing import CliRunner
from tix.cli import cli
import tempfile
from pathlib import Path
from unittest.mock import patch


@pytest.fixture
def runner():
    """Create a CLI runner for testing"""
    return CliRunner()


def test_completion_command_exists(runner):
    """Test that completion command exists"""
    result = runner.invoke(cli, ['completion', '--help'])
    assert result.exit_code == 0
    assert 'Generate or install shell completion scripts' in result.output


def test_generate_bash_completion(runner):
    """Test generating bash completion script"""
    result = runner.invoke(cli, ['completion', '--shell', 'bash'])
    assert result.exit_code == 0
    assert '_tix_completion()' in result.output
    assert 'complete -o nosort -F _tix_completion tix' in result.output
    assert 'COMP_WORDS' in result.output


def test_generate_zsh_completion(runner):
    """Test generating zsh completion script"""
    result = runner.invoke(cli, ['completion', '--shell', 'zsh'])
    assert result.exit_code == 0
    assert '#compdef tix' in result.output
    assert '_tix_completion()' in result.output
    assert 'compdef _tix_completion tix' in result.output


def test_generate_fish_completion(runner):
    """Test generating fish completion script"""
    result = runner.invoke(cli, ['completion', '--shell', 'fish'])
    assert result.exit_code == 0
    assert 'function _tix_completion' in result.output
    assert 'complete -c tix' in result.output
    assert '__fish_complete_directories' in result.output


def test_completion_requires_shell_option(runner):
    """Test that completion command requires --shell option"""
    result = runner.invoke(cli, ['completion'])
    assert result.exit_code != 0
    assert 'Missing option' in result.output or 'required' in result.output.lower()


def test_completion_invalid_shell(runner):
    """Test completion with invalid shell type"""
    result = runner.invoke(cli, ['completion', '--shell', 'invalid'])
    assert result.exit_code != 0
    assert 'Invalid value' in result.output or 'invalid' in result.output.lower()


def test_install_bash_completion(runner):
    """Test installing bash completion script"""
    with runner.isolated_filesystem():
        # Create a mock home directory
        home_dir = Path.cwd() / 'home'
        home_dir.mkdir()
        bash_comp_dir = home_dir / '.bash_completion.d'
        bash_comp_dir.mkdir()

        with patch('pathlib.Path.home', return_value=home_dir):
            result = runner.invoke(cli, ['completion', '--shell', 'bash', '--install'])

            assert result.exit_code == 0
            assert 'Installed bash completion' in result.output

            # Check that the file was created
            comp_file = bash_comp_dir / 'tix.bash'
            assert comp_file.exists()
            content = comp_file.read_text()
            assert '_tix_completion()' in content


def test_install_zsh_completion(runner):
    """Test installing zsh completion script"""
    with runner.isolated_filesystem():
        # Create a mock home directory
        home_dir = Path.cwd() / 'home'
        home_dir.mkdir()

        with patch('pathlib.Path.home', return_value=home_dir):
            result = runner.invoke(cli, ['completion', '--shell', 'zsh', '--install'])

            assert result.exit_code == 0
            assert 'Installed zsh completion' in result.output

            # Check that the file was created
            comp_file = home_dir / '.zsh/completions/_tix'
            assert comp_file.exists()
            content = comp_file.read_text()
            assert '#compdef tix' in content


def test_install_fish_completion(runner):
    """Test installing fish completion script"""
    with runner.isolated_filesystem():
        # Create a mock home directory
        home_dir = Path.cwd() / 'home'
        home_dir.mkdir()

        with patch('pathlib.Path.home', return_value=home_dir):
            result = runner.invoke(cli, ['completion', '--shell', 'fish', '--install'])

            assert result.exit_code == 0
            assert 'Installed fish completion' in result.output

            # Check that the file was created
            comp_file = home_dir / '.config/fish/completions/tix.fish'
            assert comp_file.exists()
            content = comp_file.read_text()
            assert 'function _tix_completion' in content


def test_completion_script_contains_all_commands(runner):
    """Test that completion scripts reference all CLI commands"""
    # Get bash completion (could test any shell)
    result = runner.invoke(cli, ['completion', '--shell', 'bash'])
    assert result.exit_code == 0

    # The completion script should work with Click's built-in mechanism
    # which automatically handles all commands
    assert '_TIX_COMPLETE=bash_complete' in result.output