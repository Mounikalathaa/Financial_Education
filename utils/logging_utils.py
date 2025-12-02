"""Logging and observability utilities."""

import logging
import sys
from pathlib import Path
from datetime import datetime
import colorlog

def setup_logging(log_level: str = "INFO", log_file: str = None):
    """
    Set up comprehensive logging with color output and file logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path for log output
    """
    # Create logs directory if needed
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Console handler with colors
    console_handler = colorlog.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    console_format = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s%(reset)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_format)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        root_logger.addHandler(file_handler)
    
    return root_logger

class AgentTracer:
    """Utility for tracing agent execution flow."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.traces = []
    
    def log_step(self, agent_name: str, action: str, details: dict = None):
        """Log an agent execution step."""
        trace_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "action": action,
            "details": details or {}
        }
        self.traces.append(trace_entry)
        
        # Log to console
        details_str = f" | {details}" if details else ""
        self.logger.info(f"[{agent_name}] {action}{details_str}")
    
    def get_trace_summary(self) -> str:
        """Get formatted trace summary."""
        if not self.traces:
            return "No traces recorded"
        
        summary = "\n=== Agent Execution Trace ===\n"
        for i, trace in enumerate(self.traces, 1):
            summary += f"\n{i}. [{trace['timestamp']}] {trace['agent']}\n"
            summary += f"   Action: {trace['action']}\n"
            if trace['details']:
                summary += f"   Details: {trace['details']}\n"
        
        return summary
    
    def clear_traces(self):
        """Clear all traces."""
        self.traces = []
