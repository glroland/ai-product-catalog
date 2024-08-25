package com.glroland.ai.catalog.similaritysearch;

import java.util.List;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.glroland.ai.catalog.ChatLanguageModelFactory;
import com.glroland.ai.catalog.product.Product;
import com.glroland.ai.catalog.product.SimilarProduct;
import com.glroland.ai.catalog.product.ProductDAO;

import dev.langchain4j.data.embedding.Embedding;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.openai.OpenAiEmbeddingModel;
import dev.langchain4j.model.output.Response;

@RestController
public class SimilaritySearchController 
{
    private static final Log log = LogFactory.getLog(SimilaritySearchController.class);

    @Autowired
    private ChatLanguageModelFactory chatLanguageModelFactory;

    @Autowired
    private ProductDAO productDAO;

    @PostMapping("/similaritysearch")
    public List<SimilarProduct> similaritySearch(@RequestParam(value = "userMessage") 
                        String userMessage,
                        @RequestParam(value = "limit", defaultValue = "5") 
                        int limit)
    {
        log.info("Performing similarity search.  UserMessage='" + userMessage + "' Limit=" + limit);

        // encode the user message
        EmbeddingModel model = this.chatLanguageModelFactory.createHuggingFaceEmbeddingModel();
        Response<Embedding> response = model.embed(userMessage);
        Embedding embedding = response.content();
        log.debug("Embedding for text.  Text='" + userMessage + "' Embedding=" + embedding + " Vector=" + embedding.vector());

        // query for similarity
        return productDAO.similaritySearch(embedding.vector(), limit);
    }
}
