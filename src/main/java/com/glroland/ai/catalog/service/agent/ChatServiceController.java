package com.glroland.ai.catalog.service.agent;

import java.time.Duration;
import java.util.List;
import java.util.ArrayList;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.glroland.ai.catalog.service.ConfigManager;

import dev.langchain4j.memory.chat.MessageWindowChatMemory;
import dev.langchain4j.model.chat.ChatLanguageModel;
import dev.langchain4j.model.mistralai.MistralAiChatModel;
import dev.langchain4j.model.mistralai.MistralAiResponseFormatType;
import dev.langchain4j.service.AiServices;

@RestController
public class ChatServiceController 
{
    private static final Log log = LogFactory.getLog(ChatServiceController.class);

    @Autowired
    private ProductTool productTool;

    @Autowired
    private ConfigManager configManager;

    @GetMapping("/chat")
    public String chat(@RequestParam(value = "userMessage", defaultValue = "What is the current date and time?") String userMessage)
    {
        ChatLanguageModel chatLanguageModel = MistralAiChatModel.builder()
                    .baseUrl(configManager.getInferenceEndpoint())
                    .apiKey(configManager.getInferenceApiKey())
                    .modelName(configManager.getModelName())
                    .maxTokens(configManager.getMaxTokens())
                    .temperature(configManager.getTemperature())
                    .topP(configManager.getTopP())
                    .timeout(Duration.ofSeconds(configManager.getInferenceTimeout()))
                    .logRequests(true)
                    .logResponses(true)
                    .responseFormat(MistralAiResponseFormatType.JSON_OBJECT)
                    .build();

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
