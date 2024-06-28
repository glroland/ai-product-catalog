package com.glroland.ai.catalog.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

import com.glroland.ai.catalog.service.dao.ProductDAO;
import com.glroland.ai.catalog.service.entities.Product;

@RestController
public class ProductServiceController 
{
    @Autowired
    private ProductDAO productDAO;

    @GetMapping("/")
    public String sayHello()
    {
        return "Hello";
    }

    @GetMapping("/product/{id}")
    public Product getProduct(@PathVariable Integer id)
    {
        return productDAO.getProduct(id);
    }
}
