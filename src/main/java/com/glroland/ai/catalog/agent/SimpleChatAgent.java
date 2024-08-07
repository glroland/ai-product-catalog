package com.glroland.ai.catalog.agent;

import dev.langchain4j.service.SystemMessage;

interface SimpleChatAgent {
    @SystemMessage({
            "You are a helpful sales agent for a shoe store.",
            "Only talk about selling shoes.",
            "Do not participate in hateful or abusive conversations.",
            "If there a date convert it in a human readable format."
    })
    String chat(String userMessage);
}
