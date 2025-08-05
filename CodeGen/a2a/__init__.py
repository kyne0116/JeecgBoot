"""
CodeGen A2A Protocol Module

This module contains all A2A (Agent-to-Agent) protocol related components for CodeGen system.
"""

from .a2a_flask_app import app
from .a2a_server import A2AProtocolServer

__all__ = ['app', 'A2AProtocolServer']
