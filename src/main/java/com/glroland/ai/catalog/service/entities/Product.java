package com.glroland.ai.catalog.service.entities;

public class Product 
{
    private int productId;
    private String productCode;
    private int brandId;
    private String productName;
    private String productDescription;
    private String size;
    private double msrp;
    private int categoryId;

    public Product(int productId, String productCode, int brandId, String productName, String productDescription,
            String size, double msrp, int categoryId) {
        this.productId = productId;
        this.productCode = productCode;
        this.brandId = brandId;
        this.productName = productName;
        this.productDescription = productDescription;
        this.size = size;
        this.msrp = msrp;
        this.categoryId = categoryId;
    }

    public int getProductId() {
        return productId;
    }
    public void setProductId(int productId) {
        this.productId = productId;
    }
    public String getProductCode() {
        return productCode;
    }
    public void setProductCode(String productCode) {
        this.productCode = productCode;
    }
    public int getBrandId() {
        return brandId;
    }
    public void setBrandId(int brandId) {
        this.brandId = brandId;
    }
    public String getProductName() {
        return productName;
    }
    public void setProductName(String productName) {
        this.productName = productName;
    }
    public String getProductDescription() {
        return productDescription;
    }
    public void setProductDescription(String productDescription) {
        this.productDescription = productDescription;
    }
    public String getSize() {
        return size;
    }
    public void setSize(String size) {
        this.size = size;
    }
    public double getMsrp() {
        return msrp;
    }
    public void setMsrp(double msrp) {
        this.msrp = msrp;
    }
    public int getCategoryId() {
        return categoryId;
    }
    public void setCategoryId(int categoryId) {
        this.categoryId = categoryId;
    }
}
