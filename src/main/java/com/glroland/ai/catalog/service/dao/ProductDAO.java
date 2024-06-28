package com.glroland.ai.catalog.service.dao;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

import com.glroland.ai.catalog.service.entities.Product;

@Component
public class ProductDAO {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    public Product getProduct(int id)
    {
        String sql = "SELECT product_id, "
                          + "product_code, "
                          + "brand_id, " 
                          + "product_name, "
                          + "product_desc, "
                          + "size, "
                          + "msrp, "
                          + "category_id "
                    + "FROM products "
                    + "WHERE product_id = ?";

        List<Product> products = (List<Product>)jdbcTemplate.query(
            sql,
            (rs, rowNum) -> new Product(rs.getInt("product_id"), 
                                        rs.getString("product_code"), 
                                        rs.getInt("brand_id"), 
                                        rs.getString("product_name"), 
                                        rs.getString("product_desc"), 
                                        rs.getString("size"), 
                                        rs.getDouble("msrp"), 
                                        rs.getInt("category_id")),
            id);

        if ((products == null) || (products.size() == 0))
            return null;

        if (products.size() > 1)
            throw new RuntimeException("More than one product found with ID.  Unexpected...");

        return products.get(0);
    }
}
