examples = [
    {
        "question": "What is the total spend for API Development and Integration?",
        "query": "MATCH (buyer:Buyer)-[:PLACED_BY]->(po:PurchaseOrder)-[:INCLUDES_SERVICE]->(service:Service) WHERE service.serviceName = 'API Development and Integration' RETURN SUM(po.poAmount) AS totalSpend",
    },
    {
        "question": "What is the total cost for all suppliers?",
        "query": "MATCH (s:Supplier)-[:PROVIDES_SERVICE]->(:Service)<-[:INCLUDES_SERVICE]-(po:PurchaseOrder) WITH s, SUM(po.poAmount) AS totalCost RETURN s.supplierName AS SupplierName, s.supplierID AS SupplierID, totalCost ORDER BY totalCost DESC",
    },
    {
        "question": "Who are the top 5 suppliers with the highest supplier rating and their corresponding financial scores?",
        "query": "MATCH (s:Supplier) WITH s, (s.sustainabilityRating + s.financialHealthScore) AS combinedScore ORDER BY combinedScore DESC LIMIT 5 RETURN s.supplierName AS supplierName, s.sustainabilityRating AS supplierRating, s.financialHealthScore AS financialHealthScore",
    },
    {
        "question": "which suppliers have the highest financial score for software development and management?",
        "query": "MATCH (s:Supplier)-[:PROVIDES_CATEGORY]->(c:Category {{categoryName: 'Software Development and Management'}}) RETURN s.supplierName AS SupplierName, s.financialHealthScore AS FinancialScore ORDER BY s.financialHealthScore DESC LIMIT 5",
    },
    {
        "question": "Which suppliers are offering the best payment terms (e.g., early payment discounts)?",
        "query": "MATCH (s:Supplier)-[:ISSUED_TO]-(po:PurchaseOrder) WHERE po.paymentTerms CONTAINS 'discount' RETURN DISTINCT s.supplierName AS supplier, po.paymentTerms AS paymentTerms ORDER BY po.paymentTerms",
    },
    {
        "question": "What percentage of POs were issued to suppliers based in the US?",
        "query": "MATCH (po:PurchaseOrder) WITH count(po) AS totalPOs MATCH (po:PurchaseOrder)-[:ISSUED_TO]->(s:Supplier) WHERE s.country = 'US' WITH totalPOs, count(po) AS usPOs RETURN usPOs AS POsIssuedToUSSuppliers, totalPOs AS TotalPOs, round((toFloat(usPOs) / totalPOs) * 100, 2) AS PercentageOfPOsToUSSuppliers",
    },
    {
        "question": "How has my total procurement spend changed over the last 3 years?",
        "query": "MATCH (po:PurchaseOrder) WITH po, datetime(po.poDate).year AS year WITH year, sum(po.poAmount) AS yearlySpend WITH collect({{year: year, spend: yearlySpend}}) AS yearlyData UNWIND range(0, size(yearlyData) - 2) AS i WITH yearlyData[i] AS currentYear, yearlyData[i+1] AS previousYear WHERE currentYear.year > previousYear.year RETURN currentYear.year AS year, currentYear.spend AS totalSpend, currentYear.spend - previousYear.spend AS yearOverYearChange ORDER BY year DESC years",
    },
    {
        "question": "How many POs are tied to contracts that are ending this year?",
        "query": "WITH datetime().year AS currentYear MATCH (po:PurchaseOrder)-[:ISSUED_TO]->(s:Supplier)-[:UNDER_CONTRACT]->(c:Contract) WHERE toInteger(split(c.contractEndDate, '/')[2]) = currentYear RETURN count(DISTINCT po) AS NumberOfPOs, currentYear AS Year",
    },
    {
        "question": "who is the cheapest supplier in cloud migration category?",
        "query": "MATCH (c:Category {{categoryName: 'Cloud Migration'}})<-[:BELONGS_TO_CATEGORY]-(s:Service)<-[:PROVIDES_SERVICE]-(sup:Supplier) MATCH (po:PurchaseOrder)-[:INCLUDES_SERVICE]->(s) RETURN sup.supplierName AS supplier, MIN(po.poAmount) AS cheapestPOAmount ORDER BY cheapestPOAmount ASC LIMIT 1",
    },
    {
        "question": "How many active contracts do I have with suppliers, and what is their total value?",
        "query": "MATCH (s:Supplier)-[:UNDER_CONTRACT]->(c:Contract) WHERE apoc.date.parse(c.contractEndDate, 'ms', 'M/d/yyyy') > timestamp() WITH s, c, apoc.date.parse(c.contractEndDate, 'ms', 'MM/dd/yyyy') AS contractEndDateParsed RETURN DISTINCT s.supplierName AS SupplierName, c.contractID AS ContractID, c.contractEndDate AS ContractEndDate, c.contractValue AS ContractValue",
    },
    {
        "question": "what is the department wise total spend?",
        "query": "MATCH (d:Department)-[:SPEND_BY_DEPARTMENT]->(po:PurchaseOrder) WITH d.name AS departmentName, collect(po) AS purchaseOrders UNWIND purchaseOrders AS po WITH departmentName, sum(po.poAmount) AS totalSpend RETURN departmentName, totalSpend, 'USD' AS currencyCode ORDER BY totalSpend DESC",
    },
    
    {
        "question": "Which parent category has the highest total spend?",
        "query": "MATCH (pc:ParentCategory)-[:SPEND_PARENT_CATEGORY]->(po:PurchaseOrder) WITH pc, sum(po.poAmount) AS totalSpend RETURN pc.parentCategoryName AS ParentCategory, totalSpend, 'USD' AS Currency ORDER BY totalSpend DESC LIMIT 1",
    },
    {
        "question": "How many suppliers are associated with each parent category?",
        "query": "MATCH (pc:ParentCategory)<-[:BELONGS_TO_PARENT_CATEGORY]-(:Category)<-[:BELONGS_TO_CATEGORY]-(:Service)<-[:PROVIDES_SERVICE]-(s:Supplier) WITH pc, count(DISTINCT s) AS supplierCount RETURN pc.parentCategoryName AS ParentCategory, supplierCount ORDER BY supplierCount DESC",
    },
    {
        "question": "the average annual growth rate, the highest/lowest spend year",
        "query": "MATCH (po:PurchaseOrder) WITH datetime(po.poDate).year as year, sum(po.poAmount) as yearly_spend WITH year, yearly_spend ORDER BY year WITH collect({{year: year, spend: yearly_spend}}) as years_data WITH years_data, reduce(s = {{year: 0, spend: 0}}, x in years_data | CASE WHEN x.spend > s.spend THEN x ELSE s END) as highest_spend, reduce(s = {{year: 0, spend: toInteger(9999999999)}}, x in years_data | CASE WHEN x.spend < s.spend THEN x ELSE s END) as lowest_spend UNWIND range(0, size(years_data)-2) as i WITH years_data, i, highest_spend, lowest_spend WITH years_data, highest_spend, lowest_spend, ((years_data[i+1].spend - years_data[i].spend) * 100.0 / years_data[i].spend) as growth_rate WITH highest_spend, lowest_spend, avg(growth_rate) as avg_growth_rate RETURN round(avg_growth_rate * 100) / 100 as average_annual_growth_rate, highest_spend.year as highest_spend_year, highest_spend.spend as highest_spend_amount, lowest_spend.year as lowest_spend_year, lowest_spend.spend as lowest_spend_amount",
    },
    {
        "question": "how many catogeries are there and which suppliers offers products and services in what categories",
        "query":"MATCH (c:Catalog) WITH c.supplier_name as supplier, c.category as category, c.parent_category as parent_category WHERE category IS NOT NULL WITH supplier, category, parent_category, COUNT(*) as offering_count WITH COUNT(DISTINCT category) as total_categories, COUNT(DISTINCT parent_category) as total_parent_categories, COLLECT(DISTINCT {{supplier: supplier, category: category, parent_category: parent_category, offering_count: offering_count}}) as supplier_category_details RETURN total_categories, total_parent_categories, supplier_category_details ORDER BY SIZE(supplier_category_details) DESC",

    }


    
  
    
]

print(examples)