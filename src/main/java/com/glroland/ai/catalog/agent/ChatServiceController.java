package com.glroland.ai.catalog.agent;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import dev.langchain4j.memory.chat.MessageWindowChatMemory;
import dev.langchain4j.model.chat.ChatLanguageModel;
import dev.langchain4j.service.AiServices;

@RestController
public class ChatServiceController 
{
    private static final Log log = LogFactory.getLog(ChatServiceController.class);

    @Autowired
    private ProductTool productTool;

    @Autowired
    private ChatLanguageModelFactory chatLanguageModelFactory;

    @PostMapping("/chat")
    public String chat(@RequestParam(value = "userMessage", defaultValue = "What is the current date and time?") String userMessage)
    {
        ChatLanguageModel chatLanguageModel = chatLanguageModelFactory.createDefault();

        ChatAgent agent = AiServices.builder(ChatAgent.class)
                .chatLanguageModel(chatLanguageModel)
                .tools(productTool)
                .chatMemory(MessageWindowChatMemory.withMaxMessages(10))
                .build();
        
        String answer = agent.chat(userMessage);
        log.info("User Message = '" + userMessage + "'  Response = '" + answer + "'");

        return answer;
    }
}
