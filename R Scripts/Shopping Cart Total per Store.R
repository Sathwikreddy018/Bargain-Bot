library(DBI)
library(RMariaDB)

con <- dbConnect(RMariaDB::MariaDB(),
                 user = "BargainBot",
                 password = "%BargainBot",
                 dbname = "manuel projekt v4",
                 host = "localhost")

cart <- dbGetQuery(con, "
  SELECT 
    s.name AS store,
    p.productname,
    sp.price
  FROM store_product sp
  JOIN store s ON sp.storestore_id = s.store_id
  JOIN product p ON sp.productproduct_id = p.product_id
")

dbDisconnect(con)

total_prices <- aggregate(price ~ store, data = cart, sum)
total_prices <- total_prices[order(total_prices$price), ]

bars <- barplot(total_prices$price,
                names.arg = total_prices$store,
                col = "darkorange",
                main = "Price Comparison: Total Shopping List per Store",
                ylab = "Total Cost in CHF",
                las = 1)
