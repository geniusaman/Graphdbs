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
        "question": "Which suppliers are offering the best payment terms (e.g., early payment discounts)?",
        "query": "MATCH (s:Supplier)-[:ISSUED_TO]-(po:PurchaseOrder) WHERE po.paymentTerms CONTAINS 'discount' RETURN DISTINCT s.supplierName AS supplier, po.paymentTerms AS paymentTerms ORDER BY po.paymentTerms",
    },
    {
        "question": "What percentage of POs were issued to suppliers based in the US?",
        "query": "MATCH (po:PurchaseOrder) WITH count(po) AS totalPOs MATCH (po:PurchaseOrder)-[:ISSUED_TO]->(s:Supplier) WHERE s.country = 'US' WITH totalPOs, count(po) AS usPOs RETURN usPOs AS POsIssuedToUSSuppliers, totalPOs AS TotalPOs, round((toFloat(usPOs) / totalPOs) * 100, 2) AS PercentageOfPOsToUSSuppliers",
    },
    {
        "question": "How many POs are tied to contracts that are ending this year?",
        "query": "WITH datetime().year AS currentYear MATCH (po:PurchaseOrder)-[:ISSUED_TO]->(s:Supplier)-[:UNDER_CONTRACT]->(c:Contract) WHERE toInteger(split(c.contractEndDate, '/')[2]) = currentYear RETURN count(DISTINCT po) AS NumberOfPOs, currentYear AS Year",
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
        "query": "MATCH (pc:ParentCategory)-[:SPEND_PARENT_CATEGORY]->(po:PurchaseOrder)WITH pc, sum(po.poAmount) AS totalSpendRETURN pc.parentCategoryName AS ParentCategory,       totalSpend,       'USD' AS CurrencyORDER BY totalSpend DESCLIMIT 1",
    },
    {
        "question": "Which parent category has the highest total spend?",
        "query": "MATCH (pc:ParentCategory)-[:SPEND_PARENT_CATEGORY]->(po:PurchaseOrder) WITH pc, sum(po.poAmount) AS totalSpend RETURN pc.parentCategoryName AS ParentCategory, totalSpend, 'USD' AS Currency ORDER BY totalSpend DESC LIMIT 1",
    },
    {
        "question": "How many suppliers are associated with each parent category?",
        "query": "MATCH (pc:ParentCategory)<-[:BELONGS_TO_PARENT_CATEGORY]-(:Category)<-[:BELONGS_TO_CATEGORY]-(:Service)<-[:PROVIDES_SERVICE]-(s:Supplier) WITH pc, count(DISTINCT s) AS supplierCount RETURN pc.parentCategoryName AS ParentCategory, supplierCount ORDER BY supplierCount DESC",
    },


    
  
    
]

print(examples)