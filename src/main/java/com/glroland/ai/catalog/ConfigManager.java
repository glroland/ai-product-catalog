package com.glroland.ai.catalog;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.env.Environment;
import org.springframework.stereotype.Component;

import io.micrometer.common.util.StringUtils;

@Component
public class ConfigManager 
{
    private static final Log log = LogFactory.getLog(ConfigManager.class);
    
    @Autowired
    private Environment env;

    public static final String CONFIG_GROUP = "ai-product-catalog";

    public static final String CONFIG_ENTRY_ENDPOINT = "inference-endpoint";
    public static final String CONFIG_ENTRY_APIKEY = "api-key";
    public static final String CONFIG_ENTRY_MODEL_NAME = "model-name";
    public static final String CONFIG_ENTRY_MAX_TOKENS = "max-tokens";
    public static final String CONFIG_ENTRY_TIMEOUT = "timeout-seconds";
    public static final String CONFIG_ENTRY_TEMP = "temperature";
    public static final String CONFIG_ENTRY_TOP_P = "top-p";

    public static final String CHAT_MODEL_MISTRAL = "mistral";
    public static final String CHAT_MODEL_OPENAI = "openai";
    public static final String CHAT_MODEL_OLLAMA = "ollama";
    public static final String CHAT_MODEL_LOCALAI = "localai";

    public static final String AGENT_TYPE_SIMPLE = "simple";
    public static final String AGENT_TYPE_TOOL = "tool";
    public static final String AGENT_TYPE_RAG = "rag";

    private String getValue(String chatModel, String propertyName)
    {
        // order of precidence - chat model override first
        if (StringUtils.isNotEmpty(chatModel))
        {
            String value = env.getProperty(CONFIG_GROUP + "." + chatModel + "." + propertyName);
            if (value != null)
            {
                log.debug("Configured Value -- [" + chatModel + "] [propertyName=" + propertyName + "] [value=" + value + "]");                
                return value;
            }
        }
            
        // order of precidence - root override second
        String value = env.getProperty(CONFIG_GROUP + "." + chatModel + "." + propertyName);
        log.debug("Configured Value -- [DEFAULT] [propertyName=" + propertyName + "] [value=" + value + "]");                
        return value;
    }

    public String getInferenceEndpoint()
    {
        return getInferenceEndpoint("");
    }

    public String getInferenceEndpoint(String chatModel)
    {
        return getValue(chatModel, CONFIG_ENTRY_ENDPOINT);
    }

    public String getInferenceApiKey()
    {
        return getInferenceApiKey("");
    }

    public String getInferenceApiKey(String chatModel)
    {
        return getValue(chatModel, CONFIG_ENTRY_APIKEY);
    }

    public String getModelName()
    {
        return getModelName("");
    }

    public String getModelName(String chatModel)
    {
        return getValue(chatModel, CONFIG_ENTRY_MODEL_NAME);
    }

    public Integer getMaxTokens()
    {
        return getMaxTokens("");
    }

    public Integer getMaxTokens(String chatModel)
    {
        String value = getValue(chatModel, CONFIG_ENTRY_MAX_TOKENS);
        if (value == null)
            return null;
        return Integer.valueOf(value);
    }

    public Integer getInferenceTimeout()
    {
        return getInferenceTimeout("");
    }

    public Integer getInferenceTimeout(String chatModel)
    {
        String value = getValue(chatModel, CONFIG_ENTRY_TIMEOUT);
        if (value == null)
            return null;
        return Integer.valueOf(value);
    }

    public Double getTemperature()
    {
        return getTemperature("");
    }

    public Double getTemperature(String chatModel)
    {
        String value = getValue(chatModel, CONFIG_ENTRY_TEMP);
        if (value == null)
            return null;
        return Double.valueOf(value);
    }

    public Double getTopP()
    {
        return getTopP("");
    }

    public Double getTopP(String chatModel)
    {
        String value = getValue(chatModel, CONFIG_ENTRY_TOP_P);
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
