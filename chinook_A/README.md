# Week 3: querying the Chinook music store

Thursday afternoon of week 3, in the project slot. Nothing here is marked. You work alone or in pairs, at your own pace, against a database you have never seen: the same moves the morning made on the ticket desk, on a bigger data set.

Chinook is a sample database of a digital music store: artists, albums, tracks, the customers who bought them, their invoices and the employees who support them. It is published by Luis Rocha under the MIT license (`Chinook-LICENSE.md`), and `Chinook_MySql.sql` here is version 1.4.5 of its MySQL script, unchanged.

## 1. Load the database (2 minutes)

Your `desk-mysql` container from Monday must be running (`docker ps`; `docker start desk-mysql` if it is not). From a terminal in your copy of this repository:

```
docker exec -i desk-mysql mysql -uroot -pdesk < activities/week-03-chinook/Chinook_MySql.sql
```

`desk` is the root password from Monday's `docker run` line; type yours if you chose another. The script creates a database called `Chinook` with eleven tables and about 15,000 rows. It drops and recreates `Chinook` each time it runs, so you can reload a clean copy whenever you want. It never touches `ticket_desk`.

Then open the client inside that database:

```
docker exec -it desk-mysql mysql -uroot -pdesk Chinook
```

(`winpty` in front if Git Bash says it has no TTY, as on Monday.) At the prompt, look around the way Tuesday did: `SHOW TABLES;` and `DESCRIBE Track;`.

## 2. The tables

Eleven tables. The names are in PascalCase, and every id column is the table name plus `Id`: `Artist.ArtistId`, `Album.AlbumId`, and `Album.ArtistId` is the foreign key to `Artist`. Two things to know before you type:

- Table names are case sensitive on this server, because MySQL in the Linux container keeps the case of its table files. `SELECT * FROM Album` works; `SELECT * FROM album` is `ERROR 1146: Table 'Chinook.album' doesn't exist`. Column names are not case sensitive.
- Strings go in single quotes: `WHERE Country = 'Canada'`.

| Table | What a row is | Links to |
|---|---|---|
| `Artist` | one artist (275) | |
| `Album` | one album (347) | `Artist` through `ArtistId` |
| `Track` | one track (3,503): name, length in `Milliseconds`, `UnitPrice`, `Composer` (often NULL) | `Album`, `Genre`, `MediaType` |
| `Genre` | one genre (25): Rock, Jazz, Metal... | |
| `MediaType` | one file format (5) | |
| `Playlist` | one playlist (18) | |
| `PlaylistTrack` | one track on one playlist (8,715); its key is both ids | `Playlist`, `Track` |
| `Customer` | one customer (59): name, `Company` (often NULL), `Country`, `SupportRepId` | `Employee` through `SupportRepId` |
| `Employee` | one employee (8): name, `Title`, `ReportsTo` (the manager's `EmployeeId`, NULL for the general manager) | `Employee` |
| `Invoice` | one purchase (412): `CustomerId`, `InvoiceDate` (2021 to 2025), `BillingCountry`, `Total` | `Customer` |
| `InvoiceLine` | one track on one invoice (2,240): `UnitPrice`, `Quantity` | `Invoice`, `Track` |

Read it as three chains. Music: `Artist` 1 to many `Album` 1 to many `Track`, with `Genre` and `MediaType` hanging off `Track`. Sales: `Customer` 1 to many `Invoice` 1 to many `InvoiceLine`, each line naming one `Track`. People: an `Employee` supports many customers, and reports to one employee.

## 3. The questions

`chinook-questions.sql` holds 26 questions as comments, in four parts plus a stretch, each part one idea from this morning's walkthrough:

- **Part A, one table (Q01 to Q06):** SELECT, WHERE with `=`, `>`, `IN`, `BETWEEN`, `LIKE`, `IS NOT NULL`, ORDER BY, LIMIT, `ROUND` and `CONCAT` with an alias.
- **Part B, aggregates (Q07 to Q11):** `COUNT`, `MIN`, `MAX`, `AVG`, `SUM`, GROUP BY, HAVING.
- **Part C, joins (Q12 to Q19):** inner joins over two, three and four tables, a LEFT JOIN that keeps the rows with nothing on the other side, a join feeding GROUP BY.
- **Part D, subqueries (Q20 to Q24):** a subquery that hands back one value, `IN` and `NOT IN` against a list, the same question as a subquery and as a LEFT JOIN, a subquery with joins inside it.
- **Stretch (Q25, Q26):** a table joined to itself, and a subquery in FROM. Both are on tonight's notes page ("Subquery or join?", "Derived tables and WITH"). For home, or if you finish early.

Work in order. Everyone should get through Part C in the slot; nobody is expected to finish all 26. Write each query at the `mysql>` prompt until it gives the rows below, then paste it under its question in the file.

Expected row counts, so you know when you are there:

| Q | Rows | Q | Rows | Q | Rows |
|---|---|---|---|---|---|
| Q01 | 25 | Q10 | 4 | Q19 | 1 (the number is 1519) |
| Q02 | 8 | Q11 | 5 | Q20 | 8 |
| Q03 | 10 | Q12 | 347 | Q21 | 10 |
| Q04 | 12 | Q13 | 4 | Q22 | 71 |
| Q05 | 17 | Q14 | 213 | Q22b | 71 (the same 71) |
| Q06 | 5 | Q15 | 130 | Q23 | 1 |
| Q07 | 1 | Q16 | 59 | Q24 | 55 |
| Q08 | 24 | Q17 | 8 | Q25 | 8 |
| Q09 | 6 | Q18 | 5 | Q26 | 22 |

A few checks beyond the count: Q07's longest track is 88.12 minutes; Q09 starts with USA at 523.06; Q13's first row is Greatest Hits by Lenny Kravitz with 57 tracks; Q17 shows three sales support agents with customers and five employees with 0; Q18's top genre is Rock at 826.65; Q23 is invoice 404 at 25.86.

## 4. Running the whole file

Once the queries are in the file, run it the way this morning ran `reports.sql`:

```
docker exec -i desk-mysql mysql -uroot -pdesk -t -v < chinook-questions.sql
```

`-t` draws every result as a table and `-v` prints each query above its result, so you can read the file's output top to bottom. The client stops at the first error, so test each query at the prompt before it goes in the file.

## 5. Things that will bite

- `ERROR 1046: No database selected`: the file starts with `USE Chinook;`, and the prompt needs `USE Chinook;` once, or the database name on the `docker exec` line as above.
- `ERROR 1146: Table 'Chinook.album' doesn't exist`: the case of the table name (section 2).
- `ERROR 1055 ... this is incompatible with sql_mode=only_full_group_by`: a column in SELECT that is neither in GROUP BY nor inside an aggregate. Add it to GROUP BY.
- `ERROR 1111: Invalid use of group function`: an aggregate in WHERE. Move the test to HAVING.
- A LEFT JOIN that lost its NULL rows: the test on the right-hand table is in WHERE. It belongs in ON, or the test must be `IS NULL`.
- `COUNT(*)` gives 1 for an employee with no customers after a LEFT JOIN. `COUNT(c.CustomerId)` gives 0, because COUNT skips NULLs.
- `Company <> NULL` gives no rows at all. Nothing equals NULL. Use `IS NOT NULL`.
- A LIMIT without an ORDER BY gives ten rows in no promised order.

## 6. Hand-in

Copy `chinook-questions.sql` into your own `2494-Gen-AI-CN/<FirstnameLastname>` repository as `week-03/hackathon/chinook/chinook-questions.sql`, fill it in there, commit and push to `main` before you leave. Finish what is left at home before Friday. Keep the questions as comments above the queries, so the file reads as question, answer, question, answer.
