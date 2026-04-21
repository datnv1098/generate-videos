<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## YouTube Research MCP Server

### Project Overview
This is a Model Context Protocol (MCP) server that provides tools for researching and analyzing YouTube videos. It enables Claude to search videos, retrieve video information, analyze comments, get transcripts, and analyze channel data.

### Technology Stack
- **Language**: TypeScript
- **Runtime**: Node.js
- **Framework**: @modelcontextprotocol/sdk
- **Build**: TypeScript Compiler (tsc)

### Key Files
- `src/index.ts` - Main MCP server implementation with tool definitions
- `.vscode/mcp.json` - MCP server configuration
- `package.json` - Project dependencies and scripts
- `tsconfig.json` - TypeScript compilation settings

### Available Tools
1. search_videos - Search YouTube videos
2. get_video_info - Get video details
3. get_video_comments - Retrieve video comments
4. get_video_transcript - Get video transcript
5. get_channel_info - Get channel information
6. analyze_video_sentiment - Analyze comment sentiment

### Development Commands
- `npm install` - Install dependencies
- `npm run build` - Compile TypeScript to JavaScript
- `npm run dev` - Build and run development server
- `npm start` - Run compiled server
- `npm run watch` - Watch for TypeScript changes and auto-compile

### Integration with Claude Desktop
After building, add this to Claude Desktop config:
```json
{
  "mcpServers": {
    "youtube-research": {
      "command": "node",
      "args": ["path/to/build/index.js"]
    }
  }
}
```

### Next Steps for YouTube API Integration
1. Obtain YouTube API key from Google Cloud Console
2. Install `googleapis` package: `npm install googleapis`
3. Create `.env` file with API key
4. Update tool implementations in `src/index.ts` with real API calls
5. Test with Claude Desktop

### MCP Protocol Reference
- Documentation: https://modelcontextprotocol.io/
- TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk
- Examples: https://github.com/modelcontextprotocol/servers

### Debugging
- Errors logged to stderr
- Build output in `/build` directory
- Check TypeScript compilation errors with `npm run build`
