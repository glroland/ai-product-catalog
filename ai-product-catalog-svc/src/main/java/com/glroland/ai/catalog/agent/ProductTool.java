package com.glroland.ai.catalog.agent;

import java.time.LocalTime;
import java.util.ArrayList;
import java.util.List;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import com.glroland.ai.catalog.product.Product;
import com.glroland.ai.catalog.product.ProductDAO;

//import dev.langchain4j.agent.tool.P;
import dev.langchain4j.agent.tool.Tool;

@Component
public class ProductTool 
{
    private static final Log log = LogFactory.getLog(ProductTool.class);

    @Autowired
    private ProductDAO productDao;

    @Tool("Get the current date and time")
    public String getCurrentTime() 
    {
        String response = LocalTime.now().toString();
        log.info("Product Tool Called.  currentTime Response=" + response);
        return response;
    }

    @Tool("Get the price for the product associated with a SKU")
    public Double getProductPrice(String sku)
    {
        log.info("Product Tool Called.  SKU = " + sku);
        Product product = productDao.getProductBySKU(sku);
        if (product == null)
        {
            log.warn("No product found for SKU.  SKU=" + sku);
            return null;
        }

        return product.getMsrp();
    }

    @Tool("Get a list of all of Nike's shoes, available for sale or not.  Shoes are provided by a list of SKUs.")
    public List<String> getNikeShoes()
    {
        ArrayList<String> skus = new ArrayList<String>();

        List<Product> products = productDao.search("Shoes", "Nike", null, null, null);
        if (products != null)
        {
            for (Product product : products)
            {
                skus.add(product.getSku());
            }
        }

        return skus;
    }
}
