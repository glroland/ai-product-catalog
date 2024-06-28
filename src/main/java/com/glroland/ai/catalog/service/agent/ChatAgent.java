package com.glroland.ai.catalog.service.agent;

import dev.langchain4j.service.SystemMessage;

interface ChatAgent {
    @SystemMessage({
            "You are an agent specializing in retail products.",
            "You MUST use the product tool to get the current date and time.",
            "If there a date convert it in a human readable format."
    })
    String chat(String userMessage);
}
