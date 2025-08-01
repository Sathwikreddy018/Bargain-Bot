library(DBI)
library(RMariaDB)

con <- dbConnect(RMariaDB::MariaDB(),
                 user = "BargainBot",
                 password = "%BargainBot",
                 dbname = "manuel projekt v4",
                 host = "localhost")

data <- dbGetQuery(con, "
  SELECT s.name AS store, sp.price AS price
  FROM store_product sp
  JOIN store s ON sp.storestore_id = s.store_id
")

dbDisconnect(con)

boxplot(price ~ store, data = data,
        col = "cadetblue",
        main = "Price Distribution per Store",
        xlab = "Store",
        ylab = "Price (CHF)",
        las = 1)
