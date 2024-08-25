package com.glroland.ai.catalog.ragagent;

import java.util.List;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.glroland.ai.catalog.ChatLanguageModelFactory;
import com.glroland.ai.catalog.product.Product;
import com.glroland.ai.catalog.product.ProductDAO;
import com.glroland.ai.catalog.product.SimilarProduct;

import dev.langchain4j.data.document.Metadata;
import dev.langchain4j.data.embedding.Embedding;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.memory.chat.MessageWindowChatMemory;
import dev.langchain4j.model.chat.ChatLanguageModel;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.output.Response;
import dev.langchain4j.rag.DefaultRetrievalAugmentor;
import dev.langchain4j.rag.RetrievalAugmentor;
import dev.langchain4j.rag.content.retriever.ContentRetriever;
import dev.langchain4j.rag.content.retriever.EmbeddingStoreContentRetriever;
import dev.langchain4j.rag.query.router.DefaultQueryRouter;
import dev.langchain4j.service.AiServices;
import dev.langchain4j.store.embedding.inmemory.InMemoryEmbeddingStore;

@RestController
public class RagChatServiceController 
{
    private static final Log log = LogFactory.getLog(RagChatServiceController.class);

    private static final int LIMIT = 5;

    @Autowired
    private ChatLanguageModelFactory chatLanguageModelFactory;

    @Autowired
    private ProductDAO productDAO;

    @PostMapping("/ragchat")
    public String chatWithRag(@RequestParam(value = "userMessage") String userMessage)
    {
        EmbeddingModel hfEmbeddingModel = chatLanguageModelFactory.createHuggingFaceEmbeddingModel();

        // Encode user message
        Response<Embedding> hfUserMessageEmbeddingResponse = hfEmbeddingModel.embed(userMessage);
        if (hfUserMessageEmbeddingResponse == null)
        {
            String message = "Unable to create embedding for userMessage due to null response: " + userMessage;
            log.error(message);
            throw new RuntimeException(message);
        }
        Embedding hfUserMessageEmbedding = hfUserMessageEmbeddingResponse.content();
        if (hfUserMessageEmbedding == null)
        {
            String message = "Unable to create embedding for userMessage due to empty embedding in response: " + userMessage;
            log.error(message);
            throw new RuntimeException(message);
        }

        // Find and store related embeddings
        List<SimilarProduct> similarProducts = productDAO.similaritySearch(hfUserMessageEmbedding.vector(), LIMIT);

        EmbeddingModel embeddingModel = chatLanguageModelFactory.createDefaultEmbeddingModel();

        // process matches
        InMemoryEmbeddingStore<TextSegment> embeddingStore = new InMemoryEmbeddingStore<>();
        if (similarProducts != null)
        {
            for (Product product : similarProducts)
            {
                String text = product.getProductName() + " " + product.getProductDescription();
                Response<Embedding> productEmbeddingResponse = embeddingModel.embed(text);
                if (productEmbeddingResponse == null)
                {
                    String message = "Unable to create embedding for product text segment due to null response: " + text;
                    log.error(message);
                    throw new RuntimeException(message);
                }
                Embedding e = productEmbeddingResponse.content();

                Metadata md = new Metadata();
                TextSegment ts = new TextSegment(text, md);
                embeddingStore.add(e, ts);
            }
        }

        // Send related embeddings to LLM for inclusion in user message
        ChatLanguageModel chatLanguageModel = chatLanguageModelFactory.createDefault();

        ContentRetriever contentRetriever = EmbeddingStoreContentRetriever.builder()
                .embeddingStore(embeddingStore)
                .embeddingModel(embeddingModel)
//                .maxResults(2)
//                .minScore(0.6)
                .build();
        
                DefaultQueryRouter queryRouter = new DefaultQueryRouter(contentRetriever);
                
                RetrievalAugmentor retrievalAugmentor = DefaultRetrievalAugmentor.builder()
                .queryRouter(queryRouter)
                .build();
                                

        RagEnabledChatAgent agent = AiServices.builder(RagEnabledChatAgent.class)
                .chatLanguageModel(chatLanguageModel)
                .retrievalAugmentor(retrievalAugmentor)
                .chatMemory(MessageWindowChatMemory.withMaxMessages(10))
                .build();
        
        String answer = agent.chat(userMessage);
        log.info("User Message = '" + userMessage + "'  Response = '" + answer + "'");

        return answer;
    }
}
