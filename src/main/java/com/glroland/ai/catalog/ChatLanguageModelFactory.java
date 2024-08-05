package com.glroland.ai.catalog;

import java.time.Duration;

import org.apache.commons.lang3.StringUtils;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import dev.langchain4j.model.chat.ChatLanguageModel;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.huggingface.HuggingFaceEmbeddingModel;
import dev.langchain4j.model.huggingface.HuggingFaceEmbeddingModel.HuggingFaceEmbeddingModelBuilder;
import dev.langchain4j.model.localai.LocalAiChatModel;
import dev.langchain4j.model.localai.LocalAiChatModel.LocalAiChatModelBuilder;
import dev.langchain4j.model.localai.LocalAiEmbeddingModel;
import dev.langchain4j.model.localai.LocalAiEmbeddingModel.LocalAiEmbeddingModelBuilder;
import dev.langchain4j.model.mistralai.MistralAiChatModel;
import dev.langchain4j.model.mistralai.internal.api.MistralAiResponseFormatType;
import dev.langchain4j.model.ollama.OllamaChatModel;
import dev.langchain4j.model.ollama.OllamaEmbeddingModel;
import dev.langchain4j.model.ollama.OllamaChatModel.OllamaChatModelBuilder;
import dev.langchain4j.model.ollama.OllamaEmbeddingModel.OllamaEmbeddingModelBuilder;
import dev.langchain4j.model.mistralai.MistralAiChatModel.MistralAiChatModelBuilder;
import dev.langchain4j.model.mistralai.MistralAiEmbeddingModel;
import dev.langchain4j.model.mistralai.MistralAiEmbeddingModel.MistralAiEmbeddingModelBuilder;
import dev.langchain4j.model.openai.OpenAiChatModel;
import dev.langchain4j.model.openai.OpenAiChatModel.OpenAiChatModelBuilder;
import dev.langchain4j.model.openai.OpenAiEmbeddingModel;
import dev.langchain4j.model.openai.OpenAiEmbeddingModel.OpenAiEmbeddingModelBuilder;

@Component
public class ChatLanguageModelFactory 
{
    private static final Log log = LogFactory.getLog(ChatLanguageModelFactory.class);

    @Autowired
    private ConfigManager configManager;

    public MistralAiEmbeddingModel createMistralEmbeddingModel()
    {
        log.debug("Creating Mistral Embedding Model");
        MistralAiEmbeddingModelBuilder builder = MistralAiEmbeddingModel.builder()
            .logRequests(true)
            .logResponses(true);

        String v = configManager.getInferenceEndpoint(ConfigManager.CHAT_MODEL_MISTRAL);
        if (StringUtils.isNotEmpty(v))
            builder = builder.baseUrl(v);
        v = configManager.getInferenceApiKey(ConfigManager.CHAT_MODEL_MISTRAL);
        if (StringUtils.isNotEmpty(v))
            builder = builder.apiKey(v);
        v = configManager.getEmbeddingModelName(ConfigManager.CHAT_MODEL_MISTRAL);
        if (StringUtils.isNotEmpty(v))
            builder = builder.modelName(v);

        return builder.build();
    }

    public ChatLanguageModel createMistral()
    {
        log.debug("Creating Mistral Chat Language Model");
        MistralAiChatModelBuilder builder = MistralAiChatModel.builder()
            .logRequests(true)
            .logResponses(true)
            .responseFormat(MistralAiResponseFormatType.TEXT);

        String v = configManager.getInferenceEndpoint(ConfigManager.CHAT_MODEL_MISTRAL);
        if (StringUtils.isNotEmpty(v))
            builder = builder.baseUrl(v);
        v = configManager.getInferenceApiKey(ConfigManager.CHAT_MODEL_MISTRAL);
        if (StringUtils.isNotEmpty(v))
            builder = builder.apiKey(v);
        v = configManager.getAgentModelName(ConfigManager.CHAT_MODEL_MISTRAL);
        if (StringUtils.isNotEmpty(v))
            builder = builder.modelName(v);
        Integer iv = configManager.getMaxTokens(ConfigManager.CHAT_MODEL_MISTRAL);
        if (v != null)
            builder = builder.maxTokens(iv);
        Double dv = configManager.getTemperature(ConfigManager.CHAT_MODEL_MISTRAL);
        if (dv != null)
            builder = builder.temperature(dv);
        dv = configManager.getTopP(ConfigManager.CHAT_MODEL_MISTRAL);
        if (dv != null)
            builder = builder.topP(dv);
        iv = configManager.getInferenceTimeout(ConfigManager.CHAT_MODEL_MISTRAL);
        if (iv != null)
            builder = builder.timeout(Duration.ofSeconds(iv));

        return builder.build();
    }

    public OpenAiEmbeddingModel createOpenAiEmbeddingModel()
    {
        log.debug("Creating Open AI Embedding Model");

        OpenAiEmbeddingModelBuilder builder = OpenAiEmbeddingModel.builder()
            .logRequests(true)
            .logResponses(true);

        String v = configManager.getInferenceEndpoint(ConfigManager.CHAT_MODEL_OPENAI);
        if (StringUtils.isNotEmpty(v))
            builder = builder.baseUrl(v);
        v = configManager.getInferenceApiKey(ConfigManager.CHAT_MODEL_OPENAI);
        if (StringUtils.isNotEmpty(v))
            builder = builder.apiKey(v);
        v = configManager.getEmbeddingModelName(ConfigManager.CHAT_MODEL_OPENAI);
        if (StringUtils.isNotEmpty(v))
            builder = builder.modelName(v);
        Integer iv = configManager.getInferenceTimeout(ConfigManager.CHAT_MODEL_OPENAI);
        if (iv != null)
            builder = builder.timeout(Duration.ofSeconds(iv));
        iv = configManager.getEmbeddingsDimensions(ConfigManager.CHAT_MODEL_OPENAI);
        if (iv != null)
            builder.dimensions(iv);

        return builder.build();
    }

    public ChatLanguageModel createOpenAi()
    {
        log.debug("Creating OpenAI Chat Language Model");
        OpenAiChatModelBuilder builder = OpenAiChatModel.builder()
            .logRequests(true)
            .logResponses(true)
            .responseFormat("text"); // Supported values are: 'json_object' and 'text'.

        String v = configManager.getInferenceEndpoint(ConfigManager.CHAT_MODEL_OPENAI);
        if (StringUtils.isNotEmpty(v))
            builder = builder.baseUrl(v);
        v = configManager.getInferenceApiKey(ConfigManager.CHAT_MODEL_OPENAI);
        if (StringUtils.isNotEmpty(v))
            builder = builder.apiKey(v);
        v = configManager.getAgentModelName(ConfigManager.CHAT_MODEL_OPENAI);
        if (StringUtils.isNotEmpty(v))
            builder = builder.modelName(v);
        Integer iv = configManager.getMaxTokens(ConfigManager.CHAT_MODEL_OPENAI);
        if (v != null)
            builder = builder.maxTokens(iv);
        Double dv = configManager.getTemperature(ConfigManager.CHAT_MODEL_OPENAI);
        if (dv != null)
            builder = builder.temperature(dv);
        dv = configManager.getTopP(ConfigManager.CHAT_MODEL_OPENAI);
        if (dv != null)
            builder = builder.topP(dv);
        iv = configManager.getInferenceTimeout(ConfigManager.CHAT_MODEL_OPENAI);
        if (iv != null)
            builder = builder.timeout(Duration.ofSeconds(iv));
    
        return builder.build();
    }

    public OllamaEmbeddingModel createOllamaEmbeddingModel()
    {
        log.debug("Creating Ollama Embedding Model");
        OllamaEmbeddingModelBuilder builder = OllamaEmbeddingModel.builder()
            .logRequests(true)
            .logResponses(true);

        String v = configManager.getInferenceEndpoint(ConfigManager.CHAT_MODEL_OLLAMA);
        if (StringUtils.isNotEmpty(v))
            builder = builder.baseUrl(v);
        v = configManager.getEmbeddingModelName(ConfigManager.CHAT_MODEL_OLLAMA);
        if (StringUtils.isNotEmpty(v))
            builder = builder.modelName(v);
        Integer iv = configManager.getInferenceTimeout(ConfigManager.CHAT_MODEL_OLLAMA);
        if (iv != null)
            builder = builder.timeout(Duration.ofSeconds(iv));
    
        return builder.build();
    }

    public ChatLanguageModel createOllama()
    {
        log.debug("Creating Ollama Chat Language Model");
        OllamaChatModelBuilder builder = OllamaChatModel.builder()
            .logRequests(true)
            .logResponses(true);

        String v = configManager.getInferenceEndpoint(ConfigManager.CHAT_MODEL_OLLAMA);
        if (StringUtils.isNotEmpty(v))
            builder = builder.baseUrl(v);
        v = configManager.getAgentModelName(ConfigManager.CHAT_MODEL_OLLAMA);
        if (StringUtils.isNotEmpty(v))
            builder = builder.modelName(v);
        Double dv = configManager.getTemperature(ConfigManager.CHAT_MODEL_OLLAMA);
        if (dv != null)
            builder = builder.temperature(dv);
        dv = configManager.getTopP(ConfigManager.CHAT_MODEL_OLLAMA);
        if (dv != null)
            builder = builder.topP(dv);
        Integer iv = configManager.getInferenceTimeout(ConfigManager.CHAT_MODEL_OLLAMA);
        if (iv != null)
            builder = builder.timeout(Duration.ofSeconds(iv));

        return builder.build();
    }

    public LocalAiEmbeddingModel createLocalAiEmbeddingModel()
    {
        LocalAiEmbeddingModelBuilder builder = LocalAiEmbeddingModel.builder()
            .logRequests(true)
            .logResponses(true);

        String v = configManager.getInferenceEndpoint(ConfigManager.CHAT_MODEL_LOCALAI);
        if (StringUtils.isNotEmpty(v))
            builder = builder.baseUrl(v);
        v = configManager.getEmbeddingModelName(ConfigManager.CHAT_MODEL_LOCALAI);
        if (StringUtils.isNotEmpty(v))
            builder = builder.modelName(v);
        Integer iv = configManager.getInferenceTimeout(ConfigManager.CHAT_MODEL_LOCALAI);
        if (iv != null)
            builder = builder.timeout(Duration.ofSeconds(iv));
    
        return builder.build();
    }

    public ChatLanguageModel createLocalAi()
    {
        log.debug("Creating Local AI Chat Language Model");
        LocalAiChatModelBuilder builder = LocalAiChatModel.builder()
            .logRequests(true)
            .logResponses(true);

        String v = configManager.getInferenceEndpoint(ConfigManager.CHAT_MODEL_LOCALAI);
        if (StringUtils.isNotEmpty(v))
            builder = builder.baseUrl(v);
        v = configManager.getAgentModelName(ConfigManager.CHAT_MODEL_LOCALAI);
        if (StringUtils.isNotEmpty(v))
            builder = builder.modelName(v);
        Integer iv = configManager.getMaxTokens(ConfigManager.CHAT_MODEL_LOCALAI);
        if (v != null)
            builder = builder.maxTokens(iv);
        Double dv = configManager.getTemperature(ConfigManager.CHAT_MODEL_LOCALAI);
        if (dv != null)
            builder = builder.temperature(dv);
        dv = configManager.getTopP(ConfigManager.CHAT_MODEL_LOCALAI);
        if (dv != null)
            builder = builder.topP(dv);
        iv = configManager.getInferenceTimeout(ConfigManager.CHAT_MODEL_LOCALAI);
        if (iv != null)
            builder = builder.timeout(Duration.ofSeconds(iv));

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

        if(ConfigManager.CHAT_MODEL_OLLAMA.equalsIgnoreCase(defaultModel))
        {
            log.debug("Using Ollama Chat Model");
            return this.createOllama();
        }

        if(ConfigManager.CHAT_MODEL_LOCALAI.equalsIgnoreCase(defaultModel))
        {
            log.debug("Using Ollama Chat Model");
            return this.createLocalAi();
        }

        // unknown chat model type
        String msg = "Unknown Chat Model Type Requested: " + defaultModel;
        log.error(msg);
        throw new RuntimeException(msg);
    }

    public EmbeddingModel createDefaultEmbeddingModel()
    {
        String defaultModel = configManager.getDefaultChatModel();
        if ((defaultModel == null) || (defaultModel.length() == 0))
        {
            log.warn("No default chat model specified.  Using default for embedding model...");
            defaultModel = ConfigManager.CHAT_MODEL_MISTRAL;
        }

        if(ConfigManager.CHAT_MODEL_MISTRAL.equalsIgnoreCase(defaultModel))
        {
            log.debug("Using Mistral Embedding Model");
            return this.createMistralEmbeddingModel();
        }

        if(ConfigManager.CHAT_MODEL_OPENAI.equalsIgnoreCase(defaultModel))
        {
            log.debug("Using Open AI Embedding Model");
            return this.createOpenAiEmbeddingModel();
        }

        if(ConfigManager.CHAT_MODEL_OLLAMA.equalsIgnoreCase(defaultModel))
        {
            log.debug("Using Ollama Embedding Model");
            return this.createOllamaEmbeddingModel();
        }

        if(ConfigManager.CHAT_MODEL_LOCALAI.equalsIgnoreCase(defaultModel))
        {
            log.debug("Using Ollama Embedding Model");
            return this.createLocalAiEmbeddingModel();
        }

        // unknown chat model type
        String msg = "Unknown Chat Model Type Requested: " + defaultModel + ".  Cannot provide embedding model.";
        log.error(msg);
        throw new RuntimeException(msg);
    }

    public HuggingFaceEmbeddingModel createHuggingFaceEmbeddingModel()
    {
        HuggingFaceEmbeddingModelBuilder builder = HuggingFaceEmbeddingModel.builder()
                .modelId(configManager.getEmbeddingModelName())
                .waitForModel(true)
                .timeout(Duration.ofSeconds(configManager.getInferenceTimeout()));

        if (StringUtils.isNotEmpty(configManager.getHuggingFaceApiKey()))
        {
            builder.accessToken(configManager.getHuggingFaceApiKey());
        }

        return builder.build();
    }
}
