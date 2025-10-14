#!/bin/bash
# cleanup_mcp_zombies.sh
# Utility to clean up zombie MCP server processes
# This is a Claude Code issue, not OTK - but we provide this helper

echo "🔍 Scanning for MCP zombie processes..."

# Find all MCP-related processes
MCP_PROCESSES=$(ps aux | grep -E "(mcp-server|tavily-mcp|playwright-mcp|context7-mcp|git-mcp-server)" | grep -v grep)

if [ -z "$MCP_PROCESSES" ]; then
    echo "✅ No MCP zombie processes found"
    exit 0
fi

echo "Found zombie MCP processes:"
echo "$MCP_PROCESSES" | awk '{print "  PID", $2, "-", $11, $12, $13}'

echo ""
read -p "Kill these processes? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗡️  Killing MCP processes..."
    echo "$MCP_PROCESSES" | awk '{print $2}' | xargs kill -9 2>/dev/null
    echo "✅ Done! Processes terminated."
else
    echo "❌ Cancelled. No processes killed."
fi
