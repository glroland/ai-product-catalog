package com.glroland.ai.catalog.agent;

import dev.langchain4j.service.SystemMessage;

interface ProductToolEnabledChatAgent {
    @SystemMessage({
            "You are an agent specializing in retail products.",
            "You MUST use the product tool to get the current date and time.",
            "You MUST use the product tool to get information about the shoes Nike sells.",
            "You MUST use the product tool to get specific prices for products.",
            "If there a date convert it in a human readable format."
    })
    String chat(String userMessage);
}
