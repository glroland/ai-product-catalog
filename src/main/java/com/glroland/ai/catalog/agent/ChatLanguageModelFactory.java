package com.glroland.ai.catalog.agent;

import java.time.Duration;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import com.glroland.ai.catalog.ConfigManager;

import dev.langchain4j.model.chat.ChatLanguageModel;
import dev.langchain4j.model.mistralai.MistralAiChatModel;
import dev.langchain4j.model.mistralai.MistralAiResponseFormatType;
import dev.langchain4j.model.openai.OpenAiChatModel;

@Component
public class ChatLanguageModelFactory 
{
    private static final Log log = LogFactory.getLog(ChatLanguageModelFactory.class);

    @Autowired
    private ConfigManager configManager;

    public ChatLanguageModel createMistral()
    {
        log.debug("Creating Mistral Chat Language Model");
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
            .responseFormat(MistralAiResponseFormatType.TEXT)
            .build();

        return chatLanguageModel;
    }

    public ChatLanguageModel createOpenAi()
    {
        log.debug("Creating Mistral Chat Language Model");
        ChatLanguageModel chatLanguageModel = OpenAiChatModel.builder()
            .baseUrl(configManager.getInferenceEndpoint())
            .apiKey(configManager.getInferenceApiKey())
            .modelName(configManager.getModelName())
            .maxTokens(configManager.getMaxTokens())
            .temperature(configManager.getTemperature())
            .topP(configManager.getTopP())
            .timeout(Duration.ofSeconds(configManager.getInferenceTimeout()))
            .logRequests(true)
            .logResponses(true)
            .responseFormat("TEXT")
            .build();

        return chatLanguageModel;
    }

    public ChatLanguageModel createDefault()
    {
        String defaultModel = configManager.getDefaultChatModel();
        if ((defaultModel == null) || (defaultModel.length() == 0))
        {
            log.warn("No default chat model specified.  Using default...");
            defaultModel = ConfigManager.CHAT_MODEL_MISTRAL;
        }

        if(ConfigManager.CHAT_MODEL_MISTRAL.equalsIgnoreCase(defaultModel))
        {
            log.debug("Using Mistral Chat Model");
            return this.createMistral();
        }

        if(ConfigManager.CHAT_MODEL_OPENAI.equalsIgnoreCase(defaultModel))
        {
            log.debug("Using Open AI Chat Model");
            return this.createOpenAi();
        }

        // unknown chat model type
        String msg = "Unknown Chat Model Type Requested: " + defaultModel;
        log.error(msg);
        throw new RuntimeException(msg);
    }
}
