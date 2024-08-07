package com.glroland.ai.catalog.agent;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.glroland.ai.catalog.ChatLanguageModelFactory;
import com.glroland.ai.catalog.ConfigManager;

import dev.langchain4j.data.message.AiMessage;
import dev.langchain4j.memory.ChatMemory;
import dev.langchain4j.memory.chat.MessageWindowChatMemory;
import dev.langchain4j.memory.chat.TokenWindowChatMemory;
import dev.langchain4j.model.chat.ChatLanguageModel;
import dev.langchain4j.model.openai.OpenAiTokenizer;
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

/*     private void buildChatMemroy()
    {
https://github.com/langchain4j/langchain4j-examples/blob/main/other-examples/src/main/java/ChatMemoryExamples.java
@RequestBody 
        ChatMemory chatMemory = TokenWindowChatMemory.withMaxTokens(300, new OpenAiTokenizer());

        // You have full control over the chat memory.
        // You can decide if you want to add a particular message to the memory
        // (e.g. you might not want to store few-shot examples to save on tokens).
        // You can process/modify the message before saving if required.

        chatMemory.add(userMessage("Hello, my name is Klaus"));
        AiMessage answer = model.generate(chatMemory.messages()).content();
        System.out.println(answer.text()); // Hello Klaus! How can I assist you today?
        chatMemory.add(answer);

        chatMemory.add(userMessage("What is my name?"));
        AiMessage answerWithName = model.generate(chatMemory.messages()).content();
        System.out.println(answerWithName.text()); // Your name is Klaus.
        chatMemory.add(answerWithName);        
    }*/
}
