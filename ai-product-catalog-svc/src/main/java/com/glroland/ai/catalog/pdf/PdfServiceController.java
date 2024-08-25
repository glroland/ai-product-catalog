package com.glroland.ai.catalog.pdf;

import java.io.DataInputStream;
import java.io.IOException;
import java.util.List;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import com.glroland.ai.catalog.ChatLanguageModelFactory;

import dev.langchain4j.data.document.Document;
import dev.langchain4j.data.document.parser.apache.pdfbox.ApachePdfBoxDocumentParser;
import dev.langchain4j.data.document.splitter.DocumentByParagraphSplitter;
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
public class PdfServiceController 
{
    private static final Log log = LogFactory.getLog(PdfServiceController.class);

    public static final int MAX_SEGMENT_SIZE_IN_CHARS = 10000;
    public static final int MAX_OVERLAP_SIZE_IN_CHARS = 200;

    @Autowired
    private ChatLanguageModelFactory chatLanguageModelFactory;

    @PostMapping(path = "/upload", produces = "text/plain")
    public @ResponseBody String upload(@RequestParam(value = "textSegmentPrompt") String textSegmentPrompt, 
                                       @RequestParam(value = "summarizationPrompt") String summarizationPrompt, 
                                       @RequestParam("file") MultipartFile file, 
                                       RedirectAttributes redirectAttributes)
    {
        // log user prompt
        log.info("User Prompts....  textSegmentPrompt: " + textSegmentPrompt + " summarizationPrompt: " + summarizationPrompt);

        // process upload
        log.debug("Upload initiated.  Beginning receipt and conversion to PDF");
        Document document = this.parsePDFUpload(file);
        log.info ("Upload complete.  Converted from PDF to Langchain4j Document.");
        log.info("Document Contents: " + document.text());

        // split document into chunks
        DocumentByParagraphSplitter docSplitter = new DocumentByParagraphSplitter(MAX_SEGMENT_SIZE_IN_CHARS, MAX_OVERLAP_SIZE_IN_CHARS);
        List<TextSegment> textSegments = docSplitter.split(document);
        if ((textSegments == null) || (textSegments.size() == 0))
        {
            String msg = "Resulting text segments list from split is empty!";
            log.error(msg);
            throw new RuntimeException(msg);
        }
        log.info("DocumentSizeInBytes=" + document.text().length() + " TextSegmentsArrayLength=" + textSegments.size());

        // summarize each chunk
        StringBuffer responses = new StringBuffer();
        for (TextSegment textSegment : textSegments)
        {
            log.debug("Summarizing Chunk: " + textSegment.text());
            String chunk = summarizeChunk(textSegmentPrompt, textSegment);
            log.info("Summarized Chunk....  TextSegment=" + textSegment.text() + " Summary=" + chunk);
            responses.append(chunk).append("  ");
        }

        // summarize all the summaries with the other prompt
        log.debug("Summarizing Document: " + responses.toString());
        String summary = summarizeChunk(summarizationPrompt, responses.toString());
        log.info ("Summarized Document...  " + summary);

        return summary;
    }

    private Embedding createEmbedding(EmbeddingModel embeddingModel, TextSegment content)
    {
        Response<Embedding> embeddingResponse = embeddingModel.embed(content);
        if (embeddingResponse == null)
        {
            String message = "Unable to create embedding for content due to null response: " + content;
            log.error(message);
            throw new RuntimeException(message);
        }
        Embedding embedding = embeddingResponse.content();
        if (embedding == null)
        {
            String message = "Unable to create embedding for content due to empty embedding in response: " + content;
            log.error(message);
            throw new RuntimeException(message);
        }

        return embedding;
    }

    private Embedding createEmbedding(EmbeddingModel embeddingModel, String content)
    {
        return createEmbedding(embeddingModel, TextSegment.from(content));
    }

    private String summarizeChunk(String prompt, String content)
    {
        return summarizeChunk(prompt, TextSegment.from(content));
    }

    private String summarizeChunk(String prompt, TextSegment textSegment)
    {
        EmbeddingModel embeddingModel = chatLanguageModelFactory.createDefaultEmbeddingModel();
        Embedding promptEmbedding = createEmbedding(embeddingModel, prompt);

        // Encode text segment
        InMemoryEmbeddingStore<TextSegment> embeddingStore = new InMemoryEmbeddingStore<>();
        Embedding textSegmentEmbedding = createEmbedding(embeddingModel, textSegment);
        embeddingStore.add(textSegmentEmbedding, textSegment);

        // Send related embeddings to LLM for inclusion in user message
        ChatLanguageModel chatLanguageModel = chatLanguageModelFactory.createDefault();
        
        ContentRetriever contentRetriever = EmbeddingStoreContentRetriever.builder()
                .embeddingStore(embeddingStore)
                .embeddingModel(embeddingModel)
                .build();
                
        DefaultQueryRouter queryRouter = new DefaultQueryRouter(contentRetriever);
        
        RetrievalAugmentor retrievalAugmentor = DefaultRetrievalAugmentor.builder()
                .queryRouter(queryRouter)
                .build();

        SummarizerChatAgent agent = AiServices.builder(SummarizerChatAgent.class)
                .chatLanguageModel(chatLanguageModel)
                .retrievalAugmentor(retrievalAugmentor)
                .chatMemory(MessageWindowChatMemory.withMaxMessages(10))
                .build();
        
        String answer = agent.chat(prompt);
        log.info("Prompt = '" + prompt + "'  Response = '" + answer + "'");

        return answer;
    }

    private Document parsePDFUpload(MultipartFile file) 
    {
		try 
        {
			if (file.isEmpty()) 
            {
                String msg = "Unable to store empty file, or at least not trying to!";
                log.error(msg);
                throw new RuntimeException(msg);
			}

            ApachePdfBoxDocumentParser pdfParser = new ApachePdfBoxDocumentParser();
			DataInputStream inputStream = new DataInputStream(file.getInputStream());
            return pdfParser.parse(inputStream); 
		}
		catch (IOException e) 
        {
            String msg = "Unable to obtain and process input file";
            log.error(msg, e);
            throw new RuntimeException(msg, e);
		}
	}
}
