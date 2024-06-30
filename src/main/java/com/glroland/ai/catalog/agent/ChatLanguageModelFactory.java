package com.glroland.ai.catalog.agent;

import java.time.Duration;

import org.apache.commons.lang3.StringUtils;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import com.glroland.ai.catalog.ConfigManager;

import dev.langchain4j.model.chat.ChatLanguageModel;
import dev.langchain4j.model.mistralai.MistralAiChatModel;
import dev.langchain4j.model.mistralai.MistralAiResponseFormatType;
import dev.langchain4j.model.mistralai.MistralAiChatModel.MistralAiChatModelBuilder;
import dev.langchain4j.model.openai.OpenAiChatModel;
import dev.langchain4j.model.openai.OpenAiChatModel.OpenAiChatModelBuilder;

@Component
public class ChatLanguageModelFactory 
{
    private static final Log log = LogFactory.getLog(ChatLanguageModelFactory.class);

    @Autowired
    private ConfigManager configManager;

    public ChatLanguageModel createMistral()
    {
        log.debug("Creating Mistral Chat Language Model");
        MistralAiChatModelBuilder builder = MistralAiChatModel.builder()
            .logRequests(true)
            .logResponses(true)
            .responseFormat(MistralAiResponseFormatType.TEXT);

        if (StringUtils.isNotEmpty(configManager.getInferenceEndpoint()))
            builder = builder.baseUrl(configManager.getInferenceEndpoint());
        if (StringUtils.isNotEmpty(configManager.getInferenceApiKey()))
            builder = builder.apiKey(configManager.getInferenceApiKey());
        if (StringUtils.isNotEmpty(configManager.getModelName()))
            builder = builder.modelName(configManager.getModelName());
        if (configManager.getMaxTokens() != null)
            builder = builder.maxTokens(configManager.getMaxTokens());
        if (configManager.getTemperature() != null)
            builder = builder.temperature(configManager.getTemperature());
        if (configManager.getTopP() != null)
            builder = builder.topP(configManager.getTopP());
        if (configManager.getInferenceTimeout() != null)
            builder = builder.timeout(Duration.ofSeconds(configManager.getInferenceTimeout()));

        return builder.build();
    }

    public ChatLanguageModel createOpenAi()
    {
        log.debug("Creating Mistral Chat Language Model");
        OpenAiChatModelBuilder builder = OpenAiChatModel.builder()
            .logRequests(true)
            .logResponses(true)
            .responseFormat("text"); // Supported values are: 'json_object' and 'text'.
        
        if (StringUtils.isNotEmpty(configManager.getInferenceEndpoint()))
            builder = builder.baseUrl(configManager.getInferenceEndpoint());
        if (StringUtils.isNotEmpty(configManager.getInferenceApiKey()))
            builder = builder.apiKey(configManager.getInferenceApiKey());
        if (StringUtils.isNotEmpty(configManager.getModelName()))
            builder = builder.modelName(configManager.getModelName());
        if (configManager.getMaxTokens() != null)
            builder = builder.maxTokens(configManager.getMaxTokens());
        if (configManager.getTemperature() != null)
            builder = builder.temperature(configManager.getTemperature());
        if (configManager.getTopP() != null)
            builder = builder.topP(configManager.getTopP());
        if (configManager.getInferenceTimeout() != null)
            builder = builder.timeout(Duration.ofSeconds(configManager.getInferenceTimeout()));

        return builder.build();
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
