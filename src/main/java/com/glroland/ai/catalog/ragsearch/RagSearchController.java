package com.glroland.ai.catalog.ragsearch;

import java.util.ArrayList;
import java.util.List;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;

import com.glroland.ai.catalog.ChatLanguageModelFactory;
import com.glroland.ai.catalog.product.Product;
import com.glroland.ai.catalog.product.ProductDAO;

import dev.langchain4j.data.document.Document;
import dev.langchain4j.data.document.splitter.DocumentBySentenceSplitter;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.memory.chat.MessageWindowChatMemory;
import dev.langchain4j.model.chat.ChatLanguageModel;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.rag.DefaultRetrievalAugmentor;
import dev.langchain4j.rag.RetrievalAugmentor;
import dev.langchain4j.rag.content.retriever.ContentRetriever;
import dev.langchain4j.rag.content.retriever.EmbeddingStoreContentRetriever;
import dev.langchain4j.rag.query.transformer.CompressingQueryTransformer;
import dev.langchain4j.rag.query.transformer.QueryTransformer;
import dev.langchain4j.service.AiServices;
import dev.langchain4j.store.embedding.EmbeddingStoreIngestor;
import dev.langchain4j.store.embedding.inmemory.InMemoryEmbeddingStore;

@RestController
public class RagSearchController 
{
    private static final Log log = LogFactory.getLog(RagSearchController.class);

    @Autowired
    private ChatLanguageModelFactory chatLanguageModelFactory;

    @Autowired
    private ProductDAO productDAO;

    @PostMapping("/ragsearch")
    private String searchWithRag(String userMessage)
    {
        EmbeddingModel embeddingModel = chatLanguageModelFactory.createOpenAiEmbeddingModel();

        InMemoryEmbeddingStore<TextSegment> embeddingStore = new InMemoryEmbeddingStore<>();
        EmbeddingStoreIngestor ingester = EmbeddingStoreIngestor.builder()
            .documentTransformer(document -> {
                document.metadata().put("userId", "12345");
                return document;
            })
            .documentSplitter(new DocumentBySentenceSplitter(1000, 0))
            .textSegmentTransformer(textSegment -> TextSegment.from(
                textSegment.metadata("file_name") + "\n" + textSegment.text(),
                textSegment.metadata()
            ))
            .embeddingModel(embeddingModel)
            .embeddingStore(embeddingStore)
            .build();

        ArrayList<Document> documents = new ArrayList<Document>();
        List<Product> products = productDAO.search(null, null, "CJ1646-600", null, null);
        if (products != null)
        {
            for (Product product : products)
            {
                Document document = new Document(product.getProductDescription());
                ingester.ingest(document);
                documents.add(document);
            }
        }

        ContentRetriever contentRetriever = EmbeddingStoreContentRetriever.builder()
                .embeddingStore(embeddingStore)
                .embeddingModel(embeddingModel)
                .maxResults(2)
                .minScore(0.6)
                .build();
                
        ChatLanguageModel chatLanguageModel = chatLanguageModelFactory.createOpenAi();

        QueryTransformer queryTransformer = new CompressingQueryTransformer(chatLanguageModel);

        RetrievalAugmentor retrievalAugmentor = DefaultRetrievalAugmentor.builder()
                .queryTransformer(queryTransformer)
                .contentRetriever(contentRetriever)
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
