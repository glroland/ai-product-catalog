package com.glroland.ai.catalog.agent;

import java.time.LocalTime;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.stereotype.Component;

//import dev.langchain4j.agent.tool.P;
import dev.langchain4j.agent.tool.Tool;

@Component
public class ProductTool 
{
    private static final Log log = LogFactory.getLog(ProductTool.class);

    @Tool("Get the current date and time")
    public String getCurrentTime() 
    {
        String response = LocalTime.now().toString();
        log.info("Product Tool Called.  currentTime Response=" + response);
        return response;
    }            
}
