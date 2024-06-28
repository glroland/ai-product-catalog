package com.glroland.ai.catalog.service;

import java.util.ArrayList;
import java.util.List;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.glroland.ai.catalog.service.dao.ProductDAO;
import com.glroland.ai.catalog.service.entities.Product;

@RestController
public class ProductServiceController 
{
    private static final Log log = LogFactory.getLog(ProductServiceController.class);
    
    @Autowired
    private ProductDAO productDAO;

    @GetMapping("/greeting")
    public String greeting()
    {
        return "Hello!";
    }

    @GetMapping("/product/{id}")
    public Product getProduct(@PathVariable Integer id)
    {
        return productDAO.getProduct(id);
    }

    @PostMapping("/search")
    public List<Product> search(@RequestParam(value="category", required=false) String category,
                                @RequestParam(value="brand", required=false) String brand,
                                @RequestParam(value="sku", required=false) String sku,
                                @RequestParam(value="size", required=false) String size,
                                @RequestParam(value="nameDesc", required=false) String nameDesc
     )
    {
        log.info("Search API called with the following parameters: category=" + category + " brand=" + brand + " sku=" + sku + " size=" + size + " nameDesc=" + nameDesc);

        List<Product> products = productDAO.search(category, brand, sku, size, nameDesc);
        log.info("# of Search Results: " + products.size());

        return products;
    }
}
