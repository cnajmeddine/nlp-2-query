SELECT d.department_name, SUM(s.amount) AS total_sales
FROM sales s
JOIN departments d ON s.department_id = d.department_id
GROUP BY d.department_name;