package com.glroland.ai.catalog.agent;

import java.util.ArrayList;
import java.util.List;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.glroland.ai.catalog.ConfigManager;
import com.glroland.ai.catalog.product.Product;
import com.glroland.ai.catalog.product.ProductDAO;

import dev.langchain4j.data.document.Document;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.memory.chat.MessageWindowChatMemory;
import dev.langchain4j.model.chat.ChatLanguageModel;
import dev.langchain4j.rag.content.retriever.ContentRetriever;
import dev.langchain4j.rag.content.retriever.EmbeddingStoreContentRetriever;
import dev.langchain4j.service.AiServices;
import dev.langchain4j.store.embedding.EmbeddingStoreIngestor;
import dev.langchain4j.store.embedding.inmemory.InMemoryEmbeddingStore;
import dev.langchain4j.model.embedding.EmbeddingModel;

import io.micrometer.common.util.StringUtils;

@RestController
public class ChatServiceController 
{
    private static final Log log = LogFactory.getLog(ChatServiceController.class);

    @Autowired
    private ProductTool productTool;

    @Autowired
    private ChatLanguageModelFactory chatLanguageModelFactory;

    @Autowired
    private ProductDAO productDAO;

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

        if (ConfigManager.AGENT_TYPE_RAG.equals(type))
        {
            log.info("Chatting w/RAG-enhanced Chat Engine - No tools, only document embedding");
            return chatWithRag(userMessage);
        }

        // unknown chat engine type specified
        String msg = "Unknown Agent Type Specified.  Type = " + type;
        log.error(msg);
        throw new RuntimeException(msg);
    }

    private String chatWithRag(String userMessage)
    {
        ArrayList<Document> documents = new ArrayList<Document>();
        List<Product> products = productDAO.search(null, null, null, null, null);
        if (products != null)
        {
            for (Product product : products)
            {
                Document document = new Document(product.getProductDescription());
                documents.add(document);
            }
        }

        EmbeddingModel embeddingModel = chatLanguageModelFactory.createMistralEmbeddingModel();
        InMemoryEmbeddingStore<TextSegment> embeddingStore = new InMemoryEmbeddingStore<>();
        EmbeddingStoreIngestor.ingest(documents, embeddingStore);

        ContentRetriever contentRetriever = EmbeddingStoreContentRetriever.builder()
                .embeddingStore(embeddingStore)
                .embeddingModel(embeddingModel)
                .maxResults(2)
                .minScore(0.6)
                .build();
                
        ChatLanguageModel chatLanguageModel = chatLanguageModelFactory.createMistral();

        RagEnabledChatAgent agent = AiServices.builder(RagEnabledChatAgent.class)
                .chatLanguageModel(chatLanguageModel)
                .contentRetriever(contentRetriever)
                .chatMemory(MessageWindowChatMemory.withMaxMessages(10))
                .build();
        
        String answer = agent.chat(userMessage);
        log.info("User Message = '" + userMessage + "'  Response = '" + answer + "'");

        return answer;
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
        ChatLanguageModel chatLanguageModel = chatLanguageModelFactory.createDefault();

        SimpleChatAgent agent = AiServices.builder(SimpleChatAgent.class)
                .chatLanguageModel(chatLanguageModel)
                .chatMemory(MessageWindowChatMemory.withMaxMessages(10))
                .build();
        
        String answer = agent.chat(userMessage);
        log.info("User Message = '" + userMessage + "'  Response = '" + answer + "'");

        return answer;
    }
}
