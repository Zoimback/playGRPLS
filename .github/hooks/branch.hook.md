{
  "version": 1,
  "hooks": {
    "postToolUse": [
      {
        "type": "command",
        "bash": "git status --short --branch",
        "timeoutSec": 10
      }
    ]
  }
}
