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
        "question": "Get more information about a Ground freight category",
        "query":"MATCH (c:Catalog) WHERE toLower(c.category) CONTAINS 'freight' OR toLower(c.parent_category) CONTAINS 'freight' OR toLower(c.service_name) CONTAINS 'freight' RETURN c.category, c.parent_category, c.service_name, c.equipment, c.route, c.base_rate_per_mile, c.fuel_surcharge, c.detention_rate_per_hour, c.liftgate_service_rate, c.additional_services, c.special_instructions, c.supplier_name, c.currency, c.lead_time, c.distance_miles LIMIT 10",

    },
    {
        "question": "How has my total procurement spend changed over the last 3 years?",
        "query":"MATCH (s:Supplier)-[r:SUPPLIES]->(po:PurchaseOrder) WHERE po.product_name CONTAINS '410 Stainless Round Bar 1' WITH DISTINCT s, COUNT(po) as order_count, COLLECT(DISTINCT {{ po_number: po.po_number, quantity: po.quantity, unit_price: po.unit_price, order_date: po.po_date }}) as order_details RETURN 'Active Supplier' as status, s.supplier_name as supplier_name, s.supplier_id as supplier_id, s.country as country, s.contact_number as contact, s.email as email, s.financial_score as financial_score, s.sustainability_score as sustainability_score, order_count as total_orders, order_details as purchase_details UNION MATCH (s:Supplier)-[:OFFERS_PRODUCT]->(c:Catalog) WHERE c.product_name CONTAINS '410 Stainless Round Bar 1' AND NOT EXISTS {{ MATCH (s)-[:SUPPLIES]->(:PurchaseOrder {{product_name: '410 Stainless Round Bar 1'}}) }} RETURN 'Catalog Only' as status, s.supplier_name as supplier_name, s.supplier_id as supplier_id, s.country as country, s.contact_number as contact, s.email as email, s.financial_score as financial_score, s.sustainability_score as sustainability_score, 0 as total_orders, COLLECT({{ catalog_price: c.unit_price, lead_time: c.lead_time }}) as purchase_details;",

    },
    {
        "question": "How many POs are tied to contracts that are ending this year?",
        "query": "MATCH (po:PurchaseOrder)-[:SUPPLIES]-(s:Supplier)-[:HAS_CONTRACT]->(c:Contract) WHERE datetime(c.contract_end_date).year = datetime().year RETURN c.contract_id, c.supplier_name, c.category, datetime(c.contract_end_date) as end_date, COUNT(po) as number_of_pos, SUM(po.po_amount) as total_po_value ORDER BY end_date;",
    },
    {
        "question": "who is the cheapest supplier for Products?",
        "query": "MATCH (s:Supplier)-[o:OFFERS_PRODUCT]->(c:Catalog) WHERE c.unit_price IS NOT NULL WITH s, c, o, toFloat(c.unit_price) AS price ORDER BY price ASC WITH s, collect({{productName: c.product_name, price: price, poAmount: o.po_amount}})[0] AS cheapestProduct RETURN s.supplier_name AS supplier_name, cheapestProduct.productName AS product_name, cheapestProduct.price AS unit_price, s.sustainability_score AS sustainability_score, cheapestProduct.poAmount AS total_spend ORDER BY cheapestProduct.price ASC LIMIT 5",
    },
    {
        "question": "who is the cheapest supplier for Tranasport Services?",
        "query": "MATCH (s:Supplier)-[o:OFFERS_SERVICE]->(c:Catalog) WHERE c.base_rate_per_mile IS NOT NULL WITH s, c, o, toFloat(c.base_rate_per_mile) AS price ORDER BY price ASC WITH s, collect({{serviceName: c.service_name, price: price, poAmount: o.po_amount}})[0] AS cheapestService RETURN s.supplier_name AS supplier_name, cheapestService.serviceName AS service_name, cheapestService.price AS base_rate_per_mile, s.sustainability_score AS sustainability_score, cheapestService.poAmount AS total_spend ORDER BY cheapestService.price ASC LIMIT 5",
    },
    {
        "question": "whO is the cheapest supplier for Cloud migration?",
        "query": "MATCH (po:PurchaseOrder)-[:SUPPLIES]-(s:Supplier) WHERE ANY(keyword IN ['cloud migration', 'cloud', 'migration', 'cloud services'] WHERE toLower(po.category) CONTAINS toLower(keyword) OR toLower(po.parent_category) CONTAINS toLower(keyword)) WITH s, po.supplier_name as supplier_name, SUM(po.po_amount) as total_spend, COUNT(po) as order_count, AVG(po.financial_score) as financial_score, s.sustainability_score as sustainability_score RETURN supplier_name, round(total_spend / order_count, 2) as average_cost_per_order, order_count as number_of_orders, round(total_spend, 2) as total_spend, round(financial_score, 2) as financial_score, round(sustainability_score, 2) as sustainability_score ORDER BY average_cost_per_order ASC LIMIT 5;",
    },
    {
        "question": "What is the sum of TotalCost for all suppliers, along with the individual supplier costs?",
        "query": "MATCH (s:Supplier)-[:SUPPLIES]->(po:PurchaseOrder) WITH s.supplier_name AS Supplier, SUM(po.po_amount) AS SupplierTotalCost WITH COLLECT({{Supplier: Supplier, TotalCost: SupplierTotalCost}}) AS SupplierCosts, SUM(SupplierTotalCost) AS GrandTotal RETURN {{GrandTotal: GrandTotal, SupplierCosts: SupplierCosts}} AS Result",
    },
        {   "question":"Which contracts are expiring within the next 3 months?",
         "query":"MATCH (c:Contract) WHERE datetime(c.contract_end_date) >= datetime('2024-10-21T00:00:00') AND datetime(c.contract_end_date) <= datetime('2025-01-21T00:00:00') RETURN c.contract_id, c.supplier_name, c.category, c.contract_value, c.contract_end_date as expiry_date ORDER BY expiry_date ASC",

    },
    {   "question":"Which suppliers are offering the best payment terms (e.g., early payment discounts)?",
         "query":"MATCH (s:Supplier)-[:SUPPLIES]->(po:PurchaseOrder) WHERE po.payment_terms CONTAINS 'discount' RETURN DISTINCT s.supplier_name, po.payment_terms, s.financial_score, COUNT(po) as number_of_orders, ROUND(AVG(po.po_amount) * 100) / 100.0 as average_order_amount ORDER BY s.financial_score DESC",

    },
    {   "question":"for API Development and Integration Service What are the prices in 2024 and 2023?",
         "query":"MATCH (po:PurchaseOrder)-[:CREATED_ON]->(d:Date) WHERE po.parent_category = 'IT Professional Services' AND po.category = 'ITC-001-C: Software Development and Management' AND d.date.year IN [2023, 2024] RETURN d.date.year as Year, count(po) as Number_of_Orders, round(avg(po.fixed_cost), 2) as Average_Fixed_Cost, round(sum(po.po_amount), 2) as Total_Spend ORDER BY Year",

    },
    {   "question":"How many active contracts do I have with suppliers, and what is their total value?",
         "query":"MATCH (c:Contract) WHERE date(datetime(c.contract_end_date)) >= date() RETURN c.supplier_id AS supplier_id, c.supplier_name AS supplier_name, c.contract_id AS contract_id, c.contract_start_date AS contract_start_date, c.contract_end_date AS contract_end_date, c.contract_value AS contract_value ORDER BY c.contract_end_date DESC",

    },
    {   "question":"How many POs are tied to contracts that are ending this year?",
         "query":"MATCH (po:PurchaseOrder)-[:SUPPLIES]-(s:Supplier), (c:Contract) WHERE c.supplier_id = s.supplier_id AND datetime(c.contract_end_date).year = datetime().year RETURN c.contract_id, po.po_number, c.contract_start_date, c.contract_end_date ORDER BY c.contract_id, po.po_number",

    },
    {   "question":"which supplier offers the services in the Ground Freight category and how base rate changed over the time",
         "query":"MATCH (s:Supplier)-[r:OFFERS_TRANSPORT_SERVICES]->(po:PurchaseOrder) MATCH (po)-[:CREATED_ON]->(d:Date) RETURN DISTINCT s.supplier_name as SupplierName, COLLECT(DISTINCT {{liftgate_Service_rate: po.liftgate_service_rate, base_rate: po.base_rate_per_mile, year: substring(toString(d.date), 0, 4)}}) as ServiceRates ORDER BY SupplierName;",

    },
     {  "question":"What charges XPO Logistics implies in LTL service",
         "query":"MATCH (s:Supplier {{supplier_name: 'XPO Logistics'}}) OPTIONAL MATCH (s)-[:SUPPLIES|:OFFERS_TRANSPORT_SERVICES]->(po:PurchaseOrder) WITH s, COLLECT(DISTINCT {{service: po.service_name, liftgate_rate: po.liftgate_service_rate, base_rate: po.base_rate_per_mile, fuel_surcharge: po.fuel_surcharge, pickup_date: po.pickup_date, delivery_date: po.delivery_date, po_date: po.po_date}}) as po_services OPTIONAL MATCH (c:Catalog {{supplier_name: 'XPO Logistics'}}) WITH s, po_services, COLLECT(DISTINCT {{service: c.additional_services, liftgate_rate: c.liftgate_service_rate, base_rate: c.base_rate_per_mile, fuel_surcharge: c.fuel_surcharge, detention_rate: c.detention_rate_per_hour}}) as catalog_services UNWIND po_services as records WITH records WHERE records.po_date IS NOT NULL RETURN DISTINCT DATETIME(records.po_date).year as Year, records.base_rate as Base_Rate, records.liftgate_rate as Liftgate_Rate, records.fuel_surcharge as Fuel_Surcharge ORDER BY Year DESC",

    },
    {  "question":"what is the  detention_rate_per_hour for supplier XPO Logistics",
         "query":"MATCH (c:Catalog {{supplier_name: 'XPO Logistics'}}) RETURN c.supplier_name as Supplier, c.detention_rate_per_hour as DetentionRatePerHour;",

    },
    {  "question":"What is the detention rate per hour for XPO Logistics?",
         "query":"MATCH (c:Catalog {{supplier_name: 'XPO Logistics'}}) RETURN c.supplier_name as Supplier, c.detention_rate_per_hour as DetentionRatePerHour;",

    },
    {   "question":"What's the breakdown of software development spend by cost center?",
         "query":"MATCH (s:Supplier)-[:SUPPLIES]->(po:PurchaseOrder) WHERE po.category = 'ITC-001-C: Software Development and Management' RETURN po.cost_center, sum(po.po_amount) as total_spend, count(po) as number_of_projects, avg(po.po_amount) as avg_project_cost ORDER BY total_spend DESC",
 
    },
 
    {   "question":"How does the fixed cost compare to contract utilization across suppliers?",
         "query":"MATCH (s:Supplier)-[:SUPPLIES]->(po:PurchaseOrder) WHERE po.category = 'ITC-001-C: Software Development and Management' RETURN s.supplier_name, avg(po.fixed_cost) as avg_fixed_cost, sum(po.contract_utilised) as total_utilization, sum(po.contract_value) as total_contract_value ORDER BY avg_fixed_cost DESC",
 
    },
    {   "question":"What are the available products for desktop computers?",
         "query":"MATCH (c:Catalog) WHERE toLower(c.category) CONTAINS 'computer' OR toLower(c.parent_category) CONTAINS 'computer' OR toLower(c.product_name) CONTAINS 'desktop' RETURN c.product_name, c.product_id, c.category, c.parent_category, c.unit_price, c.currency, c.unit_of_measure, c.specification, c.additional_terms_and_conditions, c.service_name, c.equipment, c.fuel_surcharge, c.route, c.distance_miles, c.additional_services, c.liftgate_service_rate, c.dimensions, c.total_weight_lbs, c.pickup_date, c.ship_from, c.ship_from_address, c.ship_to, c.ship_to_address ORDER BY c.product_name",
 
    },
    {   "question":"which products are you offering in stainless steel category?",
         "query":"MATCH (c:Catalog) WHERE toLower(c.category) CONTAINS 'stainless steel' OR toLower(c.parent_category) CONTAINS 'stainless steel' RETURN DISTINCT c.product_name ORDER BY c.product_name",
 
    },
    {   "question":"list all the suppliers which are offering stainless steel products and what are their prices?",
         "query":"MATCH (s:Supplier)-[sup:SUPPLIES]->(po:PurchaseOrder) WHERE po.category = 'Stainless Steel' RETURN DISTINCT s.supplier_name as Supplier, po.product_name as ProductName, po.unit_price as UnitPrice ORDER BY s.supplier_name",
 
    },
    {   "question":"among all stainless steel category suppliers which suppliers are having contract?",
         "query":"MATCH (s:Supplier)-[:SUPPLIES]->(po:PurchaseOrder) WHERE po.category = 'Stainless Steel' OPTIONAL MATCH (s)-[:SUPPLIES]->(c:Contract) RETURN DISTINCT s.supplier_name as Supplier, CASE WHEN c IS NULL THEN 'No Contract Available' ELSE c.contract_id END as ContractStatus ORDER BY s.supplier_name",
 
    },
    {   "question":"Which supplier offer HP Elite 800 G6?",
         "query":"MATCH (s:Supplier)-[r:OFFERS_PRODUCT]->(po:PurchaseOrder) WHERE po.product_name CONTAINS 'HP Elite 800 G6' RETURN DISTINCT s.supplier_name as Supplier, s.supplier_id as SupplierID, po.product_name as Product, po.unit_price as UnitPrice, po.currency as Currency",
 
    },
    {   "question":"the suppliers for cloud migration catogery whats their price history?",
         "query":"MATCH (s:Supplier)-[r]->(po:PurchaseOrder) WHERE (po.category = 'Cloud Migration' OR po.parent_category = 'Cloud Migration') AND type(r) IN ['OFFERS_SERVICES', 'OFFERS_PRODUCT'] MATCH (po)-[:CREATED_ON]->(d:Date) RETURN s.supplier_name as Supplier, po.po_number as PurchaseOrder, CASE type(r) WHEN 'OFFERS_SERVICES' THEN po.service_name WHEN 'OFFERS_PRODUCT' THEN po.product_name END as ItemName, type(r) as OfferingType, po.category as Category, po.po_amount as Amount, po.currency as Currency, d.date as OrderDate ORDER BY d.date DESC",
 
    },
    {   "question":"for supplier Tech Mahindra whats their price history?",
         "query":"MATCH (s:Supplier)-[r]->(po:PurchaseOrder) WHERE s.supplier_name = 'Tech Mahindra' AND type(r) IN ['OFFERS_SERVICES', 'OFFERS_PRODUCT'] MATCH (po)-[:CREATED_ON]->(d:Date) RETURN po.po_number as PurchaseOrder, CASE type(r) WHEN 'OFFERS_SERVICES' THEN po.service_name WHEN 'OFFERS_PRODUCT' THEN po.product_name END as ItemName, type(r) as OfferingType, po.category as Category, po.po_amount as Amount, po.currency as Currency, d.date as OrderDate ORDER BY d.date DESC",
 
    },
    {   "question":"how much time they took to complete a Ground Freight?",
         "query":"MATCH (po:PurchaseOrder) WHERE po.category = 'Ground Freight' WITH po, CASE WHEN po.service_start_date IS NOT NULL AND po.service_end_date IS NOT NULL THEN duration.between(po.service_start_date, po.service_end_date).days WHEN po.pickup_date IS NOT NULL AND po.delivery_date IS NOT NULL THEN duration.between(po.pickup_date, po.delivery_date).days WHEN po.delivery_date IS NOT NULL AND po.actual_receipt_date IS NOT NULL THEN duration.between(po.delivery_date, po.actual_receipt_date).days END as days_taken RETURN po.po_number, po.supplier_name, CASE WHEN po.service_name IS NOT NULL THEN po.service_name WHEN po.shipping_method IS NOT NULL THEN po.shipping_method ELSE po.product_name END as item_name, CASE WHEN po.service_start_date IS NOT NULL THEN po.service_start_date WHEN po.pickup_date IS NOT NULL THEN po.pickup_date ELSE po.delivery_date END as start_date, CASE WHEN po.service_end_date IS NOT NULL THEN po.service_end_date WHEN po.delivery_date IS NOT NULL AND po.pickup_date IS NOT NULL THEN po.delivery_date ELSE po.actual_receipt_date END as end_date, days_taken ORDER BY days_taken DESC;",
 
    },
     {   "question":"How long did Wipro take to complete their cloud migration projects?",
         "query":"MATCH (po:PurchaseOrder) WHERE po.category = 'Cloud Migration' AND po.supplier_name = 'Wipro' RETURN po.po_number, po.supplier_name, po.service_name, po.service_start_date, po.service_end_date, duration.between(po.service_start_date, po.service_end_date).days as days_taken ORDER BY days_taken DESC",
 
    },
    {   "question":"suggest me a buyer or requester who have taken their service in  cloud migration",
         "query":"MATCH (po:PurchaseOrder) WHERE po.category = 'Cloud Migration' RETURN DISTINCT po.requester ORDER BY po.requester LIMIT 5",
 
    },
    {   "question":"the suppliers for cloud migration catogery are they competitive",
         "query":"MATCH (s:Supplier)-[r:PROVIDES_CATEGORY]->(po:PurchaseOrder) WHERE r.category = 'Cloud Migration' WITH s, count(po) as number_of_orders, avg(po.po_amount) as avg_order_value, s.financial_score as financial_score, s.sustainability_score as sustainability_score RETURN s.supplier_name as Supplier, financial_score as Financial_Score, sustainability_score as Sustainability_Score, number_of_orders as Number_of_Orders, round(avg_order_value, 2) as Average_Order_Value ORDER BY financial_score DESC;",
 
    },
    {   "question":"What is the price history of Network Services across all suppliers over the last year?",
         "query":"MATCH (po:PurchaseOrder)-[:CREATED_ON]->(d:Date) WHERE po.service_name = 'Network Services' AND d.date >= date() - duration('P1Y') RETURN d.date as order_date, po.fixed_cost as service_cost, po.supplier_name ORDER BY order_date DESC",
 
    },
    {   "question":"Do we have contract with Tech Mahindra?",
         "query":"MATCH (c:Contract) WHERE c.supplier_name = 'Tech Mahindra' RETURN c.contract_id, c.contract_start_date, c.contract_end_date, c.contract_value, c.contract_term, c.category, c.description, c.supplier_name;",
 
    },
    {   "question":"how many suppliers have contracts in cloud migration category and what are contract details",
         "query":"MATCH (c:Contract) WHERE c.category = 'Cloud Migration' RETURN c.supplier_name AS SupplierName, c.contract_id AS ContractID, c.contract_value as ContractValue,  c.contract_term AS ContractTerm ORDER BY  ContractTerm DESC;",
 
    },
    {   "question":"which suppliers offers product 410 Stainless Round Bar 1",
         "query":"MATCH (s:Supplier)-[r:SUPPLIES]->(po:PurchaseOrder) WHERE po.product_name CONTAINS '410 Stainless Round Bar 1' WITH DISTINCT s, COUNT(po) as order_count, COLLECT(DISTINCT {{ po_number: po.po_number, quantity: po.quantity, unit_price: po.unit_price, order_date: po.po_date }}) as order_details RETURN 'Active Supplier' as status, s.supplier_name as supplier_name, s.supplier_id as supplier_id, s.country as country, s.contact_number as contact, s.email as email, s.financial_score as financial_score, s.sustainability_score as sustainability_score, order_count as total_orders, order_details as purchase_details UNION MATCH (s:Supplier)-[:OFFERS_PRODUCT]->(c:Catalog) WHERE c.product_name CONTAINS '410 Stainless Round Bar 1' AND NOT EXISTS {{ MATCH (s)-[:SUPPLIES]->(:PurchaseOrder {{product_name: '410 Stainless Round Bar 1'}}) }} RETURN 'Catalog Only' as status, s.supplier_name as supplier_name, s.supplier_id as supplier_id, s.country as country, s.contact_number as contact, s.email as email, s.financial_score as financial_score, s.sustainability_score as sustainability_score, 0 as total_orders;",
 
    },
    {   "question":"which po's are due in next 3 weeks for 410 Stainless Round Bar 1 product",
         "query":"MATCH (po:PurchaseOrder) WHERE po.product_name CONTAINS '410 Stainless Round Bar 1' AND po.delivery_date >= datetime() AND po.delivery_date <= datetime() + duration('P21D') RETURN po.po_number, po.supplier_name, po.quantity, po.unit_price, po.po_amount, po.delivery_date ORDER BY po.delivery_date",
 
    },
    {   "question":"Is there any delayed request for this 316 Stainless Square Bar product",
         "query":"MATCH (e:Email) WHERE e.subject CONTAINS 'PO Change Approval Request' AND e.mailBody CONTAINS 'PO Change Approval Request' AND e.originalDeliveryDate IS NOT NULL AND e.requestedDeliveryDate IS NOT NULL WITH e MATCH (po:PurchaseOrder) WHERE po.product_name CONTAINS '316 Stainless Square Bar 1' AND po.po_number = e.poNumber RETURN DISTINCT e.poNumber as PO_Number, e.originalDeliveryDate as Original_Delivery_Date, e.requestedDeliveryDate as Requested_Delivery_Date, e.sender as Sender, e.recipient as Recipient, e.sentDate as Email_Sent_Date, po.product_name as Product_Name;",
 
    },
    {   "question":"Is there any potential low stock alert for product 316 Stainless Square Bar",
         "query":"MATCH (e:Email) RETURN e.mailBody as message;",
 
    },
    ]

print(examples)
