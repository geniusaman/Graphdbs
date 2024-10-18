examples = [
    {
        "question": "What is the total spend for steel dynamic?",
        "query": "MATCH (s:Supplier {{supplier_name: 'Steel Dynamic'}})-[:SUPPLIES]->(po:PurchaseOrder) RETURN SUM(po.po_amount) AS TotalSpend",
    },
    {
        "question": "What is the total cost for all suppliers?",
        "query": "MATCH (s:Supplier)-[:SUPPLIES]->(po:PurchaseOrder) RETURN s.supplier_name AS Supplier, SUM(po.po_amount) AS TotalCost ORDER BY TotalCost DESC",
    },
    {
        "question": "Who are the top 5 suppliers with the highest supplier rating and their corresponding financial scores?",
        "query": "MATCH (s:Supplier) RETURN s.supplier_name AS Supplier, s.sustainability_score AS SupplierRating, s.financial_score AS FinancialScore ORDER BY s.sustainability_score DESC LIMIT 5",
    },
    {
        "question": "which suppliers have the highest financial score for Service and Product?",
        "query": "MATCH (s:Supplier)-[:OFFERS_SERVICE]->(c:Catalog) WITH DISTINCT s.supplier_name AS Supplier, s.financial_score AS FinancialScore, 'Service' AS Type ORDER BY FinancialScore DESC LIMIT 5 RETURN Supplier, FinancialScore, Type UNION ALL MATCH (s:Supplier)-[:OFFERS_PRODUCT]->(c:Catalog) WITH DISTINCT s.supplier_name AS Supplier, s.financial_score AS FinancialScore, 'Product' AS Type ORDER BY FinancialScore DESC LIMIT 5 RETURN Supplier, FinancialScore, Type",
    },
    {
        "question": "how many catogeries are there and which suppliers offers products and services in what categories",
        "query": "MATCH (c:Catalog) WITH c.supplier_name as supplier, c.category as category, c.parent_category as parent_category WHERE category IS NOT NULL WITH supplier, category, parent_category, COUNT(*) as offering_count WITH COUNT(DISTINCT category) as total_categories, COUNT(DISTINCT parent_category) as total_parent_categories, COLLECT(DISTINCT {{supplier: supplier, category: category, parent_category: parent_category, offering_count: offering_count}}) as supplier_category_details RETURN total_categories, total_parent_categories, supplier_category_details ORDER BY SIZE(supplier_category_details) DESC",
    },
    {
        "question": "how many catogeries are there and which suppliers offers products and services in what categories",
        "query":"MATCH (c:Catalog) WITH c.supplier_name as supplier, c.category as category, c.parent_category as parent_category WHERE category IS NOT NULL WITH supplier, category, parent_category, COUNT(*) as offering_count WITH COUNT(DISTINCT category) as total_categories, COUNT(DISTINCT parent_category) as total_parent_categories, COLLECT(DISTINCT {{supplier: supplier, category: category, parent_category: parent_category, offering_count: offering_count}}) as supplier_category_details RETURN total_categories, total_parent_categories, supplier_category_details ORDER BY SIZE(supplier_category_details) DESC",

    },
    {
        "question": "Get more information about a Ground freight category",
        "query":"MATCH (c:Catalog) WHERE toLower(c.category) CONTAINS 'freight' OR toLower(c.parent_category) CONTAINS 'freight' OR toLower(c.service_name) CONTAINS 'freight' RETURN c.category, c.parent_category, c.service_name, c.equipment, c.route, c.base_rate_per_mile, c.fuel_surcharge, c.detention_rate_per_hour, c.liftgate_service_rate, c.additional_services, c.special_instructions, c.supplier_name, c.currency, c.lead_time, c.distance_miles LIMIT 10",

    },
    ]

print(examples)