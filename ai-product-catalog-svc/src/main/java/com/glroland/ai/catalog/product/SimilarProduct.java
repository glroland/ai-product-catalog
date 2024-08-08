package com.glroland.ai.catalog.product;

public class SimilarProduct extends Product
{
    private double distance;
    private double cosignSimilarity;
    private double innerProduct;

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
                          double innerProduct)
    {
        super(productId, sku, brandId, productName, productDescription, size, msrp, categoryId);

        this.distance = distance;
        this.cosignSimilarity = cosignSimilarity;
        this.innerProduct = innerProduct;
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
}
