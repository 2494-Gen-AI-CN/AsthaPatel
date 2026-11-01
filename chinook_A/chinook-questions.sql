-- Active: 1793321564026@@127.0.0.1@3306@Chinook
-- Active: 1793321564026@@127.0.0.1@3306@Chinook
-- Chinook query activity (week 3, Thursday). Write one query under each question.
-- How to run this file, what the tables are and what each question expects is in
-- README.md beside it. Test each query at the mysql> prompt first, then paste it here.
-- Hand-in: week-03/hackathon/chinook/chinook-questions.sql in your own learner repo.

USE Chinook;


-- ============================================================
-- Part A: one table (SELECT, WHERE, ORDER BY, LIMIT)
-- ============================================================

-- Q01. Every genre name, A to Z.
SELECT name
FROM Genre
ORDER BY name ASC;

-- Q02. The customers who live in Canada: first name, last name and city, sorted by city.
SELECT FirstName, LastName, City
FROM Customer
WHERE Country = 'Canada'
ORDER BY City ASC;

-- Q03. The ten longest tracks that run over 10 minutes: name and length in minutes
--      (one decimal), longest first.
SELECT Name, ROUND(Milliseconds/600000.0, 1) AS Length
FROM Track 
WHERE Milliseconds > 600000
ORDER BY Milliseconds DESC 
LIMIT 10;  

-- Q04. Invoices from 2025 whose total is above 10: invoice id, date and total, highest total first.
SELECT InvoiceId, InvoiceDate, Total
FROM Invoice 
WHERE InvoiceDate >= '2025-01-01' AND Total >= 10
ORDER BY Total DESC;

-- Q05. Albums whose title contains the word Live, A to Z.
SELECT Title
FROM Album
WHERE Title LIKE '%Live%'
ORDER BY Title ASC;

-- Q06. Customers in the USA or Canada who gave a company name: the full name in one
--      column called customer, the company and the country, sorted by company.
SELECT CONCAT(FirstName, ' ', LastName) AS customer, Company, Country
FROM Customer 
WHERE Country IN ('USA', 'Canada') 
        AND Company IS NOT NULL
ORDER BY Company ASC; 

-- ============================================================
-- Part B: aggregates (GROUP BY, HAVING)
-- ============================================================

-- Q07. One row about the whole Track table: how many tracks, and the shortest, longest
--      and average length in minutes (two decimals).
SELECT COUNT(TrackId), 
        ROUND(MIN(Milliseconds)/600000.0, 2) AS shortest, 
        ROUND(MAX(Milliseconds)/600000.0, 2) AS longest, 
        ROUND(AVG(Milliseconds)/600000.0, 2) AS average
FROM Track;

-- Q08. How many customers live in each country, most customers first, then country A to Z.
SELECT Country, COUNT(CustomerId) AS customerCount
FROM Customer 
GROUP BY Country
ORDER BY customerCount DESC, Country ASC;

-- Q09. Total billed per billing country (two decimals), only the countries billed more
--      than 100 in all, highest first.
SELECT BillingCountry, ROUND(SUM(Total),2) AS TotalBilled
FROM Invoice
GROUP BY BillingCountry
HAVING TotalBilled > 100
ORDER BY TotalBilled DESC;

-- Q10. Albums with more than 25 tracks: the album id and its track count, most tracks first.
--      (Only the id for now. Q13 adds the title.)
SELECT AlbumId, COUNT(TrackId) AS TrackCount
FROM Track
GROUP BY AlbumId 
HAVING TrackCount > 25
ORDER BY TrackCount DESC;

-- Q11. Per customer id: how many invoices and how much they spent in all (two decimals),
--      only the customers who spent more than 45, biggest spender first.

SELECT CustomerId, COUNT(InvoiceId) AS InvoiceCount, ROUND(SUM(Total), 2) AS InvoiceSum
FROM Invoice 
GROUP BY CustomerId
HAVING InvoiceSum > 45
ORDER BY InvoiceSum DESC;

DELIMITER //
CREATE PROCEDURE get_title(IN Title VARCHAR(200))
BEGIN
        SELECT Title
        FROM Album
        WHERE Title LIKE '%Live%'
        ORDER BY Title ASC;
END //
DELIMITER ;

CALL get_title('Show Me How to Live');

-- ============================================================
-- Part C: joins
-- ============================================================

-- Q12. Every album title with the name of its artist, sorted by artist then title.
SELECT ar.Name , al.Title
FROM Album AS al
INNER JOIN Artist AS ar ON al.ArtistId = ar.ArtistId
ORDER BY ar.ArtistId ASC, al.Title ASC;

-- Q13. Q10 again, with the album title and the artist name instead of the id.
-- Q10. Albums with more than 25 tracks: 
--      the album title and the artist name and its track count, most tracks first.
SELECT al.Title, ar.Name, COUNT(t.TrackId) AS TrackCount
FROM Album AS al 
INNER JOIN Artist AS ar ON al.ArtistId = ar.ArtistId 
INNER JOIN Track AS t ON al.AlbumId = t.AlbumId
GROUP BY al.AlbumId
HAVING TrackCount > 25 -- cannot use WHERE since COUNT(t.TrackId) > 25 is not valid for this clause
ORDER BY TrackCount DESC;

-- Q14. Every track by Iron Maiden: album title and track name, sorted by album then track.
SELECT al.Title, t.Name
FROM Album AS al 
INNER JOIN Track as t ON al.AlbumId = t.AlbumId 
WHERE al.ArtistId = (SELECT ar.ArtistId 
                        FROM Artist AS ar 
                        WHERE ar.Name = 'Iron Maiden' )
ORDER BY al.Title ASC, t.Name ASC;

-- Q15. Every Jazz track: track name, album title and media type name, sorted by album then track.
SELECT al.Title AS 'Album name', 
        t.Name AS 'Track name', 
        m.Name AS 'Media Type'
FROM Track AS t
INNER JOIN Album AS al ON t.AlbumId = al.AlbumId 
INNER JOIN MediaType AS m ON t.MediaTypeId = m.MediaTypeId 
WHERE t.GenreId = (SELECT g.GenreId 
                  FROM Genre AS g 
                  WHERE g.Name = 'Jazz')
ORDER BY al.Title ASC, t.Name ASC;


-- Q16. Each customer with the employee who supports them: customer full name and rep full
--      name (one column each), sorted by rep then customer.
SELECT CONCAT(e.FirstName, ' ', e.LastName) AS 'Rep Full Name',
        CONCAT(c.FirstName,' ', c.LastName) AS 'Customer Full Name'
FROM Customer AS c 
INNER JOIN Employee AS e ON e.EmployeeId = c.SupportRepId
ORDER BY 'Rep Full Name' ASC, 'Customer Full Name' ASC;

-- Q17. Every employee and how many customers they support, including the employees who
--      support nobody (they show 0), most customers first, then last name.
SELECT COUNT(c.SupportRepId) AS Supported, e.LastName, e.FirstName
FROM Employee AS e 
LEFT JOIN Customer AS c ON e.EmployeeId = c.SupportRepId
GROUP BY e.EmployeeId
ORDER BY Supported DESC, e.LastName ASC; 


-- Q18. The five genres that earned the most: genre name and revenue (the sum of unit price
--      times quantity over every invoice line, two decimals), highest first.
SELECT g.Name, ROUND(SUM(i.UnitPrice*i.Quantity),2) AS Revenue
FROM Genre AS g 
LEFT JOIN Track AS t ON g.GenreId = t.GenreId
INNER JOIN InvoiceLine AS i ON i.TrackId = t.TrackId
GROUP BY g.GenreId
ORDER BY Revenue DESC
LIMIT 5;


-- Q19. How many tracks have never been sold? One number, found with a LEFT JOIN
--      from Track to InvoiceLine and a test for NULL.
SELECT COUNT(t.TrackId) AS 'Total sold tracks'
FROM Track AS t 
LEFT JOIN InvoiceLine AS i ON i.TrackId = t.TrackId 
GROUP BY t.TrackId 
HAVING ;

-- ============================================================
-- Part D: subqueries
-- ============================================================

-- Q20. Every track on the album called Let There Be Rock: name and length in milliseconds,
--      in track order (by TrackId). Use a subquery for the album id, not a join.
SELECT t.Name, t.Milliseconds
FROM  Track AS t
WHERE t.AlbumId = ALL(SELECT a.AlbumId
                        FROM Album AS a
                        WHERE a.Title = 'Let There Be Rock');
-- OR JOIN
SELECT t.Name, t.Milliseconds
FROM Track AS t 
INNER JOIN Album AS a ON a.AlbumId = t.AlbumId 
WHERE a.Title = 'Let There Be Rock';


-- Q21. Tracks that cost more than the average track price: name and unit price,
--      the first ten alphabetically.
SELECT t.Name, t.UnitPrice
FROM Track AS t
WHERE t.UnitPrice > (SELECT AVG(i.UnitPrice)
                        FROM InvoiceLine AS i)
ORDER BY t.Name ASC
LIMIT 10;

-- Q22. Artists with no album at all, A to Z. Write it with NOT IN and a subquery.
SELECT ar.Name
FROM Artist AS ar 
WHERE ar.ArtistId NOT IN(SELECT al.ArtistId
                                FROM Album AS al
                                WHERE al.ArtistId IS NOT NULL) -- prevent NULL trap
ORDER BY ar.Name ASC;

-- Q22b. Same question, written as a LEFT JOIN. Same rows?
SELECT ar.Name 
FROM Artist AS ar 
LEFT JOIN Album AS al ON al.ArtistId = ar.ArtistId 
WHERE al.ArtistId IS NULL --The artist id in album will be null sicne they dont have an album
ORDER BY ar.Name ASC;


-- Q23. The invoice with the highest total: invoice id, customer id, date and total.
SELECT i.InvoiceId, i.CustomerId, i.InvoiceDate, i.Total
FROM Invoice AS i 
WHERE i.Total = (SELECT MAX(Total)
                        FROM Invoice);

-- Q24. Customers who bought at least one Metal track: full name and country, sorted by
--      name. The list of customer ids comes from a subquery that joins Invoice,
--      InvoiceLine, Track and Genre.
SELECT CONCAT(c.FirstName, ' ', c.LastName) AS 'Full Name', c.Country
FROM Customer AS c 
WHERE  

-- ============================================================
-- Stretch (for home, or if you finish early)
-- ============================================================

-- Q25. Each employee with the name of the person they report to. The general manager
--      reports to nobody and must still appear, with NULL. Hint: join Employee to
--      itself under two aliases.


-- Q26. Customers whose total spend is above the average customer's total spend: full name
--      and what they spent (two decimals), biggest first. The average of the per-customer
--      totals needs a subquery in FROM (the notes page calls it a derived table).

