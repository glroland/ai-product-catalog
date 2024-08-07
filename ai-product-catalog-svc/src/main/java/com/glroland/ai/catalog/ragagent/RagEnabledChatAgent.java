package com.glroland.ai.catalog.ragagent;

import dev.langchain4j.service.SystemMessage;

interface RagEnabledChatAgent {
    @SystemMessage({
            "You are an agent specializing in retail products."
    })
    String chat(String userMessage);
}

