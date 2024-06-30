package com.glroland.ai.catalog;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.env.Environment;
import org.springframework.stereotype.Component;

@Component
public class ConfigManager 
{
    private static final Log log = LogFactory.getLog(ConfigManager.class);
    
    @Autowired
    private Environment env;

    public static final String CHAT_MODEL_MISTRAL = "mistral";
    public static final String CHAT_MODEL_OPENAI = "openai";

    public String getInferenceEndpoint()
    {
        String value = env.getProperty("ai-product-catalog.inference-endpoint");
        log.debug("Configured Endpoint URL = " + value);
        return value;
    }

    public String getInferenceApiKey()
    {
        String value = env.getProperty("ai-product-catalog.api-key");
        log.debug("Configured API Key = " + value);
        return value;
    }

    public String getModelName()
    {
        String value = env.getProperty("ai-product-catalog.model-name");
        log.debug("Configured Model Name = " + value);
        return value;
    }

    public Integer getMaxTokens()
    {
        String value = env.getProperty("ai-product-catalog.max-tokens");
        log.debug ("Configured Max Tokens = " + value);

        if (value == null)
            return null;
        return Integer.valueOf(value);
    }

    public Integer getInferenceTimeout()
    {
        String value = env.getProperty("ai-product-catalog.timeout-seconds");
        log.debug("Configured Inference Timeout = " + value);

        if (value == null)
            return null;
        return Integer.valueOf(value);
    }

    public Double getTemperature()
    {
        String value = env.getProperty("ai-product-catalog.temperature");
        log.debug("Configured Temperature = " + value);

        if (value == null)
            return null;
        return Double.valueOf(value);
    }

    public Double getTopP()
    {
        String value = env.getProperty("ai-product-catalog.top-p");
        log.debug("Configured Top-P = " + value);

        if (value == null)
            return null;
        return Double.valueOf(value);
    }

    public String getDefaultChatModel()
    {
        String value = env.getProperty("ai-product-catalog.default-chat-model");
        log.debug("Configured Default Chat Model = " + value);
        return value;
    }
}
