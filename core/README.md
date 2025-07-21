# Core Module

This module contains the core logic for the Slack bot, including event handling, workflow orchestration, and integrations.

## Slack Bolt Communications

The following diagram illustrates the communication flow between Slack and the bot when handling various events.

```mermaid
sequenceDiagram
    participant User
    participant Slack API
    participant SlackBotHandler
    participant Workflows
    participant Services

    User->>Slack API: Sends message (e.g., "review pr ...")
    Slack API->>SlackBotHandler: Message Event
    SlackBotHandler->>SlackBotHandler: Parses command ("review pr")
    SlackBotHandler->>Workflows: Calls pr_review_workflow()
    Workflows-->>SlackBotHandler: Returns result
    SlackBotHandler->>Slack API: Sends response to user

    User->>Slack API: Clicks "Approve" button
    Slack API->>SlackBotHandler: Action Event ("approve")
    SlackBotHandler->>Services: Calls ApprovalService
    Services-->>SlackBotHandler: Handles approval
    SlackBotHandler->>Slack API: Sends confirmation message

    User->>Slack API: Uploads an audio/video file
    Slack API->>SlackBotHandler: File Share Event
    alt Audio File
        SlackBotHandler->>Services: process_slack_audio_event()
        Services-->>SlackBotHandler: Returns transcript
        SlackBotHandler->>Services: ArchitectService.conduct_research(transcript)
        Services-->>SlackBotHandler: Returns research result
        SlackBotHandler->>Slack API: Sends transcript & results
    else Video File
        SlackBotHandler->>Services: process_slack_video_event()
        Services-->>SlackBotHandler: Returns video info
        SlackBotHandler->>Services: process_video_with_rag()
        Services-->>SlackBotHandler: Returns video understanding
        SlackBotHandler->>Services: ArchitectService.conduct_research(analysis)
        Services-->>SlackBotHandler: Returns research result
        SlackBotHandler->>Slack API: Sends summary & results
    end
