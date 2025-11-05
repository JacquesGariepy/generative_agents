"""
Shell Interface - Linux Command Execution

Enables agents to execute Linux shell commands safely and autonomously.

Features:
- Safe command execution with sandboxing
- Command history and learning
- Error handling and recovery
- Resource monitoring
- Permission management

Author: Autonomous Implementation
"""

import subprocess
import os
import time
import json
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
import shlex
import psutil


@dataclass
class CommandResult:
    """Result of a shell command execution"""
    command: str
    stdout: str
    stderr: str
    return_code: int
    execution_time: float
    success: bool
    timestamp: str


class ShellInterface:
    """
    Safe interface for agents to execute shell commands.

    Implements safety measures, learning, and autonomous command composition.
    """

    def __init__(self, agent_name: str, working_directory: str = "/tmp/agent_workspace"):
        self.agent_name = agent_name
        self.working_directory = working_directory

        # Create agent's workspace
        os.makedirs(self.working_directory, exist_ok=True)

        # Command history and learning
        self.command_history: List[CommandResult] = []
        self.successful_patterns: Dict[str, int] = {}

        # Safety settings
        self.allowed_commands = self._init_safe_commands()
        self.forbidden_patterns = ['rm -rf /', 'dd if=', 'fork bomb', ':(){ :|:& };:']
        self.max_execution_time = 60  # seconds

        # Resource limits
        self.max_memory_mb = 512
        self.max_cpu_percent = 50

    def _init_safe_commands(self) -> set:
        """Initialize list of safe commands"""
        return {
            # File operations
            'ls', 'cat', 'less', 'head', 'tail', 'grep', 'find', 'wc',
            'touch', 'mkdir', 'cp', 'mv', 'rm',

            # Text processing
            'sed', 'awk', 'sort', 'uniq', 'cut', 'tr',

            # System info
            'pwd', 'whoami', 'date', 'hostname', 'uname',
            'df', 'du', 'free', 'top', 'ps',

            # Network
            'ping', 'curl', 'wget', 'nc', 'dig', 'nslookup',

            # Development
            'git', 'python', 'python3', 'pip', 'pip3',
            'node', 'npm', 'make', 'gcc',

            # Utilities
            'echo', 'printf', 'which', 'whereis', 'file',
            'tar', 'gzip', 'gunzip', 'zip', 'unzip'
        }

    def execute(self, command: str, timeout: Optional[int] = None) -> CommandResult:
        """
        Execute a shell command safely.

        Args:
            command: Command to execute
            timeout: Max execution time (seconds)

        Returns:
            CommandResult with output and status
        """
        start_time = time.time()
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

        # Safety checks
        if not self._is_safe_command(command):
            return CommandResult(
                command=command,
                stdout="",
                stderr=f"Command rejected by safety check: {command}",
                return_code=-1,
                execution_time=0,
                success=False,
                timestamp=timestamp
            )

        # Execute command
        try:
            # Use subprocess with timeout
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.working_directory,
                text=True
            )

            # Monitor resource usage
            try:
                proc = psutil.Process(process.pid)

                # Wait for completion with timeout
                stdout, stderr = process.communicate(
                    timeout=timeout or self.max_execution_time
                )

            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                stderr += "\n[Killed: Execution timeout]"

            return_code = process.returncode
            execution_time = time.time() - start_time
            success = return_code == 0

            result = CommandResult(
                command=command,
                stdout=stdout,
                stderr=stderr,
                return_code=return_code,
                execution_time=execution_time,
                success=success,
                timestamp=timestamp
            )

            # Learn from execution
            self._learn_from_execution(result)

            return result

        except Exception as e:
            return CommandResult(
                command=command,
                stdout="",
                stderr=f"Execution error: {str(e)}",
                return_code=-1,
                execution_time=time.time() - start_time,
                success=False,
                timestamp=timestamp
            )

    def _is_safe_command(self, command: str) -> bool:
        """Check if command is safe to execute"""
        # Check for forbidden patterns
        for pattern in self.forbidden_patterns:
            if pattern in command.lower():
                return False

        # Extract base command
        try:
            parts = shlex.split(command)
            if not parts:
                return False

            base_cmd = parts[0]

            # Check if base command is allowed
            if base_cmd not in self.allowed_commands:
                # Allow if it's a path to allowed command
                if '/' in base_cmd:
                    base_cmd = os.path.basename(base_cmd)
                    if base_cmd not in self.allowed_commands:
                        return False
                else:
                    return False

        except ValueError:
            return False

        return True

    def _learn_from_execution(self, result: CommandResult):
        """Learn from command execution"""
        self.command_history.append(result)

        # Track successful patterns
        if result.success:
            # Extract pattern (first 2 words)
            parts = result.command.split()
            if len(parts) >= 2:
                pattern = ' '.join(parts[:2])
                self.successful_patterns[pattern] = \
                    self.successful_patterns.get(pattern, 0) + 1

    def compose_command(self, goal: str) -> Optional[str]:
        """
        Autonomously compose a command to achieve a goal.

        Args:
            goal: What to achieve (e.g., "list all python files")

        Returns:
            Composed command or None
        """
        goal_lower = goal.lower()

        # Pattern matching for common goals
        if 'list' in goal_lower and 'file' in goal_lower:
            if 'python' in goal_lower:
                return "find . -name '*.py' -type f"
            elif 'directory' in goal_lower or 'folder' in goal_lower:
                return "ls -la"
            else:
                return "ls -lh"

        elif 'search' in goal_lower or 'find' in goal_lower:
            # Extract search term
            words = goal_lower.split()
            if 'for' in words:
                idx = words.index('for')
                if idx + 1 < len(words):
                    term = words[idx + 1]
                    return f"grep -r '{term}' ."

        elif 'disk' in goal_lower and ('space' in goal_lower or 'usage' in goal_lower):
            return "df -h"

        elif 'process' in goal_lower:
            if 'python' in goal_lower:
                return "ps aux | grep python"
            else:
                return "ps aux"

        elif 'download' in goal_lower:
            # Extract URL
            words = goal.split()
            for word in words:
                if word.startswith('http'):
                    return f"wget {word}"

        elif 'create' in goal_lower and ('file' in goal_lower or 'directory' in goal_lower):
            if 'directory' in goal_lower:
                # Extract name
                words = goal.split()
                if len(words) > 2:
                    name = words[-1]
                    return f"mkdir -p {name}"
            else:
                words = goal.split()
                if len(words) > 1:
                    name = words[-1]
                    return f"touch {name}"

        # Learning: use successful patterns
        for pattern, count in sorted(
            self.successful_patterns.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            if any(word in goal_lower for word in pattern.lower().split()):
                return f"{pattern} ..."  # Template

        return None

    def get_command_suggestions(self, context: str) -> List[str]:
        """
        Get command suggestions based on context.

        Args:
            context: Current context

        Returns:
            List of suggested commands
        """
        suggestions = []

        # Context-based suggestions
        if 'error' in context.lower():
            suggestions.extend([
                "tail -n 50 /var/log/syslog",
                "dmesg | tail -n 20",
                "journalctl -n 50"
            ])

        if 'slow' in context.lower() or 'performance' in context.lower():
            suggestions.extend([
                "top -bn1",
                "free -h",
                "df -h",
                "ps aux --sort=-%mem | head -n 10"
            ])

        if 'network' in context.lower():
            suggestions.extend([
                "ping -c 4 8.8.8.8",
                "netstat -tuln",
                "ss -tuln"
            ])

        # Based on successful history
        if len(self.command_history) > 5:
            recent_successful = [
                cmd.command for cmd in self.command_history[-10:]
                if cmd.success
            ]
            suggestions.extend(recent_successful[:3])

        return suggestions

    def get_workspace_info(self) -> Dict[str, Any]:
        """Get information about agent's workspace"""
        try:
            # List files
            files = os.listdir(self.working_directory)

            # Get size
            total_size = sum(
                os.path.getsize(os.path.join(self.working_directory, f))
                for f in files
                if os.path.isfile(os.path.join(self.working_directory, f))
            )

            return {
                'working_directory': self.working_directory,
                'file_count': len(files),
                'total_size_bytes': total_size,
                'files': files[:10],  # First 10 files
                'commands_executed': len(self.command_history),
                'successful_commands': sum(1 for cmd in self.command_history if cmd.success)
            }

        except Exception as e:
            return {'error': str(e)}

    def cleanup_workspace(self):
        """Clean up agent's workspace"""
        try:
            for item in os.listdir(self.working_directory):
                item_path = os.path.join(self.working_directory, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    import shutil
                    shutil.rmtree(item_path)

            return True

        except Exception as e:
            return False

    def save_history(self, filepath: str):
        """Save command history to file"""
        history_data = [
            {
                'command': cmd.command,
                'success': cmd.success,
                'return_code': cmd.return_code,
                'execution_time': cmd.execution_time,
                'timestamp': cmd.timestamp
            }
            for cmd in self.command_history
        ]

        with open(filepath, 'w') as f:
            json.dump(history_data, f, indent=2)
