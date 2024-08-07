package com.glroland.ai.catalog.ragagent;

import java.sql.Array;
import java.sql.SQLException;

import org.apache.commons.lang3.StringUtils;

public class ProductEmbedding 
{
    private int productId;
    private String model;
    private String textSegment;
    private float [] embedding;
    
    public ProductEmbedding(int productId, String model, String textSegment, String embeddingStr) {
        this.productId = productId;
        this.model = model;
        this.textSegment = textSegment;

        this.setEmbedding(embeddingStr);
    }

    public int getProductId() {
        return productId;
    }
    public void setProductId(int productId) {
        this.productId = productId;
    }
    public String getModel() {
        return model;
    }
    public void setModel(String model) {
        this.model = model;
    }
    public String getTextSegment() {
        return textSegment;
    }
    public void setTextSegment(String textSegment) {
        this.textSegment = textSegment;
    }
    public float[] getEmbedding() {
        return embedding;
    }
    public void setEmbedding(float[] embedding) {
        this.embedding = embedding;
    }

    public void setEmbedding(String embeddingStr)
    {
        this.embedding = null;
        if (StringUtils.isNotEmpty(embeddingStr))
        {
            String[] tokens = embeddingStr.substring(1, embeddingStr.length() - 1).split(",");
            this.embedding = new float[tokens.length];
            for (int i = 0; i < tokens.length; i++) 
            {
                this.embedding[i] = Float.parseFloat(tokens[i]);
            }
        }
    }
}
