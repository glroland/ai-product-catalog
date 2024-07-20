package com.glroland.ai.catalog.pdf;

import dev.langchain4j.service.SystemMessage;

interface SummarizerChatAgent {
    @SystemMessage({
            "You are a finance specialist for a large global corporation who has a background in legal contracts.",
            "Your specialty is translating complex documents into language a common business analyst can understand."
    })
    String chat(String userMessage);
}
