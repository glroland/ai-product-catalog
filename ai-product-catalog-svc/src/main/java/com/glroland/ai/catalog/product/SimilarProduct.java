package com.glroland.ai.catalog.product;

public class SimilarProduct extends Product
{
    private double distance;
    private double cosignSimilarity;
    private double innerProduct;
    private String textSegment;

    public SimilarProduct(int productId, 
                          String sku, 
                          int brandId, 
                          String productName, 
                          String productDescription,
                          String size, 
                          double msrp, 
                          int categoryId,
                          double distance,
                          double cosignSimilarity,
                          double innerProduct,
                          String textSegment)
    {
        super(productId, sku, brandId, productName, productDescription, size, msrp, categoryId);

        this.distance = distance;
        this.cosignSimilarity = cosignSimilarity;
        this.innerProduct = innerProduct;
        this.textSegment = textSegment;
    }

    public double getDistance() 
    {
        return distance;
    }

    public void setDistance(double distance) 
    {
        this.distance = distance;
    }

    public double getCosignSimilarity() 
    {
        return cosignSimilarity;
    }

    public void setCosignSimilarity(double cosignSimilarity) 
    {
        this.cosignSimilarity = cosignSimilarity;
    }

    public double getInnerProduct() {
        return innerProduct;
    }

    public void setInnerProduct(double innerProduct) {
        this.innerProduct = innerProduct;
    }

    public String getTextSegment() {
        return textSegment;
    }

    public void setTextSegment(String textSegment) {
        this.textSegment = textSegment;
    }
}
