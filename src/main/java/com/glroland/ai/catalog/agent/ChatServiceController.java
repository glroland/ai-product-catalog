package com.glroland.ai.catalog.agent;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.glroland.ai.catalog.ChatLanguageModelFactory;
import com.glroland.ai.catalog.ConfigManager;

import dev.langchain4j.memory.chat.MessageWindowChatMemory;
import dev.langchain4j.model.chat.ChatLanguageModel;
import dev.langchain4j.service.AiServices;
import io.micrometer.common.util.StringUtils;

@RestController
public class ChatServiceController 
{
    private static final Log log = LogFactory.getLog(ChatServiceController.class);

    @Autowired
    private ProductTool productTool;

    @Autowired
    private ChatLanguageModelFactory chatLanguageModelFactory;

    @PostMapping("/chat")
    public String chat(@RequestParam(value = "userMessage", defaultValue = "What is the current date and time?") 
                        String userMessage,
                       @RequestParam(value = "type", defaultValue = ConfigManager.AGENT_TYPE_SIMPLE)
                        String type)
    {
        if (ConfigManager.AGENT_TYPE_SIMPLE.equals(type) || StringUtils.isEmpty(type))
        {
            log.info("Chatting w/Simple Chat Engine Type");
            return simpleChat(userMessage);
        }

        if (ConfigManager.AGENT_TYPE_TOOL.equals(type))
        {
            log.info("Chatting w/Complex Chat Engine - Includes Tool/Function Support");
            return chatWithTool(userMessage);
        }

        // unknown chat engine type specified
        String msg = "Unknown Agent Type Specified.  Type = " + type;
        log.error(msg);
        throw new RuntimeException(msg);
    }

    private String chatWithTool(String userMessage)
    {
        ChatLanguageModel chatLanguageModel = chatLanguageModelFactory.createOpenAi();

        ProductToolEnabledChatAgent agent = AiServices.builder(ProductToolEnabledChatAgent.class)
                .chatLanguageModel(chatLanguageModel)
                .tools(productTool)
                .chatMemory(MessageWindowChatMemory.withMaxMessages(10))
                .build();
        
        String answer = agent.chat(userMessage);
        log.info("User Message = '" + userMessage + "'  Response = '" + answer + "'");

        return answer;
    }

    private String simpleChat(String userMessage)
    {
        ChatLanguageModel chatLanguageModel = chatLanguageModelFactory.createOpenAi();

        SimpleChatAgent agent = AiServices.builder(SimpleChatAgent.class)
                .chatLanguageModel(chatLanguageModel)
                .chatMemory(MessageWindowChatMemory.withMaxMessages(10))
                .build();
        
        String answer = agent.chat(userMessage);
        log.info("User Message = '" + userMessage + "'  Response = '" + answer + "'");

        return answer;
    }
}
